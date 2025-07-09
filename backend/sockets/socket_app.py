"""
Socket.IO application setup and configuration.
"""
import socketio
from .events import connection, matchmaking, game


def create_socket_app():
    """Create and configure the Socket.IO server."""
    sio = socketio.AsyncServer(
        cors_allowed_origins="*",
        async_mode='asgi'
    )
    
    # Register event handlers
    connection.register_events(sio)
    matchmaking.register_events(sio)
    game.register_events(sio)
    
    return sio


def create_socket_asgi_app(fastapi_app):
    """Create the combined FastAPI + Socket.IO ASGI application."""
    sio = create_socket_app()
    return socketio.ASGIApp(sio, fastapi_app)