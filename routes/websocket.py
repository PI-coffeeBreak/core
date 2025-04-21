from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
from services.websocket_service import WebSocketService
from dependencies.auth import get_current_user
import uuid
import logging
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from dependencies.app import get_current_app

logger = logging.getLogger("coffeebreak.websocket")

# Configure CORS for WebSocket
app = get_current_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def send_subscription_confirmation(websocket: WebSocket, topic: str, status: str, message: str = None):
    """Helper function to send subscription confirmation"""
    response = {
        "type": "subscription_result",
        "status": status,
        "topic": topic
    }
    if message:
        response["message"] = message
    
    try:
        await websocket.send_json(response)
        logger.debug(f"Sent subscription confirmation for topic {topic}: {status}")
    except Exception as e:
        logger.error(f"Failed to send subscription confirmation: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication
    Supports both authenticated and unauthenticated connections
    """
    logger.info("Received WebSocket connection request")
    try:
        websocket_service = WebSocketService()
        # Generate unique connection ID for this connection
        connection_id = str(uuid.uuid4())
        
        try:
            # Connect without authentication
            await websocket_service.connect(websocket, connection_id)
            logger.info("New WebSocket connection accepted")
            
            while True:
                # Wait for messages from the client
                try:
                    message = await websocket.receive_json()
                    logger.debug(f"Received message: {message}")
                    message_type = message.get("type", "")
                    logger.debug(f"Received message type: {message_type}")

                    # Handle PING/PONG messages immediately
                    if message_type == "ping":
                        logger.debug(f"Received PING from {connection_id}, sending PONG")
                        await websocket.send_json({"type": "pong"})
                        # Update activity and continue to next message
                        await websocket_service.update_activity(connection_id)
                        continue
                    elif message_type == "pong":
                        # Just update activity and continue
                        await websocket_service.update_activity(connection_id)
                        continue

                    # Update last activity timestamp for any other message
                    await websocket_service.update_activity(connection_id)

                    # Handle authentication message
                    if message_type == "authenticate":
                        try:
                            # Set a timeout for authentication
                            user = await asyncio.wait_for(
                                get_current_user(message["token"]),
                                timeout=10.0
                            )
                            
                            if user:
                                # Associate user_id with the connection
                                await websocket_service.authenticate(connection_id, user.id)
                                
                                # Send authentication success message
                                await websocket.send_json({
                                    "type": "authentication_result",
                                    "status": "success",
                                    "user_id": user.id
                                })
                            else:
                                await websocket.send_json({
                                    "type": "authentication_result",
                                    "status": "error",
                                    "message": "Invalid authentication token"
                                })
                        except (asyncio.TimeoutError) as e:
                            logger.debug("Authentication timeout")
                            await websocket.send_json({
                                "type": "authentication_result",
                                "status": "error",
                                "message": "Authentication failed"
                            })

                    # Handle subscription messages
                    elif message_type == "subscribe" and "topic" in message:
                        topic = message["topic"]
                        
                        try:
                            # Attempt to subscribe
                            await websocket_service.subscribe(connection_id, topic)
                            
                            # Send success confirmation
                            await send_subscription_confirmation(websocket, topic, "success")
                            logger.info(f"Successfully subscribed to topic {topic}")

                        except Exception as e:
                            logger.error(f"Failed to subscribe to topic {topic}: {str(e)}")
                            await send_subscription_confirmation(
                                websocket, 
                                topic, 
                                "error", 
                                f"Failed to subscribe: {str(e)}"
                            )

                    # Handle unsubscribe messages
                    elif message_type == "unsubscribe" and "topic" in message:
                        topic = message["topic"]
                        try:
                            await websocket_service.unsubscribe(connection_id, topic)
                            await websocket.send_json({
                                "type": "unsubscription_result",
                                "status": "success",
                                "topic": topic
                            })
                            logger.info(f"Successfully unsubscribed from topic {topic}")
                        except Exception as e:
                            logger.error(f"Failed to unsubscribe from topic {topic}: {str(e)}")
                            await websocket.send_json({
                                "type": "unsubscription_result",
                                "status": "error",
                                "topic": topic,
                                "message": f"Failed to unsubscribe: {str(e)}"
                            })

                    # Handle topic-specific messages
                    elif message_type == "message" and "topic" in message and "data" in message:
                        topic = message["topic"]
                        # Check if user is subscribed to the topic
                        if topic not in websocket_service.subscriptions.get(connection_id, set()):
                            await websocket.send_json({
                                "type": "message_result",
                                "status": "error",
                                "message": "Not subscribed to this topic"
                            })
                            continue

                        # Handle message with registered topic handlers
                        await websocket_service.handle_topic_message(
                            websocket,
                            connection_id,
                            topic,
                            message["data"]
                        )

                except json.JSONDecodeError:
                    logger.warning(f"Received invalid JSON from {connection_id}")
                    continue

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected (connection_id: {connection_id})")
            await websocket_service.disconnect(connection_id)

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011)  # Internal error
