from abc import ABC, abstractmethod
from langchain_core.messages import BaseMessage


class AnalyzerPrompt(ABC):
    @abstractmethod
    def get_system_message(self) -> str:
        """Returns the system message for the analyzer."""
        pass

    @abstractmethod
    def get_user_message(self) -> str:
        """Returns the user message for the analyzer."""
        pass

    @abstractmethod
    def get_messages(self) -> list[BaseMessage]:
        """Returns a list of messages for the analyzer."""
        pass
