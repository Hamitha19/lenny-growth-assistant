
from database import Base, engine

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
print("Tables: chat_sessions, chat_messages")