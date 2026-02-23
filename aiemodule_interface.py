"""
Universal Interface for AI Module Communication

This module defines the base class and protocols for all AI modules in the ecosystem.
It ensures type-safe communication and consistent behavior across all modules.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar
import json
import logging
import uuid

# Type variable for message payloads
T = TypeVar('T')

# Configure logging
logger = logging.getLogger(__name__)


class ModuleStatus(Enum):
    """Status enumeration for AI modules"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    LEARNING = "learning"
    INTEGRATING = "integrating"


class MessageType(Enum):
    """Types of messages that can be exchanged between modules"""
    QUERY = "query"
    RESPONSE = "response"
    COMMAND = "command"
    STATUS_UPDATE = "status_update"
    CAPABILITY_ANNOUNCE = "capability_announce"
    ERROR = "error"
    FEEDBACK = "feedback"
    LEARNING_UPDATE = "learning_update"


@dataclass
class Message:
    """
    Universal message format for inter-module communication.
    Uses dataclass for immutability and type safety.
    """
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    message_type: MessageType = MessageType.QUERY
    timestamp: datetime = field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-10, where 10 is highest
    requires_response: bool = False
    response_to: Optional[str] = None
    
    def to_json(self) -> str:
        """Convert message to JSON string for transmission"""
        try:
            data = {
                'message_id': self.message_id,
                'sender_id': self.sender_id,
                'receiver_id': self.receiver_id,
                'message_type': self.message_type.value,
                'timestamp': self.timestamp.isoformat(),
                'payload': self.payload,
                'metadata': self.metadata,
                'priority': self.priority,
                'requires_response': self.requires_response,
                'response_to': self.response_to
            }
            return json.dumps(data)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize message {self.message_id}: {e}")
            raise
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create Message instance from JSON string"""
        try:
            data = json.loads(json_str)
            return cls(
                message_id=data.get('message_id', str(uuid.uuid4())),
                sender_id=data.get('sender_id', ''),
                receiver_id=data.get('receiver_id', ''),
                message_type=MessageType(data.get('message_type', 'query')),
                timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
                payload=data.get('payload', {}),
                metadata=data.get('metadata', {}),
                priority=data.get('priority', 1),
                requires_response=data.get('requires_response', False),
                response_to=data.get('response_to')
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to deserialize message from JSON: {e}")
            raise


class AIModule(ABC):
    """
    Abstract Base Class for all AI modules in the ecosystem.
    
    Every module must inherit from this class and implement the required methods.
    This ensures consistent interface and communication patterns.
    """
    
    def __init__(self, module_id: str, module_name: str, version: str = "1.0.0"):
        """
        Initialize the AI module with unique identifier and metadata.
        
        Args:
            module_id: Unique identifier for this module instance
            module_name: Human-readable name of the module
            version: Version string (semantic versioning recommended)
        """
        # Core identity
        self.module_id = module_id
        self.module_name = module_name
        self.version = version
        
        # State management
        self.status: ModuleStatus = ModuleStatus.INITIALIZING
        self.capabilities: Dict[str, Any] = {}
        self.dependencies: List[str] = []
        self.integrated_modules: List[str] = []
        
        # Performance metrics
        self.metrics: Dict[str, Any] = {
            'total_messages_sent': 0,
            'total_messages_received': 0,
            'error_count': 0,
            'avg_response_time': 0.0,
            'last_activity': datetime.utcnow().isoformat()
        }
        
        # Initialize in isolation first
        self._initialize_module()
        
        # Then attempt integration with ecosystem
        self._announce_capabilities()
    
    @abstractmethod
    def _initialize_module(self) -> None:
        """
        Module-specific initialization.
        
        This method MUST be implemented by subclasses to set up
        module-specific resources, connections, or configurations.
        
        Raises:
            ModuleInitializationError: If module fails to initialize
        """
        pass
    
    def _announce_capabilities(self) -> None:
        """
        Announce module capabilities to the ecosystem.
        
        This is called automatically during initialization.
        Modules can override this to customize announcement logic.
        """
        announcement = Message(
            sender_id=self.module_id,
            message_type=MessageType.CAPABILITY_ANNOUNCE,
            payload={
                'module_id': self.module_id,
                'module_name': self.module_name,
                'version': self.version,
                'capabilities