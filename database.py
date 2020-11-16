from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Notification(db.Model):
    __tablename__ = 'notification'

    # Unique id
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Recipient's id
    user_id = Column(Integer)

    # Notification text
    content = Column(Text(256))

    # Time when the notification was sent
    sent_on = Column(DateTime)

    # Time when the notification was read (may be None)
    read_on = Column(DateTime)

    def serialize(self):
        return {
            "url": f"/notifications/{self.id}",
            "user_id": self.user_id,
            "content": self.content,
            "sent_on": self.sent_on,
            "read_on": self.read_on
        }
