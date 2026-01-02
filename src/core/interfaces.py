from abc import ABC, abstractmethod


class IRepository(ABC):
    @abstractmethod
    def load_data(self): pass

    @abstractmethod
    def add(self, item): pass

    @abstractmethod
    def delete(self, item_id): pass
