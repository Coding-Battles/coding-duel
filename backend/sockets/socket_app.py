"""
Socket.IO application setup and configuration.
"""

import socketio
from .events import connection, matchmaking


def create_socket_app(database=None, player_to_game=None, app=None):
    """Create and configure the Socket.IO server."""
    sio = socketio.AsyncServer(
        cors_allowed_origins="*",
        async_mode="asgi",
        ping_timeout=60,  # 60 seconds before considering client disconnected
        ping_interval=25,  # Send ping every 25 seconds
        logger=True,  # Enable logging for debugging
        engineio_logger=True,
    )

    # Register event handlers with dependencies
    connection.register_events(sio)
    matchmaking.register_events(sio)
    return sio


def create_socket_asgi_app(fastapi_app):
    """Create the combined FastAPI + Socket.IO ASGI application."""
    sio = create_socket_app()
    return socketio.ASGIApp(sio, fastapi_app)
