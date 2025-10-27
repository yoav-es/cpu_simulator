from cpu.cache import Cache, Block
from cpu.memory_bus import MemoryBus
from utils.constants import MEMORY_SIZE, WORD_SIZE, BLOCK_SIZE

# -------------------------------------------------------------------------------
# Cache flush test
# -------------------------------------------------------------------------------

def test_flush_writes_back_dirty_blocks_and_clears_dirty_flag():
    cache = Cache()
    memory = MemoryBus(size=MEMORY_SIZE)

    # Populate cache with dirty blocks and save expected data
    expected_data = []
    for index in range(len(cache.blocks)):
        block = Block(tag=index)
        block.valid = True
        block.dirty = True
        block.data = [index * 100 + i for i in range(cache.block_size)]
        expected_data.append(block.data[:])  # Save a copy
        cache.blocks[index] = block

    # Flush cache
    cache.flush(memory)

    # Verify memory contents and dirty flags
    for index, block in enumerate(cache.blocks):
        base_address = (block.tag << 11) | (index << 6)
        for offset, expected in enumerate(expected_data[index]):
            addr = base_address + offset * WORD_SIZE
            actual = memory.storage[addr]
            assert actual == expected, f"Memory at {addr} = {actual}, expected {expected}"
        assert block.dirty is False



# -------------------------------------------------------------------------------
# Cache replacement test
# -------------------------------------------------------------------------------

def test_replace_block_writes_back_and_loads_new_data():
    """Replacing a block should write back dirty data and load new block from memory."""
    cache = Cache()
    memory = MemoryBus(size=MEMORY_SIZE)

    index = 0
    tag_old = 1
    tag_new = 2

    # Setup old block in cache
    old_block = Block(tag=tag_old)
    old_block.valid = True
    old_block.dirty = True
    old_block.data = [10 * (i + 1) for i in range(BLOCK_SIZE)]
    cache.blocks[index] = old_block

    # Replace with new block
    new_base = (tag_new << 11) | (index << 6)
    for i in range(BLOCK_SIZE):
        memory.store_word(new_base + i * WORD_SIZE, 1000 + i)

    new_block = cache.replace_block(tag_new, index, memory)

    # Verify old block was written back
    old_base = (tag_old << 11) | (index << 6)
    for i in range(BLOCK_SIZE):
        addr = old_base + i * WORD_SIZE
        assert memory.storage[addr] == old_block.data[i]

    # Verify new block was loaded
    for i in range(BLOCK_SIZE):
        assert new_block.data[i] == 1000 + i
    assert new_block.valid is True
    assert new_block.tag == tag_new

# -------------------------------------------------------------------------------
# Cache read/write tests
# -------------------------------------------------------------------------------

def test_cache_write_and_read():
    """Writing to cache should store data and mark block dirty; reading should return correct value."""
    cache = Cache()
    memory = MemoryBus(size=MEMORY_SIZE)

    address = (3 << 11) | (2 << 6) | 4  # tag=3, index=2, offset=4
    value = 0xABCDEF

    # Write to cache
    cache.write(address, value, memory)

    # Read back
    result = cache.read(address, memory)
    assert result == [value]

    # Verify block is dirty
    tag, index, offset = cache.decode_address(address)
    block = cache.blocks[index]
    assert block.dirty is True
    assert block.data[offset] == value