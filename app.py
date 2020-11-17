import connexion, logging, database
from database import db, Notification
from flask import jsonify
import datetime
from dateutil import parser

def get_notifications(**kwargs):
    """ Returns notifications matching parameters """
    q = db.session.query(Notification)

    if 'read' in kwargs:
        if kwargs['read']:
            q = q.filter(Notification.read_on.isnot(None))
        else:
            q = q.filter(Notification.read_on.is_(None))
    
    if 'user_id' in kwargs:
        q = q.filter(Notification.user_id == kwargs['user_id'])
    
    q = q.all()
    return [p.serialize() for p in q]

def new_notification(body):
    """ Sends a new notification to a user """
    noti = Notification()
    noti.user_id = body['user_id']

    try:
        sent_on = parser.isoparse(body['sent_on'])

        if sent_on > datetime.datetime.now():
            return {"error": "Invalid sent_on date"}, 400

        noti.sent_on = parser.isoparse(body['sent_on'])
    except ValueError:
        return {"error": "Invalid sent_on date"}, 400
    
    if 'read_on' in body:
        try:
            read_on = parser.isoparse(body['read_on'])

            if read_on > datetime.datetime.now() or read_on < noti.sent_on:
                return {"error": "Invalid read_on date"}, 400

            noti.read_on = read_on
        except ValueError:
            return {"error": "Invalid read_on date"}, 400

    noti.content = body['content']
    
    db.session.add(noti)
    db.session.commit()

    return noti.serialize(), 201

def get_notification(notification_id):
    """ Returns a single notification
    
    Errors:
        - 404: The notification was not found
    """
    q = db.session.query(Notification).\
        filter(Notification.id == notification_id).\
        first()
    if q is None:
        return None, 404
    else:
        return q.serialize()

def edit_notification(notification_id, body):
    """ Edits a notification
    
    Errors:
        - 404: The notification was not found
        - 400: The read_on date predates the sent_on date
    """
    q = db.session.query(Notification).\
        filter(Notification.id == notification_id).\
        first()
    if q is None:
        return None, 404
    else:
        if q.read_on is not None:
            return {"error": "Cannot modify already present read_on date"}, 400

        try:
            read_on = parser.isoparse(body['read_on'])
        except ValueError:
            return {"error": "Invalid read_on date"}, 400

        if read_on < q.sent_on or read_on > datetime.datetime.now():
            return {"error": "Invalid read_on date"}, 400
        
        q.read_on = read_on
        
        db.session.commit()
        return q.serialize()

def create_app(db_path):
    logging.basicConfig(level=logging.INFO)
    app = connexion.App(__name__)
    app.add_api('swagger.yml')
    # set the WSGI application callable to allow using uWSGI:
    # uwsgi --http :8080 -w app
    application = app.app
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['SQLALCHEMY_DATABASE_URI'] = db_path
    db.init_app(application)
    db.create_all(app=application)

    @application.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app

if __name__ == '__main__':
    app = create_app('sqlite:///notification.db')

    with app.app.app_context():
        app.run(port=8080)