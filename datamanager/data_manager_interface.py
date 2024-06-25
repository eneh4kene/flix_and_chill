from abc import ABC, abstractmethod
from typing import Dict, List


class DatabaseManagerInterface(ABC):

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def save_data(self):
        pass

    @abstractmethod
    def get_all(self, entity: str) -> List[Dict]:
        pass

    @abstractmethod
    def get_by_id(self, entity: str, id: int) -> Dict:
        pass

    @abstractmethod
    def add(self, entity: str, data: Dict) -> Dict:
        pass

    @abstractmethod
    def update(self, entity: str, id: int, data: Dict) -> Dict:
        pass

    @abstractmethod
    def delete(self, entity: str, id: int) -> Dict:
        pass
