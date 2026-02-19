import pytest
from cpu.memory_bus import MemoryBus

# ------------------------------------------------------------------------------
# Address validation tests
# ------------------------------------------------------------------------------


def test_validate_address_valid():
    """Test that valid addresses within range do not raise exceptions."""
    mem = MemoryBus(size=10)
    mem._validate_address(0)
    mem._validate_address(9)


def test_validate_address_type_error():
    """Test that invalid address types raise TypeError."""
    mem = MemoryBus(size=10)

    # None is not a valid address
    with pytest.raises(TypeError):
        mem._validate_address(None)  # type: ignore

    # String is not a valid address
    with pytest.raises(TypeError):
        mem._validate_address("a")  # type: ignore

    # Float is not a valid address
    with pytest.raises(TypeError):
        mem._validate_address(4.5)  # type: ignore


def test_validate_address_value_error():
    """Test that out-of-range addresses raise ValueError."""
    mem = MemoryBus(size=10)

    # Negative address
    with pytest.raises(ValueError):
        mem._validate_address(-1)

    # Address equal to memory size (out of bounds)
    with pytest.raises(ValueError):
        mem._validate_address(10)


# ------------------------------------------------------------------------------
# Store and load word tests
# ------------------------------------------------------------------------------


def test_store_and_load_word():
    """Test storing and loading 32-bit words at valid addresses."""
    mem = MemoryBus(size=16)  # 16 bytes = 4 words

    # Store a word at address 0
    mem.store_word(0, 0x12345678)
    assert mem.load_word(0) == 0x12345678

    # Store another word at address 4
    mem.store_word(4, 0xDEADBEEF)
    assert mem.load_word(4) == 0xDEADBEEF


def test_store_word_out_of_bounds():
    """Test that storing a word at an out-of-bounds address raises ValueError."""
    mem = MemoryBus(size=8)  # Only 2 words

    with pytest.raises(ValueError):
        mem.store_word(8, 0xCAFEBABE)  # Address too high


def test_load_word_out_of_bounds():
    """Test that loading a word from an out-of-bounds address raises ValueError."""
    mem = MemoryBus(size=8)

    with pytest.raises(ValueError):
        mem.load_word(8)  # Address too high


def test_store_word_type_error():
    """Test that invalid types for address or value raise TypeError."""
    mem = MemoryBus(size=8)

    # Address must be an integer
    with pytest.raises(TypeError):
        mem.store_word("0", 0x12345678)  # type: ignore

    # Value must be an integer
    with pytest.raises(TypeError):
        mem.store_word(0, "value")  # type: ignore


def test_load_word_type_error():
    """Test that invalid address types raise TypeError when loading."""
    mem = MemoryBus(size=8)

    # Address must be an integer
    with pytest.raises(TypeError):
        mem.load_word(None)  # type: ignore


def test_store_word_address_too_low():
    """Test that storing a word at a negative address raises ValueError."""
    mem = MemoryBus(size=16)

    with pytest.raises(ValueError):
        mem.store_word(-4, 0x12345678)


def test_load_word_address_too_low():
    """Test that loading a word from a negative address raises ValueError."""
    mem = MemoryBus(size=16)

    with pytest.raises(ValueError):
        mem.load_word(-4)
