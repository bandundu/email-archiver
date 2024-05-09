from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Index, func
from sqlalchemy import event

# Define the base class for all models
Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True)
    password = Column(String)
    protocol = Column(String)
    server = Column(String)
    port = Column(Integer)
    available_inboxes = Column(String)
    selected_inboxes = Column(String)
    update_interval = Column(Integer, default=300)

    emails = relationship("Email", back_populates="account") # One account can have many emails
    email_uids = relationship("EmailUID", back_populates="account") 

    def __repr__(self):
        return f"<Account(id={self.id}, email='{self.email}')>"


class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    subject = Column(String)
    sender = Column(String)
    recipients = Column(String)
    date = Column(DateTime)
    body = Column(Text)
    fingerprint = Column(String, unique=True)
    __ts_vector__ = Column(
        Text,
        nullable=False,
        default="",
        index=Index("ix_emails_fts", postgresql_using="gin"),
    )

    account = relationship("Account", back_populates="emails")
    attachments = relationship("Attachment", back_populates="email")

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "subject": self.subject,
            "sender": self.sender,
            "recipients": self.recipients,
            "date": self.date,
            "body": self.body,
        }

    def __repr__(self):
        return f"<Email(id={self.id}, subject='{self.subject}')>"


def update_email_ts_vector(target, value, oldvalue, initiator):
    target.__ts_vector__ = func.to_tsvector(value)


event.listen(Email.body, "set", update_email_ts_vector)


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey("emails.id"))
    filename = Column(String)
    content = Column(String)
    cid = Column(String)

    email = relationship("Email", back_populates="attachments")

    def to_dict(self):
        return {
            "id": self.id,
            "email_id": self.email_id,
            "filename": self.filename,
            "cid": self.cid,
        }

    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}')>"


class EmailUID(Base):
    __tablename__ = "email_uids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    uid = Column(String)

    account = relationship("Account", back_populates="email_uids")

    def __repr__(self):
        return f"<EmailUID(id={self.id}, uid='{self.uid}')>"
