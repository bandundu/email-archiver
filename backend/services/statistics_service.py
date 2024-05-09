from models.models import Email, Account, Attachment
from models.database import get_db


def email_statistics():
    db = next(get_db())

    total_emails = db.query(Email).count()
    total_accounts = db.query(Account).count()
    total_attachments = db.query(Attachment).count()

    stats = {
        "totalEmails": total_emails,
        "totalAccounts": total_accounts,
        "totalAttachments": total_attachments,
    }

    return stats
