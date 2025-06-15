from fastapi import FastAPI

import pydantic
import socketio

app = FastAPI()
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode='asgi'
)

socket_app = socketio.ASGIApp(sio, app) ## Combine FastAPI and Socket.IO apps


