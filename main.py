from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Message
import asyncio

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

# DATABASE SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WEBSOCKET
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    db = SessionLocal()

    # Send old chat history
    messages = db.query(Message).all()

    for msg in messages:
        await websocket.send_json({
            "username": msg.username,
            "text": msg.text
        })

    try:
        while True:
            data = await websocket.receive_json()

            username = data["username"]
            text = data["text"]

            # Save to DB
            new_msg = Message(
                username=username,
                text=text
            )

            db.add(new_msg)
            db.commit()

            # STREAMING EFFECT
            streamed = ""

            for char in text:
                streamed += char

                for client in clients:
                    await client.send_json({
                        "username": username,
                        "text": streamed,
                        "streaming": True
                    })

                await asyncio.sleep(0.03)

            # FINAL MESSAGE
            for client in clients:
                await client.send_json({
                    "username": username,
                    "text": text,
                    "streaming": False
                })

    except WebSocketDisconnect:
        clients.remove(websocket)

# CLEAR CHAT
@app.delete("/clear")
def clear_chat():
    db = SessionLocal()
    db.query(Message).delete()
    db.commit()

    return {"message": "Chat cleared"}