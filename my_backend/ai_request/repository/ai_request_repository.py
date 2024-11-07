from abc import ABC, abstractmethod


class AiRequestRepository(ABC):
    @abstractmethod
    def aiRequest(self, command, data):
        pass