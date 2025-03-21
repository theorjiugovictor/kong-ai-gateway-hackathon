import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator

from ..utils import log

logger = log.get_logger(__name__)

class CouchbaseChatClient:
    def __init__(
        self,
        connection_string: str = None,
        username: str = None,
        password: str = None,
        bucket_name: str = None,
        scope_name: str = "_default",
        chats_collection: str = "chats",
        messages_collection: str = "chat_messages"
    ):
        self.connection_string = connection_string or os.getenv("COUCHBASE_CONNECTION_STRING", "couchbase://localhost")
        self.username = username or os.getenv("COUCHBASE_USERNAME", "user")
        self.password = password or os.getenv("COUCHBASE_PASSWORD", "password")
        self.bucket_name = bucket_name or os.getenv("COUCHBASE_BUCKET", "_default")
        self.scope_name = scope_name
        self.chats_collection = chats_collection
        self.messages_collection = messages_collection
        self.cluster = None
        self.bucket = None
        self.scope = None
        self.chats = None
        self.messages = None

    def connect(self) -> None:
        """Establish connection to Couchbase database."""
        try:
            auth = PasswordAuthenticator(self.username, self.password)
            options = ClusterOptions(auth)

            self.cluster = Cluster(self.connection_string, options)

            # Try to connect to the bucket, but don't fail if it doesn't exist yet
            try:
                self.bucket = self.cluster.bucket(self.bucket_name)
                self.scope = self.bucket.scope(self.scope_name)

                # Get collection references
                try:
                    self.chats = self.scope.collection(self.chats_collection)
                    self.messages = self.scope.collection(self.messages_collection)
                except Exception as col_err:
                    logger.warning(f"Collections not ready yet: {str(col_err)}")

                logger.info("Connected to Couchbase database with bucket")
            except Exception as bucket_err:
                logger.warning(f"Bucket not ready yet: {str(bucket_err)}")
                # Just connect to cluster for now, bucket will be created later
                logger.info("Connected to Couchbase cluster only")

        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def create_chat(self, metadata: Dict[str, Any] = None) -> str:
        """
        Create a new chat session.

        Args:
            metadata: Optional metadata for the chat session

        Returns:
            The UUID of the created chat session
        """
        if not self.cluster:
            self.connect()

        # If we don't have the chats collection ready, initialize
        if not self.chats:
            # If still not ready, we can't proceed
            if not self.chats:
                logger.error("Failed to initialize collections for chat creation")
                # Try a direct bucket connection as a fallback
                try:
                    self.bucket = self.cluster.bucket(self.bucket_name)
                    self.scope = self.bucket.scope(self.scope_name)
                    self.chats = self.scope.collection(self.chats_collection)
                except Exception as e:
                    logger.error(f"Complete failure to get chats collection: {str(e)}")
                    raise ValueError("Cannot create chat: database not initialized")

        chat_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        document = {
            "id": chat_id,
            "created_at": now,
            "updated_at": now,
            "metadata": metadata or {}
        }

        try:
            # Insert document with its ID as the key
            self.chats.upsert(chat_id, document)
            logger.info(f"Created chat session with ID: {chat_id}")
            return chat_id
        except Exception as e:
            logger.error(f"Failed to create chat: {str(e)}")
            # In case of failure, give more diagnostic information
            try:
                logger.error(f"Current bucket: {self.bucket_name}, collection: {self.chats_collection}")
                if self.bucket:
                    logger.error("Bucket exists, but collection operation failed")
                else:
                    logger.error("Bucket does not exist or is not connected")
            except Exception as _:
                pass
            raise

    def add_message(
        self,
        chat_id: str,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> int:
        """
        Add a message to an existing chat session.

        Args:
            chat_id: The UUID of the chat session
            role: The role of the message sender (e.g., 'user', 'assistant')
            content: The content of the message
            metadata: Optional metadata for the message

        Returns:
            The ID of the added message
        """
        if not self.cluster:
            self.connect()

        # If we don't have the collections ready, initialize
        if not self.chats or not self.messages:
            # If still not ready, we can't proceed
            if not self.chats or not self.messages:
                logger.error("Collections not available for adding message")
                raise ValueError("Cannot add message: database collections not initialized")

        # Update the chat's updated_at timestamp
        try:
            chat = self.get_chat(chat_id)
            if not chat:
                logger.warning(f"Chat with ID {chat_id} not found, creating new chat")
                # If chat doesn't exist, create it first
                self.create_chat(metadata or {})
                chat = self.get_chat(chat_id)
                if not chat:
                    raise ValueError(f"Failed to create chat with ID {chat_id}")

            # Update chat's timestamp
            chat["updated_at"] = datetime.utcnow().isoformat()
            self.chats.upsert(chat_id, chat)

            # Generate message ID (using timestamp and a random string)
            message_id = int(datetime.utcnow().timestamp() * 1000)

            # Create message document
            message_key = f"{chat_id}:{message_id}"
            message_doc = {
                "id": message_id,
                "chat_id": chat_id,
                "role": role,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }

            # Insert message
            self.messages.upsert(message_key, message_doc)

            logger.info(f"Added message with ID {message_id} to chat {chat_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to add message: {str(e)}")
            # Give more diagnostic info
            try:
                if not self.chats:
                    logger.error("Chats collection not available")
                if not self.messages:
                    logger.error("Messages collection not available")
            except:
                pass
            raise

    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a chat session by ID.

        Args:
            chat_id: The UUID of the chat session

        Returns:
            The chat session details or None if not found
        """
        if not self.cluster:
            self.connect()

        if not self.chats:
            logger.error("Chats collection not available")
            return None

        try:
            result = self.chats.get(chat_id)
            logger.debug(f"Get result: {type(result)} {result}")

            if not result or not hasattr(result, 'value') or not result.value:
                return None

            return result.value
        except Exception as e:
            logger.warning(f"Failed to get chat: {str(e)}")
            return None

    def get_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a chat session.

        Args:
            chat_id: The UUID of the chat session

        Returns:
            List of messages in the chat session
        """
        if not self.cluster:
            self.connect()

        # If we don't have the messages collection ready, initialize
        if not self.messages or not self.bucket:
            # If still not ready, we return empty list instead of failing
            if not self.messages or not self.bucket:
                logger.warning("Messages collection not available")
                return []

        try:
            # Use N1QL query to get all messages for the chat
            query = f"""
            SELECT m.*
            FROM {self.bucket_name}.{self.scope_name}.{self.messages_collection} m
            WHERE m.chat_id = $chat_id
            ORDER BY m.created_at ASC
            """

            options = QueryOptions(named_parameters={"chat_id": chat_id})
            result = self.cluster.query(query, options)

            messages = []
            for row in result:
                # Remove the document metadata if present
                if "m" in row:
                    row = row["m"]
                messages.append(row)

            return messages
        except Exception as e:
            logger.warning(f"Failed to get messages (returning empty list): {str(e)}")
            return []  # Return empty list instead of raising exception

    def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat session and all its messages.

        Args:
            chat_id: The UUID of the chat session

        Returns:
            True if the chat was deleted, False otherwise
        """
        if not self.cluster:
            self.connect()

        # If we don't have the collections ready, initialize
        if not self.chats or not self.messages:
            # If still not ready, we can't proceed
            if not self.chats:
                logger.warning("Collections not available for deleting chat")
                return False

        try:
            # Check if chat exists
            chat = self.get_chat(chat_id)
            if not chat:
                return False

            # Try to delete the messages first
            try:
                # Delete all messages for the chat
                query = f"""
                DELETE FROM {self.bucket_name}.{self.scope_name}.{self.messages_collection} m
                WHERE m.chat_id = $chat_id
                """

                options = QueryOptions(named_parameters={"chat_id": chat_id})
                self.cluster.query(query, options)
                logger.info(f"Deleted messages for chat {chat_id}")
            except Exception as msg_e:
                logger.warning(f"Failed to delete messages for chat: {str(msg_e)}")
                # Continue to delete the chat anyway

            # Delete the chat
            try:
                self.chats.remove(chat_id)
                logger.info(f"Deleted chat {chat_id}")
                return True
            except Exception as chat_e:
                logger.error(f"Failed to delete chat: {str(chat_e)}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete chat (general error): {str(e)}")
            return False

    def close(self) -> None:
        """Close the database connection."""
        if self.cluster:
            # Close the Couchbase connection
            # (Note: Couchbase Python SDK may handle this automatically)
            self.cluster = None
            logger.info("Database connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
