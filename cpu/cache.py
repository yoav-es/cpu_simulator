#imports
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
        self.data = data if data is not None else [0] * BLOCK_SIZE  # 8-word block

# class cache
class Cache:
    """Cache class"""
    def __init__(self) -> None:
        """Initializing block vairables"""
        logger.info("Initializing Cache")
        self.word_size = WORD_SIZE
        self.cache_size = CACHE_SIZE
        self.block_size = BLOCK_SIZE  # 8 words per block
        self.cache_lines = self.cache_size // (self.block_size * self.word_size)
        self.address_size = int(math.log2(MEMORY_SIZE))
        self.blocks = [Block() for _ in range(self.cache_lines)]
        logger.info(f"Cache initialized with {self.cache_lines} lines")
        logger.info(f"Word Size: {self.word_size}, Cache Size: {self.cache_size}, Block Size: {self.block_size}")

    def _write_back(self, block: Block, base_address: int, memory: MemoryBus) -> None:
        """writing values back to memory, to prevent data loss"""
        for i in range(self.block_size):
            memory.store_word(base_address + i * self.word_size, block.data[i])

    def decode_address(self, address: int) -> tuple[int, int, int]:
        """decode address from int to binary"""
        offset_mask = self.block_size - 1
        index_mask = self.cache_lines - 1
        offset = address & offset_mask
        index = (address >> 3) & index_mask
        tag = address >> BLOCK_SIZE
        return tag, index, offset

    def hit_or_miss(self, block: Block, tag: int) -> bool:
        """Detect cache hit or miss"""
        return block.valid and block.tag == tag

    def read(self, address: int, memory: MemoryBus) -> list[int]:
        """read value from memory by address"""
        tag, index, offset = self.decode_address(address)
        block = self.blocks[index]
        if self.hit_or_miss(block, tag):
            logger.info(f"Cache hit on read at address {address}")
            return block.data[offset:offset + 1]
        logger.info(f"Cache miss on read at address {address}")
        block = self.replace_block(tag, index, memory)
        return block.data[offset:offset + 1]

    def write(self, address: int, value: int, memory: MemoryBus) -> None:
        """write value into memory by address"""
        tag, index, offset = self.decode_address(address)
        block = self.blocks[index]

        if self.hit_or_miss(block, tag):
            # cache hit
            logger.info(f"Cache hit on write at address {address}")
            block.data[offset] = value
            block.dirty = True
        else:
            #cache miss
            logger.info(f"Cache miss on write at address {address}")
            block = self.replace_block(tag, index, memory)
            block.data[offset] = value
            # mark as dirty - data written to it
            block.dirty = True
            logger.info(f"Value written to cache after block replacement")


    def replace_block(self, tag: int, index: int, memory: MemoryBus) -> Block:
        """Block Replacement algorithm"""
        #Identify block to be replaced 
        old_block = self.blocks[index]
        old_base = (old_block.tag << 8) | (index << 3)

        #Write back old block to memory if it's valid and dirty
        if old_block.valid and old_block.dirty:
            self._write_back(old_block, old_base, memory)

        # get new block address
        new_base = (tag << 8) | (index << 3) # calculate new address 
        new_block = Block(tag=tag) #create new block 

        #load values from memory into new block
        for i in range(self.block_size):
            new_block.data[i] = memory.load_word(new_base + i * self.word_size)
        new_block.valid = True
        self.blocks[index] = new_block
        return new_block
    
    def flush(self, memory: MemoryBus) -> None:
        """Cache Flush function"""
        logger.info("Flushing cache to memory")
        for index, block in enumerate(self.blocks):
            #Calculate the memory base address for the current block
            base_address = (block.tag << 8) | (index << 3)
            #Check if the block needs to be written back
            if block.valid and block.dirty:
                #write block's data back to memory bus
                self._write_back(block, base_address, memory)
                # mark block as clean - ready to use again
                block.dirty = False
        logger.info("Cache flush complete")
