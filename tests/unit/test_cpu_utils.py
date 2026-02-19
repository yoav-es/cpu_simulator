import os
import tempfile

import pytest

from cpu.cpu import CPU
from utils.constants import INT16_MAX


# -------------------------------------------------------------------------------
# _load_file_lines tests
# -------------------------------------------------------------------------------
def test_load_file_lines_valid():
    """Should return stripped lines from a valid file."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
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

    assert cpu.load_instructions == [["LOAD", "R1", "100"], ["ADD", "R1", "R2"]]


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


# -------------------------------------------------------------------------------
# Offset Validation tests
# -------------------------------------------------------------------------------


def test_validate_offset_valid():
    CPU._validate_offset(16, 4)  # Should not raise


def test_validate_offset_non_integer():
    with pytest.raises(TypeError):
        CPU._validate_offset("8", 4)  # type: ignore


def test_validate_offset_invalid_word_size():
    with pytest.raises(ValueError):
        CPU._validate_offset(8, 0)


def test_validate_offset_not_multiple_of_word_size():
    with pytest.raises(ValueError):
        CPU._validate_offset(10, 4)


def test_validate_offset_out_of_range():
    with pytest.raises(ValueError):
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
        CPU._validate_immediate_value(42)  # type: ignore


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
