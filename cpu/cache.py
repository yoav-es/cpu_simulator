# imports
import math
import logging
from typing import Optional
from cpu.memory_bus import MemoryBus
from utils.constants import WORD_SIZE, CACHE_SIZE, MEMORY_SIZE, BLOCK_SIZE

logger = logging.getLogger(__name__)
logger.info("CPU initialized")


class Block:
    """Cache Block class"""

    def __init__(self, tag: int = 0, data: Optional[list[int]] = None) -> None:
        """Initializng block variables"""
        self.tag = tag
        self.valid = False
        self.dirty = False
        self.data = data if data is not None else [0] * BLOCK_SIZE


# class cache
class Cache:
    """Cache class"""

    def __init__(self) -> None:
        """Initializing block vairables"""
        logger.info("Initializing Cache")
        self.word_size = WORD_SIZE
        self.cache_size = CACHE_SIZE
        self.block_size = BLOCK_SIZE
        self.cache_lines = self.cache_size // (self.block_size * self.word_size)
        self.address_size = int(math.log2(MEMORY_SIZE))
        self.blocks = [Block() for _ in range(self.cache_lines)]
        logger.info(f"Cache initialized with {self.cache_lines} lines")
        logger.info(
            "Word Size: %s, Cache Size: %s, Block Size: %s",
            self.word_size,
            self.cache_size,
            self.block_size,
        )

    def _write_back(self, block: Block, base_address: int, memory: MemoryBus) -> None:
        """writing values back to memory, to prevent data loss"""
        for i in range(self.block_size):
            memory.store_word(base_address + i * self.word_size, block.data[i])
        block.dirty = False

    def _get_offset_bits(self) -> int:
        """Return number of bits for block offset."""
        return int(math.log2(self.block_size))

    def _get_index_bits(self) -> int:
        """Return number of bits for cache index."""
        return int(math.log2(self.cache_lines))

    def _block_base_address(self, tag: int, index: int) -> int:
        """Reconstruct block base byte address from tag and index."""
        offset_bits = self._get_offset_bits()
        index_bits = self._get_index_bits()
        word_base = (tag << (offset_bits + index_bits)) | (index << offset_bits)
        return word_base * self.word_size

    def decode_address(self, address: int) -> tuple[int, int, int]:
        """Decode byte address into tag, index, and word offset within block."""
        offset_bits = self._get_offset_bits()
        index_bits = self._get_index_bits()
        word_address = address // self.word_size
        offset_mask = (1 << offset_bits) - 1
        index_mask = (1 << index_bits) - 1
        offset = word_address & offset_mask
        index = (word_address >> offset_bits) & index_mask
        tag = word_address >> (offset_bits + index_bits)
        return tag, index, offset

    @staticmethod
    def hit_or_miss(block: Block, tag: int) -> bool:
        """Detect cache hit or miss"""
        return block.valid and block.tag == tag

    def _access_block(self, address: int, memory: MemoryBus) -> tuple[Block, int]:
        """Decode address and ensure block is present in cache."""
        tag, index, offset = self.decode_address(address)
        block = self.blocks[index]

        if self.hit_or_miss(block, tag):
            logger.info(f"Cache hit at address {address}")
        else:
            logger.info(f"Cache miss at address {address}")
            block = self.replace_block(tag, index, memory)

        return block, offset

    def read(self, address: int, memory: MemoryBus) -> list[int]:
        """Read value from memory by address."""
        block, offset = self._access_block(address, memory)
        return block.data[offset : offset + 1]

    def write(self, address: int, value: int, memory: MemoryBus) -> None:
        """Write value into memory by address."""
        block, offset = self._access_block(address, memory)
        block.data[offset] = value
        block.dirty = True
        logger.info(f"Value written to cache at address {address}")

    def replace_block(self, tag: int, index: int, memory: MemoryBus) -> Block:
        """Replace cache block with new data from memory."""
        old_block = self.blocks[index]
        old_base = self._block_base_address(old_block.tag, index)
        if old_block.valid and old_block.dirty:
            self._write_back(old_block, old_base, memory)
        new_base = self._block_base_address(tag, index)
        new_block = Block(tag=tag)
        for i in range(self.block_size):
            new_block.data[i] = memory.load_word(new_base + i * self.word_size)
        new_block.valid = True
        self.blocks[index] = new_block
        return new_block

    def flush(self, memory: MemoryBus) -> None:
        """Flush dirty cache blocks to memory."""
        logger.info("Flushing cache to memory")
        for index, block in enumerate(self.blocks):
            base_address = self._block_base_address(block.tag, index)
            if block.valid and block.dirty:
                # write block's data back to memory bus
                self._write_back(block, base_address, memory)
                # mark block as clean - ready to use again
                block.dirty = False
                block.valid = False
                block.data = [0] * self.block_size
        logger.info("Cache flush complete")
