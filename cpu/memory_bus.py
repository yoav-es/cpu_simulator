# imports
import logging
from utils.constants import MEMORY_SIZE, WORD_SIZE
from typing import Optional

logger = logging.getLogger(__name__)
logger.info("Memory module initialized")


class MemoryBus:
    """class memory bus"""

    def __init__(self, size=MEMORY_SIZE) -> None:
        # initialize values for memory bus
        logger.info("Initializing memory")
        self.memory_size = size  # 1 MB memory by default
        self.address_range = range(self.memory_size)
        self.storage = {i: 0 for i in self.address_range}
        self.word_mask = 0xFFFFFFFF  # 32-bit word mask
        logger.info(f"Memory initialized with size {self.memory_size} bytes")

    def __getitem__(self, address: int) -> int:
        """Enable bracket-style memory read access."""
        return self.storage.get(address, 0)

    def __setitem__(self, address: int, value: int) -> None:
        """Enable bracket-style memory write access."""
        self.storage[address] = value & self.word_mask

    def _validate_address(self, address: int) -> None:
        """Address Validation"""
        logger.info(f"validating {address}")

        if address is None:
            raise TypeError("Address cannot be None")
        if not isinstance(address, int):
            raise TypeError("Address must be an integer")
        if address not in self.address_range:
            raise ValueError(
                f"Address {address} out of range (0 to {self.memory_size - 1})"
            )

    def _access_memory(self, address: int, value: Optional[int] = None) -> int:
        """Memory access function: handles both read and write operations"""
        try:
            # Validate the memory address
            self._validate_address(address)
            # Perform a read operation if no value is provided
            if value is None:
                return self.storage.get(address, 0)
            else:
                # Mask the value to fit word size constraints
                masked_value = value & self.word_mask
                # Store the masked value at the given address
                self.storage[address] = masked_value
                # Return the stored value
                return masked_value
        except (TypeError, ValueError) as e:
            # Handle and log any address validation or type errors
            logger.error(f"Memory access error at address {address}: {e}")
            raise

    def load_word(self, address: int) -> int:
        """word load function"""
        logger.info(f"Loading word from address {address}")
        return self._access_memory(address)

    def store_word(self, address: int, value: int) -> None:
        """Store word function"""
        logger.info(f"Stored {value} at address {address}")
        self._access_memory(address, value)
