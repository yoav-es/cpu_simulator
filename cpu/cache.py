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
        block.dirty = False
        
    def decode_address(self, address: int) -> tuple[int, int, int]:
        # Number of bits for offset = log2(block size)
        offset_bits = int(math.log2(self.block_size))
        
        # Number of bits for index = log2(cache lines)
        index_bits = int(math.log2(self.cache_lines))
        
        # Masks
        offset_mask = (1 << offset_bits) - 1
        index_mask = (1 << index_bits) - 1

        # Extract parts
        offset = address & offset_mask
        index = (address >> offset_bits) & index_mask
        tag = address >> (offset_bits + index_bits)

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
        return block.data[offset:offset + 1]

    def write(self, address: int, value: int, memory: MemoryBus) -> None:
        """Write value into memory by address."""
        block, offset = self._access_block(address, memory)
        block.data[offset] = value
        block.dirty = True
        logger.info(f"Value written to cache at address {address}")

    def replace_block(self, tag: int, index: int, memory: MemoryBus) -> Block:
        """Block Replacement algorithm"""
        #Identify block to be replaced 
        old_block = self.blocks[index]
        old_base = (old_block.tag << 11) | (index << 6)

        #Write back old block to memory if it's valid and dirty
        if old_block.valid and old_block.dirty:
            self._write_back(old_block, old_base, memory)

        # get new block address
        new_base = (tag << 11) | (index << 6) # calculate new address 
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
            base_address = (block.tag << 11) | (index << 6)
            #Check if the block needs to be written back
            if block.valid and block.dirty:
                #write block's data back to memory bus
                self._write_back(block, base_address, memory)
                # mark block as clean - ready to use again
                block.dirty = False
                block.valid = False
                block.data  = [0] * self.block_size
        logger.info("Cache flush complete")
