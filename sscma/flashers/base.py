from abc import ABC, abstractmethod

class BaseFlasher(ABC):
    """Base class for all programmers.

    All programmers must implement the methods defined in this class.
    """
    
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Initialize the programmer.

        This method should be overridden by the subclass.
        """
        pass
    
    
    @abstractmethod
    def write(self, data, offset=0):
        """Write data to the programmer.

        This method should be overridden by the subclass.
        """
        pass