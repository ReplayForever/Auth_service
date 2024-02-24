from abc import ABC, abstractmethod


class AbstractService(ABC):

    @abstractmethod
    def get_data(self, *args, **kwargs):
        ...
