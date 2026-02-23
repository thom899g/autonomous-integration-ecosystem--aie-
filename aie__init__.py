"""
Autonomous Integration Ecosystem (AIE) Core Package

A seamless, self-evolving network where AI modules can integrate and communicate
autonomously, enhancing ecosystem growth through dynamic interactions.

Version: 1.0.0
"""
__version__ = "1.0.0"
__author__ = "Evolution Ecosystem"

from .module_interface import AIModule, Message, ModuleStatus
from .module_registry import ModuleRegistry
from .communication_layer import CommunicationBus
from .self_learning import SelfLearningProtocol
from .feedback_loop import FeedbackCollector

__all__ = [
    'AIModule',
    'Message',
    'ModuleStatus',
    'ModuleRegistry',
    'CommunicationBus',
    'SelfLearningProtocol',
    'FeedbackCollector'
]