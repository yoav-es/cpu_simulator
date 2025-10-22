import math
import logging
from typing import Optional
from cpu.memory_bus import MemoryBus
from utils.constants import WORD_SIZE, CACHE_SIZE, MEMORY_SIZE
logger = logging.getLogger(__name__)
logger.info("CPU initialized")

class Block:
    def __init__(self, tag: int = 0, data: Optional[list[int]] = None) -> None:
        self.tag = tag
        self.valid = False
        self.dirty = False
        self.data = data if data is not None else [0] * 8  # 8-word block

# class cache
class Cache:
    def __init__(self) -> None:
        logger.info("Initializing Cache")
        self.word_size = 4  # 4 bytes per word
        self.cache_size = 1024  # 1 KB cache size
        self.block_size = 8  # 8 words per block
        self.cache_lines = self.cache_size // (self.block_size * self.word_size)
        self.address_size = int(math.log2(MEMORY_SIZE))
        self.blocks = [Block() for _ in range(self.cache_lines)]        
        logger.info(f"Cache initialized with {self.cache_lines} lines")
        logger.info(f"Cache parameters - Word Size: {self.word_size} bytes, Cache Size: {self.cache_size} bytes, Block Size: {self.block_size} words")

    def decode_address(self, address: int) -> tuple[int, int, int]:
        offset = address & 0b111
        index = (address >> 3) & 0b11111
        tag = address >> 8
        return tag, index, offset

    def hit_or_miss(self, block: Block, tag: int) -> bool:
        return block.valid and block.tag == tag

    def read(self, address: int, memory: MemoryBus) -> Optional[list[int]]:
        tag, index, offset = self.decode_address(address)
        block = self.blocks[index]
        if self.hit_or_miss(block, tag):
            logger.info(f"Reading from cache for address {address}")
            return block.data[offset:offset+1]
        logger.info(f"Cache miss on read for address {address}")
        # implement block fetch from memory
        new_block = self.replace_block(tag, index, memory)
        return new_block.data[offset:offset+1]

    def write(self, address: int, value: int, memory: MemoryBus) -> None:
        tag, index, offset = self.decode_address(address)
        block = self.blocks[index]
        if self.hit_or_miss(block, tag):
            logger.info(f"Writing to cache for address {address}")
            block.data[offset] = value
            block.dirty = True
            return
            # Update cache block data
        logger.info(f"Cache miss on write to address {address}")
        # call block replacement policy 
        logger.info(f"Evicting block and fetching new block for address {address}")
        new_block = self.replace_block(tag, index, memory)
        new_block.data[offset] = value
        block.dirty = True
        logger.info(f"Writing to cache for address {address}")


    def replace_block(self, tag: int, index: int, memory: MemoryBus) -> Block:
        block = self.blocks[index]
        # calcuate base address of block in memory
        base_address = (block.tag << 8) | (index << 3)
        if block.valid and block.dirty:
            # Write back data to memory
            for i in range(self.block_size):
                memory.store_word(base_address + i * 4, block.data[i])
        # calculate base address for new block
        base_address = (tag << 8) | (index << 3)
        # Create new block 
        new_block = Block(tag=tag)
        # load data from memory into new block
        for i in range(self.block_size):
            word = memory.load_word(base_address + i * 4)
            new_block.data[i] = word
        new_block.valid = True
        # evict old block and replace with new block
        self.blocks[index] = new_block
        return new_block
    
    def flush(self, memory: MemoryBus) -> None:
        logger.info("flushing cache to memory")
        for index, block in enumerate(self.blocks):
            base_address = (block.tag << 8) | (index << 3)
            if block.valid and block.dirty:
                for i in range(self.block_size):
                    memory.store_word(base_address + i * 4, block.data[i])
                block.dirty = False
        logger.info("Cache flush complete")
