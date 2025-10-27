"""
Unit tests for the CPU class.

These tests verify:
- Arithmetic instruction execution
- Branching logic
- Faulty opcode handling
"""

from cpu.cpu import CPU
from utils.constants import WORD_SIZE


def test_valid_arithmetic_program():
    """Test a valid arithmetic program with expected register and memory values."""
    cpu = CPU()
    cpu._load_instructions('files/valid_arithmetic.txt')
    cpu._load_memory('files/valid_arithmetic_data.txt')
    cpu.execute_instructions()

    assert cpu.registers[3] == 15
    assert cpu.memory[0] == 15
    assert cpu.halted is True


def test_valid_branching_program():
    """Test a valid branching program where a branch should not be taken."""
    cpu = CPU()
    cpu._load_instructions('files/valid_branching.txt')
    cpu._load_memory('files/valid_branching_data.txt')
    cpu.execute_instructions()

    assert cpu.registers[3] == 0  # R3 should not be set
    assert cpu.halted is True


def test_faulty_opcode_program():
    """Test a program with an invalid opcode that should halt early."""
    cpu = CPU()
    cpu._load_instructions('files/faulty_opcode.txt')
    cpu._load_memory('files/faulty_opcode_data.txt')
    cpu.execute_instructions()

    assert cpu.registers[1] == 7
    assert cpu.registers[3] == 0  # R3 should not be set
    assert cpu.halted is True
    assert cpu.pc == WORD_SIZE  # Halted after first instruction


def test_example_program_execution():
    cpu = CPU()
    cpu._load_instructions('files/instruction_input.txt')
    cpu._load_memory('files/data_input.txt')
    cpu._validate_instructions()
    cpu.execute_instructions()

    assert cpu.halted is True
    assert cpu.registers[2] == 2  # R2 was incremented by 2
    assert cpu.registers[3] == cpu.registers[2] + cpu.registers[1]



def test_extended_program_execution():
    cpu = CPU()
    cpu._load_instructions('files/extended_program.txt')
    cpu._load_memory('files/extended_data.txt')
    cpu.execute_instructions()

    # Validate final register and memory state
    assert cpu.halted is True
    assert cpu.memory[8] == cpu.registers[3]
    assert cpu.memory[12] == cpu.registers[4]
    assert cpu.registers[6] == cpu.memory[4] + cpu.registers[3]  # Final ADD
