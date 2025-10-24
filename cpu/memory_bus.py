import logging
from utils.constants import MEMORY_SIZE
from typing import Optional
logger = logging.getLogger(__name__)
logger.info("Memory module initialized")

class MemoryBus:
    def __init__(self) -> None:
        logger.info("Initializing memory")
        self.memory_size = MEMORY_SIZE  # 1 MB memory
        self.address_range = range(self.memory_size)
        self.storage = {i: 0 for i in self.address_range}
        self.word_mask = 0xFFFFFFFF  # 32-bit word mask
        logger.info(f"Memory initialized with size {self.memory_size} bytes")

    def _validate_address(self, address: int) -> None:
        if not isinstance(address, int):
            raise TypeError("Address must be an integer")
        if address not in self.address_range:
            raise ValueError(f"Address {address} out of range (0 to {self.memory_size - 1})")

    def _access_memory(self, address: int, value: Optional[int] = None) -> int:
        try:
            self._validate_address(address)
            if value is None:
                logger.info(f"Loading word from address {address}")
                return self.storage.get(address, 0)
            else:
                masked_value = value & self.word_mask
                self.storage[address] = masked_value
                logger.info(f"Stored word at address {address}: {masked_value}")
                return masked_value  # ✅ Return an int here too
        except (TypeError, ValueError) as e:
            logger.error(f"Memory access error at address {address}: {e}")
            raise

    def load_word(self, address: int) -> int:
        return self._access_memory(address)

    def store_word(self, address: int, value: int) -> None:
        self._access_memory(address, value)