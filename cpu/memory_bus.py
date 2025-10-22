# class memory 

from utils.constants import MEMORY_SIZE
import logging
logger = logging.getLogger(__name__)
logger.info("Memoryu initialized")

class MemoryBus:
    def __init__(self) -> None:
        logger.info("Initializing Memory")
        self.memory_size = MEMORY_SIZE  # 1 MB memory
        self.address_range = range(0, self.memory_size) # Valid address range
        self.storage = {i: 0 for i in range(self.memory_size)} # Initialize memory with zeros
        self.word_mask = 0xFFFFFFFF  # 32-bit word mask
        self.cache = None  # Placeholder for cache integration
        logger.info("Memory initialized with size 1 MB")

    def _validate_address(self, address: int) -> None:
        if not isinstance(address, int):
            raise TypeError("Address must be an integer")
        if address not in self.address_range:
            raise ValueError(f"Address {address} out of range. Valid range: 0 to {self.memory_size - 1}")

    def load_word(self, address: int) -> int:
        try:
            self._validate_address(address)
            logger.info(f"Loading word from address {address}")
        except (TypeError, ValueError) as e:
            logger.error(f"Error loading word: {e}")
            raise
        return self.storage.get(address, 0)

    
    def store_word(self, address: int, value: int) -> None:
        try:
            self._validate_address(address)
            logger.info(f"Loading word from address {address}")
        except (TypeError, ValueError) as e:
            logger.error(f"Error storing word: {e}")
            raise
        masked_value = value & self.word_mask
        self.storage[address] = masked_value
        logger.info(f"Stored word at address {address}: {value}")