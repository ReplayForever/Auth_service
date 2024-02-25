from abc import ABC, abstractmethod


class AbstractService(ABC):

    @abstractmethod
    def get_data(self, *args, **kwargs):
        ...


class PatchAbstractService(ABC):

    @abstractmethod
    def patch(self, *args, **kwargs):
        ...
        ...


class PostAbstractService(ABC):

    @abstractmethod
    def post(self, *args, **kwargs):
        ...
