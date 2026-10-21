# connection.py

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseConnection(ABC):
    """
    Abstract base class for all database/vector store connections.
    """

    def __init__(self, parameters: Dict[str, Any]):
        self.parameters = parameters

    @abstractmethod
    def connect(self) -> Any:
        """
        Establish the connection and return the client object.
        """
        pass