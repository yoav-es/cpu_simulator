import pytest
import tempfile
import os
from cpu.cpu import CPU
from cpu.memory_bus import MemoryBus
from utils.constants import INT16_MAX


# -------------------------------------------------------------------------------
# _load_file_lines tests
# -------------------------------------------------------------------------------
def test_load_file_lines_valid():
    """Should return stripped lines from a valid file."""   
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write("line1\nline2\nline3\n")
        f.flush()
        lines = CPU._load_file_lines(f.name)
    assert lines == ["line1", "line2", "line3"]
    os.remove(f.name)

def test_load_file_lines_missing_file():
    with pytest.raises(FileNotFoundError):
        CPU._load_file_lines("nonexistent_file.txt")


# -------------------------------------------------------------------------------
# _load_instruction tests
# -------------------------------------------------------------------------------
def test_load_instruction_valid_file(tmp_path):
    cpu = CPU()
    instruction_file = tmp_path / "instructions.txt"
    instruction_file.write_text("LOAD,R1,100\nADD,R1,R2\n")

    cpu._load_instructions(str(instruction_file))

    assert cpu.load_instructions == [
        ["LOAD", "R1", "100"],
        ["ADD", "R1", "R2"]
    ]


def test_load_instruction_missing_file():
    cpu = CPU()
    with pytest.raises(FileNotFoundError):
        cpu._load_instructions("nonexistent_instructions.txt")

# -------------------------------------------------------------------------------
# _load_instruction tests
# -------------------------------------------------------------------------------
def test_load_memory_valid_file(tmp_path):
    cpu = CPU()
    memory_file = tmp_path / "memory.txt"
    memory_file.write_text("00000001,42\n00000010,99\n")

    cpu._load_memory(str(memory_file))

    assert cpu.memory.load_word(0b00000001) == 42
    assert cpu.memory.load_word(0b00000010) == 99


def test_load_memory_missing_file():
    cpu = CPU()
    with pytest.raises(FileNotFoundError):
        cpu._load_memory("nonexistent_memory.txt")

#-------------------------------validation

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
        mem._validate_address('a')  # type: ignore

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

# -------------------------------------------------------------------------------
# Offset Validation_tests
# -------------------------------------------------------------------------------

def test_validate_offset_valid():
    CPU._validate_offset(16, 4)  # Should not raise

def test_validate_offset_non_integer():
    with pytest.raises(TypeError):
        CPU._validate_offset("8", 4) # type: ignore

def test_validate_offset_invalid_word_size():
    with pytest.raises(ValueError):
        CPU._validate_offset(8, 0)

def test_validate_offset_not_multiple_of_word_size():
    with pytest.raises(Exception):
        CPU._validate_offset(10, 4)

def test_validate_offset_out_of_range():
    with pytest.raises(Exception):
        CPU._validate_offset(INT16_MAX + 1, 4)

# ------------------------------------------------------------------------------
# Register Validation tests
# ------------------------------------------------------------------------------

def test_valid_registers_allows_r0_when_flag_set():
    assert CPU._valid_registers(0, 5, allow_r0=True) is True

def test_valid_registers_rejects_r0_by_default():
    assert CPU._valid_registers(0, 5) is False

# -------------------------------------------------------------------------------
# _validate_immediate_value tests
# -------------------------------------------------------------------------------

def test_validate_immediate_value_valid():
    assert CPU._validate_immediate_value("42") == 42

def test_validate_immediate_value_negative():
    assert CPU._validate_immediate_value("-100") == -100

def test_validate_immediate_value_empty_string():
    with pytest.raises(ValueError):
        CPU._validate_immediate_value("")

def test_validate_immediate_value_non_string():
    with pytest.raises(ValueError):
        CPU._validate_immediate_value(42) # type: ignore

def test_validate_immediate_value_not_integer():
    with pytest.raises(ValueError):
        CPU._validate_immediate_value("abc")

def test_validate_immediate_value_out_of_range():
    with pytest.raises(ValueError):
        CPU._validate_immediate_value(str(2**31))

# -------------------------------------------------------------------------------
# _validate_instructions tests
# -------------------------------------------------------------------------------

def test_validate_instructions_valid(caplog):
    cpu = CPU()
    cpu.instruction_set = {"LOAD": {"args": 2}, "ADD": {"args": 2}}
    cpu.load_instructions = [["LOAD", "R1", "100"], ["ADD", "R1", "R2"]]

    with caplog.at_level("INFO"):
        cpu._validate_instructions()
        assert "Validated LOAD with args: ['R1', '100']" in caplog.text
        assert "Validated ADD with args: ['R1', 'R2']" in caplog.text

def test_validate_instructions_unknown_opcode(caplog):
    cpu = CPU()
    cpu.instruction_set = {"LOAD": {"args": 2}}
    cpu.load_instructions = [["FOO", "R1", "100"]]

    with caplog.at_level("WARNING"):
        cpu._validate_instructions()
        assert "Unknown instruction: FOO" in caplog.text

def test_validate_instructions_wrong_arg_count(caplog):
    cpu = CPU()
    cpu.instruction_set = {"LOAD": {"args": 2}}
    cpu.load_instructions = [["LOAD", "R1"]]

    with caplog.at_level("WARNING"):
        cpu._validate_instructions()
        assert "Incorrect number of arguments for LOAD" in caplog.text

# -------------------------------------------------------------------------------
# _parse_args tests
# -------------------------------------------------------------------------------

def test_parse_args_with_registers_only():
    args = ["R1", "R2", "R3"]
    result = CPU._parse_args(args)
    assert result == (1, 2, 3)

def test_parse_args_with_immediate_value():
    args = ["R1", "R2", "42"]
    result = CPU._parse_args(args, imm=True)
    assert result == (1, 2, 42)

def test_parse_args_with_negative_immediate():
    args = ["R1", "R2", "-100"]
    result = CPU._parse_args(args, imm=True)
    assert result == (1, 2, -100)

def test_parse_args_invalid_immediate_string():
    args = ["R1", "R2", "abc"]
    with pytest.raises(ValueError):
        CPU._parse_args(args, imm=True)
