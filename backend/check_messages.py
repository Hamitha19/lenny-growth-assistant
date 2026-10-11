from sqlalchemy import select, func
from database import SessionLocal, ChatMessage, ChatSession

with SessionLocal() as db:
    session_count = db.scalar(
        select(func.count()).select_from(ChatSession)
    )
    message_count = db.scalar(
        select(func.count()).select_from(ChatMessage)
    )

    print("Saved sessions:", session_count)
    print("Saved messages:", message_count)

    latest = db.scalars(
        select(ChatMessage)
        .order_by(ChatMessage.id.desc())
        .limit(2)
    ).all()

    for message in reversed(latest):
        print(message.role, ":", message.content[:100])