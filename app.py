import connexion, logging, database
from database import Notification
from flask import jsonify
import datetime
from dateutil import parser

db_session = None

def get_user_notifications(user_id):
    """ Returns all of a user's notifications """
    q = db_session.query(Notification).\
        filter(Notification.user_id == user_id).\
        all()
    return [p.serialize() for p in q]

def new_user_notification(user_id, body):
    """ Sends a new notification to a user """
    noti = Notification()
    noti.user_id = user_id
    noti.sent_on = datetime.datetime.now()
    noti.content = body['content']
    
    db_session.add(noti)
    db_session.commit()

    return noti.serialize()

def get_user_read_notifications(user_id):
    """ Returns a user's read notifications """
    q = db_session.query(Notification).\
        filter(Notification.user_id == user_id).\
        filter(Notification.read_on.isnot(None)).\
        all()
    return [p.serialize() for p in q]

def get_user_unread_notifications(user_id):
    """ Returns a user's unread notifications """
    q = db_session.query(Notification).\
        filter(Notification.user_id == user_id).\
        filter(Notification.read_on.is_(None)).\
        all()
    return [p.serialize() for p in q]

def get_notification(notification_id):
    """ Returns a single notification
    
    Errors:
        - 404: The notification was not found
    """
    q = db_session.query(Notification).\
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
    q = db_session.query(Notification).\
        filter(Notification.id == notification_id).\
        first()
    if q is None:
        return None, 404
    else:
        if 'read_on' in body:
            read_on = parser.isoparse(body['read_on'])

            if read_on < q.sent_on:
                return {"error": "Invalid read_on date"}, 400
            
            q.read_on = read_on

        if 'content' in body:
            q.content = body['content']
        
        db_session.commit()


logging.basicConfig(level=logging.INFO)
db_session = database.init_db('sqlite:///notification.db')
app = connexion.App(__name__)
app.add_api('swagger.yml')
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(port=8080)