import pytest
import math
from cpu.cache import Cache, Block
from cpu.memory_bus import MemoryBus
# hit or miss -----------------------------------------------------------------------------------
def test_cache_read_write_basic():
    mem = MemoryBus(size=64)
    cache = Cache()

    # Use address 0 (should be a miss first)
    cache.write(0, 42, mem)
    assert cache.read(0, mem) == [42]

    # Write again to same address (should be a hit)
    cache.write(0, 99, mem)
    assert cache.read(0, mem) == [99]
# decode -----------------------------------------------------------------------------------
def test_decode_address_bit_masks():
    cache = Cache()
    address = 262144

    offset_bits = int(math.log2(cache.block_size))
    index_bits = int(math.log2(cache.cache_lines))
    expected_tag = address >> (offset_bits + index_bits)

    tag, index, offset = cache.decode_address(address)
    assert tag == expected_tag


def test_decode_address_consistency():
    cache = Cache()
    address = 123456  # Arbitrary address

    tag1, index1, offset1 = cache.decode_address(address)
    tag2, index2, offset2 = cache.decode_address(address)

    assert (tag1, index1, offset1) == (tag2, index2, offset2)


def test_decode_address_max_address():
    cache = Cache()
    max_address = 1_048_575  # Last byte in 1MB memory

    tag, index, offset = cache.decode_address(max_address)

    offset_bits = int(math.log2(cache.block_size))
    index_bits = int(math.log2(cache.cache_lines))

    expected_offset = max_address & ((1 << offset_bits) - 1)
    expected_index = (max_address >> offset_bits) & ((1 << index_bits) - 1)
    expected_tag = max_address >> (offset_bits + index_bits)

    assert offset == expected_offset
    assert index == expected_index
    assert tag == expected_tag

#write back ---------------------------------------------------------------------------------------------
def test_write_back_dirty_block():
    mem = MemoryBus(size=64)
    cache = Cache()

    # Simulate a block with data and dirty flag
    address = 0
    tag, index, offset = cache.decode_address(address)
    block = cache.blocks[index]

    block.tag = tag
    block.data[offset] = 77
    block.dirty = True

    # Write back to memory
    cache._write_back(block, index, mem)

    # Confirm memory was updated
    assert mem.load_word(address) & 0xFF == 77
    assert not block.dirty

def test_write_back_only_if_dirty():
    mem = MemoryBus(size=1024)
    cache = Cache()

    address = 0
    tag, index, offset = cache.decode_address(address)
    block = cache.blocks[index]
    block.tag = tag
    block.data[offset] = 123
    block.dirty = True  

    base_address = (index << int(math.log2(cache.block_size))) * cache.word_size
    mem.store_word(base_address + offset * cache.word_size, 0xDEADBEEF)

    cache._write_back(block, base_address, mem)

    # Confirm overwrite
    assert mem.load_word(base_address + offset * cache.word_size) == 123


def test_write_back_multiple_offsets():
    mem = MemoryBus(size=1024)
    cache = Cache()

    base_address = 64
    block = Block()
    block.data = [i + 10 for i in range(cache.block_size)]
    block.dirty = True

    cache._write_back(block, base_address, mem)

    for i in range(cache.block_size):
        addr = base_address + i * cache.word_size
        expected = i + 10
        actual = mem.load_word(addr)
        assert actual == expected, f"At offset {i}, expected {expected}, got {actual}"


def test_write_back_resets_dirty_flag():
    mem = MemoryBus(size=64)
    cache = Cache()

    address = 0
    tag, index, offset = cache.decode_address(address)
    block = cache.blocks[index]

    block.tag = tag
    block.data[offset] = 77
    block.dirty = True

    cache._write_back(block, index, mem)

    assert not block.dirty