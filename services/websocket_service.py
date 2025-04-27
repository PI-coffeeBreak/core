from typing import Dict, Literal, Set, Optional, Any, Callable, Generic, TypeVar
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, UTC
from pydantic import BaseModel, Field
import logging
import asyncio

logger = logging.getLogger("coffeebreak.websocket")



#######################
# Protocol definition #
#######################
# WebSocket Message Types
# 
# - topicMessage: A message to be sent to a specific topic
# - ping: A ping message to check connection
# - pong: A pong message to respond to a ping
# - subscription: A subscription message to subscribe to a topic
# - unsubscribe: A unsubscribe message to unsubscribe from a topic

T = TypeVar('T')

class WebSocketMessage(BaseModel, Generic[T]):
    """Base model for all WebSocket messages"""
    type: str = Field(..., description="Message type")
    data: T = Field(..., description="Message payload")
    timestamp: str = Field(default_factory=lambda: datetime.now().timestamp())

class TopicMessage(WebSocketMessage[T]):
    """Model for topic messages"""
    type: Literal["message"] = Field(..., description="Message type")
    topic: str = Field(..., description="Message topic")

class PingMessage(BaseModel):
    """Model for ping messages"""
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class PongMessage(BaseModel):
    """Model for pong messages"""
    pass

class SubscriptionMessage(BaseModel):
    """Model for subscription messages"""
    topic: str

class SubscriptionResultMessage(BaseModel):
    """Model for subscription result messages"""
    status: str
    topic: str
    message: Optional[str] = None

class WebSocketConnection:
    """
    Abstraction of a WebSocket connection with additional functionality
    """
    def __init__(self, websocket: WebSocket, connection_id: str, service: 'WebSocketService' = None):
        self._websocket = websocket
        self.connection_id = connection_id
        self._service = service
        self.user_id = None
        self._subscribed_topics = set()
    
    async def send(self, topic: str, message: Any) -> None:
        """Send a message through the WebSocket Service"""
        if self._service:
            try:
                await self._service.send_to_connection(self.connection_id, topic, message)
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                # Schedule disconnect for after the current iteration completes
                asyncio.create_task(self._service.disconnect(self.connection_id))
        else:
            await self._websocket.send_json(message)

    def authenticate(self, user_id: str) -> None:
        """Set the user_id for this connection"""
        self.user_id = user_id

    def is_authenticated(self) -> bool:
        """Check if the connection is authenticated"""
        return self.user_id is not None

    def add_subscription(self, topic: str) -> None:
        """Add a topic subscription"""
        self._subscribed_topics.add(topic)

    def remove_subscription(self, topic: str) -> None:
        """Remove a topic subscription"""
        self._subscribed_topics.discard(topic)

    def has_subscription(self, topic: str) -> bool:
        """Check if subscribed to a topic"""
        return topic in self._subscribed_topics
    
    @property
    def subscribed_topics(self) -> Set[str]:
        """Get the subscribed topics"""
        return self._subscribed_topics
    
    async def _send(self, message: Any) -> None:
        """Send a message through the WebSocket"""
        await self._websocket.send_json(message)

    def __str__(self):
        return f"WebSocketConnection(connection_id={self.connection_id}, user_id={self.user_id})"


class WebSocketService:
    """
    Service to manage WebSocket connections and message broadcasting
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Active connections mapped by connection_id
        self.connections: Dict[str, WebSocketConnection] = {}
        # Topic handlers mapped by topic
        self.topic_handlers: Dict[str, Dict[str, Set[Callable]]] = {}
        # Last activity timestamp for each connection
        self.last_activity: Dict[str, float] = {}
        # Ping tasks for each connection
        self.ping_tasks: Dict[str, asyncio.Task] = {}
        # Idle timeout in seconds (60 seconds to match client)
        self.idle_timeout = 60
        # Pong timeout in seconds (15 seconds)
        self.pong_timeout = 15
        self._initialized = True

    def on_receive(self, topic: str):
        """
        Decorator to register a message handler for a specific topic
        
        Args:
            topic (str): The topic to handle messages for
        
        Usage:
            @WebSocketService().on_receive("notifications")
            async def handle_notification(connection: WebSocketConnection, message: dict):
                # Handle received message
                pass
        """
        def decorator(handler: Callable):
            if topic not in self.topic_handlers:
                self.topic_handlers[topic] = {"receive": set(), "subscribe": set(), "unsubscribe": set()}
            self.topic_handlers[topic]["receive"].add(handler)
            logger.info(f"Registered receive handler for topic: {topic}")
            return handler
        return decorator

    def on_subscribe(self, topic: str):
        """
        Decorator to register a subscription handler for a specific topic
        
        Args:
            topic (str): The topic to handle subscriptions for
        
        Usage:
            @WebSocketService().on_subscribe("notifications")
            async def handle_subscription(connection: WebSocketConnection):
                # Handle subscription
                pass
        """
        def decorator(handler: Callable):
            if topic not in self.topic_handlers:
                self.topic_handlers[topic] = {"receive": set(), "subscribe": set(), "unsubscribe": set()}
            self.topic_handlers[topic]["subscribe"].add(handler)
            logger.info(f"Registered subscribe handler for topic: {topic}")
            return handler
        return decorator

    def on_unsubscribe(self, topic: str):
        """
        Decorator to register an unsubscribe handler for a specific topic
        
        Args:
            topic (str): The topic to handle unsubscription for
        
        Usage:
            @WebSocketService().on_unsubscribe("notifications")
            async def handle_unsubscribe(connection: WebSocketConnection):
                # Handle unsubscription
                pass
        """
        def decorator(handler: Callable):
            if topic not in self.topic_handlers:
                self.topic_handlers[topic] = {"receive": set(), "subscribe": set(), "unsubscribe": set()}
            self.topic_handlers[topic]["unsubscribe"].add(handler)
            logger.info(f"Registered unsubscribe handler for topic: {topic}")
            return handler
        return decorator

    async def handle_topic_message(self, connection: WebSocketConnection, topic: str, message: dict):
        """
        Handle a message for a specific topic by calling all registered handlers
        """
        logger.debug(f"Handling message for topic: {topic}")
        if topic in self.topic_handlers:
            for handler in self.topic_handlers[topic]["receive"]:
                try:
                    await handler(connection, message)
                except Exception as e:
                    logger.error(f"Error in topic handler for {topic}: {str(e)}")
        else:
            logger.warning(f"No handlers registered for topic: {topic}")

    async def connect(self, websocket: WebSocket, connection_id: str):
        """
        Establish a WebSocket connection
        """
        await websocket.accept()

        # Create new connection
        connection = WebSocketConnection(websocket, connection_id, self)
        self.connections[connection_id] = connection
        self.last_activity[connection_id] = datetime.now().timestamp()

        # Start ping monitor for this connection
        self.ping_tasks[connection_id] = asyncio.create_task(
            self._monitor_connection(connection_id)
        )

        logger.info(f"New WebSocket connection established (connection_id: {connection_id})")

    async def authenticate(self, connection_id: str, user_id: str):
        """
        Associate a user_id with a connection
        """
        if connection_id in self.connections:
            self.connections[connection_id].authenticate(user_id)
            logger.info(f"Connection {connection_id} authenticated as user {user_id}")

    async def disconnect(self, connection_id: str) -> None:
        """
        Handle WebSocket disconnection
        """
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            
            # Create a copy of subscribed topics before iteration
            topics_to_unsubscribe = connection.subscribed_topics.copy()
            
            # Call unsubscribe handlers for all topics
            for topic in topics_to_unsubscribe:
                await self.unsubscribe(connection_id, topic)

            # Cancel ping task if exists
            if connection_id in self.ping_tasks:
                self.ping_tasks[connection_id].cancel()
                del self.ping_tasks[connection_id]

            # Remove connection
            del self.connections[connection_id]
            self.last_activity.pop(connection_id, None)

            logger.info(f"WebSocket connection closed (connection_id: {connection_id})")

    async def _monitor_connection(self, connection_id: str):
        """
        Monitor connection activity and send pings when idle
        """
        logger.info(f"Starting connection monitor for {connection_id}")
        try:
            while True:
                # Check if connection still exists
                if connection_id not in self.connections:
                    break

                current_time = datetime.now().timestamp()
                last_activity = self.last_activity.get(connection_id, 0)
                idle_time = current_time - last_activity

                if idle_time >= self.idle_timeout:
                    connection = self.connections[connection_id]
                    logger.debug(f"Connection idle for {idle_time}s, sending PING to {connection_id}")
                    
                    try:
                        # Send PING with Pydantic validation
                        ping_message = WebSocketMessage(
                            type="ping",
                            data=PingMessage().model_dump()
                        )
                        await connection._send(ping_message.model_dump())
                        
                        # Wait for PONG with timeout
                        try:
                            pong_received = False
                            async with asyncio.timeout(self.pong_timeout):
                                while not pong_received:
                                    message = await connection._websocket.receive_json()
                                    if message.get("type") == "pong":
                                        # Validate PONG message
                                        WebSocketMessage(
                                            type="pong",
                                            data=PongMessage().model_dump()
                                        )
                                        # Update last activity timestamp
                                        self.last_activity[connection_id] = datetime.now().timestamp()
                                        logger.debug(f"Received PONG from {connection_id}")
                                        pong_received = True
                                        break
                                    
                        except asyncio.TimeoutError:
                            logger.warning(f"No PONG received from {connection_id} within {self.pong_timeout}s")
                            await self.disconnect(connection_id)
                            break

                    except WebSocketDisconnect:
                        logger.debug(f"WebSocket disconnected for {connection_id}")
                        await self.disconnect(connection_id)
                        break
                            
                    except Exception as e:
                        logger.error(f"Error sending PING to {connection_id}: {str(e)}")
                        await self.disconnect(connection_id)
                        break

                await asyncio.sleep(1)  # Check every second
                
        except asyncio.CancelledError:
            logger.debug(f"Connection monitor cancelled for {connection_id}")
        except Exception as e:
            logger.error(f"Error in connection monitor for {connection_id}: {str(e)}")
            await self.disconnect(connection_id)

    async def update_activity(self, connection_id: str):
        """
        Update last activity timestamp for a connection
        """
        if connection_id in self.last_activity:
            self.last_activity[connection_id] = datetime.now().timestamp()
            logger.debug(f"Updated activity timestamp for {connection_id}")

    async def subscribe(self, connection_id: str, topic: str) -> None:
        """
        Subscribe a connection to a topic
        """
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.add_subscription(topic)
            logger.debug(f"Connection {connection_id} subscribed to topic {topic}")

            # Call subscription handlers
            if topic in self.topic_handlers:
                for handler in self.topic_handlers[topic]["subscribe"]:
                    try:
                        await handler(connection)
                    except Exception as e:
                        logger.error(f"Error in subscription handler for {topic}: {str(e)}")

    async def unsubscribe(self, connection_id: str, topic: str):
        """
        Unsubscribe a connection from a topic
        """
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            
            # Call unsubscribe handlers before removing the subscription
            if topic in self.topic_handlers:
                for handler in self.topic_handlers[topic]["unsubscribe"]:
                    try:
                        await handler(connection)
                    except Exception as e:
                        logger.error(f"Error in unsubscribe handler for {topic}: {str(e)}")
            
            connection.remove_subscription(topic)
            logger.debug(f"Connection {connection_id} unsubscribed from topic {topic}")

    def _prepare_message(self, topic: str, message: Any, message_type: str = "message") -> dict:
        """
        Prepare message for sending with standard format and validate using Pydantic
        """
        if isinstance(message, BaseModel):
            message = message.model_dump()
        
        ws_message = TopicMessage(
            type=message_type,
            topic=topic,
            data=message
        )
        return ws_message.model_dump()
    
    async def send_to_connection(self, connection_id: str, topic: str, message: Any) -> None:
        """
        Send a message to a specific connection
        """
        message_data = self._prepare_message(topic, message)
        await self.connections[connection_id]._send(message_data)

    async def broadcast_to_user(self, target_user_id: str, topic: str, message: Any) -> None:
        """
        Broadcast a message to all connections of a specific user (send_to_connection is preferred)
        """
        message_data = self._prepare_message(topic, message)

        for connection in self.connections.values():
            if connection.user_id == target_user_id:
                try:
                    await connection._send(message_data)
                except Exception as e:
                    logger.error(f"Error sending message to user {target_user_id}: {str(e)}")

    async def broadcast_to_topic(self, topic: str, message: Any) -> None:
        """
        Broadcast a message to all connections subscribed to a topic (send_to_connection is preferred)
        """
        message_data = self._prepare_message(topic, message)

        for connection in self.connections.values():
            if connection.has_subscription(topic):
                try:
                    await connection._send(message_data)
                except Exception as e:
                    logger.error(f"Error broadcasting to topic {topic}: {str(e)}")

    async def broadcast_to_all(self, topic: str, message: Any) -> None:
        """
        Broadcast a message to all connected clients (send_to_connection is preferred)
        """
        message_data = self._prepare_message(topic, message)

        for connection in self.connections.values():
            try:
                await connection._send(message_data)
            except Exception as e:
                logger.error(f"Error broadcasting to all: {str(e)}")

