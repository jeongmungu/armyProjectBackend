from sqlalchemy.orm import Session
from database import engine
from models import MessageLog

def check_message_log():
    with Session(engine) as db:
        logs = db.query(MessageLog).order_by(MessageLog.dt.desc()).limit(5).all()
        print(f"Found {len(logs)} logs.")
        for log in logs:
            print(f"ID: {log.id}, Date: {log.dt}, Type: {log.msg_type}")
            print(f"  Title: {log.title}")
            print(f"  SrvNo: {log.srvno}")
            print(f"  Recipient: {log.recipient}")
            print(f"  Content: {log.content[:50]}..." if log.content else "  Content: None")
            print("-" * 20)

if __name__ == "__main__":
    check_message_log()
