import pytest
from cpu.cpu import CPU
from cpu.cache import Cache
from utils.constants import WORD_SIZE
import operator

# -------------------------------------------------------------------------------
# execute_arithmetic tests
# -------------------------------------------------------------------------------

import operator


def test_execute_add():
    cpu = CPU()
    cpu.registers[1] = 10
    cpu.registers[2] = 5
    cpu.execute_arithmetic(["R3", "R1", "R2"], op_func=operator.add, op_name="ADD")
    assert cpu.registers[3] == 15


def test_execute_addi():
    cpu = CPU()
    cpu.registers[1] = 10
    cpu.execute_arithmetic(["R3", "R1", "7"], op_func=operator.add, op_name="ADDI", immediate=True)
    assert cpu.registers[3] == 17


# -------------------------------------------------------------------------------
# execute_slt tests
# -------------------------------------------------------------------------------

def test_execute_slt_true():
    cpu = CPU()
    cpu.registers[1] = 5
    cpu.registers[2] = 10
    cpu.execute_slt(["R3", "R1", "R2"])
    assert cpu.registers[3] == 1


def test_execute_slt_false():
    cpu = CPU()
    cpu.registers[1] = 15
    cpu.registers[2] = 10
    cpu.execute_slt(["R3", "R1", "R2"])
    assert cpu.registers[3] == 0


# -------------------------------------------------------------------------------
# execute_bne tests
# -------------------------------------------------------------------------------

def test_execute_bne_taken():
    cpu = CPU()
    cpu.registers[1] = 5
    cpu.registers[2] = 10
    cpu.pc = 0
    cpu.execute_bne(["R1", "R2", "2"])
    assert cpu.pc == 12  # 0 + 4 + 2*4


def test_execute_bne_not_taken():
    cpu = CPU()
    cpu.registers[1] = 5
    cpu.registers[2] = 5
    cpu.pc = 0
    cpu.execute_bne(["R1", "R2", "2"])
    assert cpu.pc == 0



# -------------------------------------------------------------------------------
# execute_jump tests
# -------------------------------------------------------------------------------

def test_execute_jump():
    cpu = CPU()
    cpu.load_instructions = [["ADD", "R1", "R1", "R1"]] * 10  # valid dummy instructions
    cpu.execute_jump(["2"])
    assert cpu.pc == 8  # 2 * 4


def test_execute_jal():
    cpu = CPU()
    cpu.load_instructions = [["NOP"]] * 10
    cpu.pc = 4
    cpu.execute_jump(["2"], link=True)
    assert cpu.pc == 8  # 2 * WORD_SIZE
    assert cpu.registers[7] == 8  # 4 + WORD_SIZE


def test_execute_jump_to_last_instruction():
    cpu = CPU()
    cpu.load_instructions = [["NOP"]] * 5  # 5 instructions = 20 bytes
    cpu.execute_jump(["4"])  # 4 * 4 = 16, which is the last valid PC
    assert cpu.pc == 16


def test_execute_jump_out_of_bounds():
    cpu = CPU()
    cpu.load_instructions = [["NOP"]] * 5  # 5 instructions = 20 bytes
    with pytest.raises(Exception, match="Jump target out of instruction range"):
        cpu.execute_jump(["5"])  # 5 * 4 = 20, which is just past the end
# -------------------------------------------------------------------------------
# execute_memory_action tests
# -------------------------------------------------------------------------------

def test_execute_lw():
    cpu = CPU()
    cpu.memory.store_word(100, 42)
    cpu.registers[1] = 80
    cpu.execute_memory_action(["R2", "20(R1)"], "LW")
    assert cpu.registers[2] == 42


def test_execute_sw():
    cpu = CPU()
    cpu.registers[1] = 80
    cpu.registers[2] = 99
    cpu.execute_memory_action(["R2", "20(R1)"], "SW")
    assert cpu.memory.load_word(100) == 99

def test_execute_lw_misaligned_offset():
    cpu = CPU()
    cpu.registers[1] = 100
    cpu.memory.store_word(104, 42)  # valid address
    with pytest.raises(Exception, match="Invalid offset"):
        cpu.execute_memory_action(["R2", "3(R1)"], "LW")  # offset = 3 (not divisible by WORD_SIZE)

def test_execute_sw_valid():
    cpu = CPU()
    cpu.registers[1] = 200
    cpu.registers[2] = 99
    cpu.execute_memory_action(["R2", "4(R1)"], "SW")  # address = 204
    assert cpu.memory.load_word(204) == 99

# -------------------------------------------------------------------------------
# execute_cache tests
# -------------------------------------------------------------------------------

def test_execute_cache_disable():
    cpu = CPU()
    cpu.cache = Cache()
    cpu.execute_cache("0")
    assert cpu.cache is None


def test_execute_cache_enable():
    cpu = CPU()
    cpu.cache = None
    cpu.execute_cache("1")
    assert isinstance(cpu.cache, Cache)


def test_execute_cache_flush():
    cpu = CPU()
    cpu.cache = Cache()

    # Simulate dirty cache blocks
    for block in cpu.cache.blocks:
        block.valid = True
        block.dirty = True  # ← Add this line
        block.data = [1] * cpu.cache.block_size

    cpu.execute_cache("2")  # Flush

    # Assert all blocks are invalid and cleared
    for block in cpu.cache.blocks:
        assert not block.valid
        assert block.data == [0] * cpu.cache.block_size
        assert not block.dirty


# -------------------------------------------------------------------------------
# Dispatcher tests
# -------------------------------------------------------------------------------

def test_dispatch_add(monkeypatch):
    cpu = CPU()

    def mock_execute_arithmetic(args, op, opcode, immediate=False):
        assert args == ['R1', 'R2', 'R3']
        assert opcode == 'ADD'
        assert not immediate

    monkeypatch.setattr(cpu, 'execute_arithmetic', mock_execute_arithmetic)
    cpu.dispatch_instruction('ADD', ['R1', 'R2', 'R3'])


def test_dispatch_addi(monkeypatch):
    cpu = CPU()

    def mock_execute_arithmetic(args, op, opcode, immediate=False):
        assert args == ['R1', 'R2', '10']
        assert opcode == 'ADDI'
        assert immediate

    monkeypatch.setattr(cpu, 'execute_arithmetic', mock_execute_arithmetic)
    cpu.dispatch_instruction('ADDI', ['R1', 'R2', '10'])


def test_dispatch_sub(monkeypatch):
    cpu = CPU()

    def mock_execute_arithmetic(args, op, opcode, immediate=False):
        assert args == ['R1', 'R2', 'R3']
        assert opcode == 'SUB'
        assert not immediate

    monkeypatch.setattr(cpu, 'execute_arithmetic', mock_execute_arithmetic)
    cpu.dispatch_instruction('SUB', ['R1', 'R2', 'R3'])


def test_dispatch_subi(monkeypatch):
    cpu = CPU()

    def mock_execute_arithmetic(args, op, opcode, immediate=False):
        assert args == ['R1', 'R2', '10']
        assert opcode == 'SUBI'
        assert immediate

    monkeypatch.setattr(cpu, 'execute_arithmetic', mock_execute_arithmetic)
    cpu.dispatch_instruction('SUBI', ['R1', 'R2', '10'])


def test_dispatch_slt(monkeypatch):
    cpu = CPU()

    def mock_execute_slt(args):
        assert args == ['R1', 'R2', 'R3']

    monkeypatch.setattr(cpu, 'execute_slt', mock_execute_slt)
    cpu.dispatch_instruction('SLT', ['R1', 'R2', 'R3'])


def test_dispatch_bne(monkeypatch):
    cpu = CPU()

    def mock_execute_bne(args):
        assert args == ['R1', 'R2', 'label']

    monkeypatch.setattr(cpu, 'execute_bne', mock_execute_bne)
    cpu.dispatch_instruction('BNE', ['R1', 'R2', 'label'])


def test_dispatch_jump(monkeypatch):
    cpu = CPU()

    def mock_execute_jump(args, link=False):
        assert args == ['label']
        assert not link

    monkeypatch.setattr(cpu, 'execute_jump', mock_execute_jump)
    cpu.dispatch_instruction('J', ['label'])


def test_dispatch_jal(monkeypatch):
    cpu = CPU()

    def mock_execute_jump(args, link=False):
        assert args == ['label']
        assert link

    monkeypatch.setattr(cpu, 'execute_jump', mock_execute_jump)
    cpu.dispatch_instruction('JAL', ['label'])


def test_dispatch_lw(monkeypatch):
    cpu = CPU()

    def mock_execute_memory_action(args, opcode):
        assert args == ['R1', '0(R2)']
        assert opcode == 'LW'

    monkeypatch.setattr(cpu, 'execute_memory_action', mock_execute_memory_action)
    cpu.dispatch_instruction('LW', ['R1', '0(R2)'])


def test_dispatch_sw(monkeypatch):
    cpu = CPU()

    def mock_execute_memory_action(args, opcode):
        assert args == ['R1', '0(R2)']
        assert opcode == 'SW'

    monkeypatch.setattr(cpu, 'execute_memory_action', mock_execute_memory_action)
    cpu.dispatch_instruction('SW', ['R1', '0(R2)'])


def test_dispatch_cache(monkeypatch):
    cpu = CPU()

    def mock_execute_cache(arg):
        assert arg == '2'

    monkeypatch.setattr(cpu, 'execute_cache', mock_execute_cache)
    cpu.dispatch_instruction('CACHE', ['2'])


def test_dispatch_halt():
    cpu = CPU()
    cpu.dispatch_instruction('HALT', [])
    assert cpu.halted is True


def test_dispatch_nop():
    cpu = CPU()
    cpu.halted = False
    cpu.dispatch_instruction('NOP', [])
    assert cpu.halted is False

# -------------------------------------------------------------------------------
# Instruction Execution tests
# -------------------------------------------------------------------------------

def test_execute_instructions_add_and_halt():
    cpu = CPU()

    # Load a simple program: ADD R1, R2, R3 followed by HALT
    cpu.load_instructions = [
        ['ADD', 'R1', 'R2', 'R3'],
        ['HALT']
    ]

    # Set initial register values
    cpu.registers[2] = 5  # R2
    cpu.registers[3] = 10  # R3

    # Execute the program
    cpu.execute_instructions()

    # Check results
    assert cpu.registers[1] == 15  # R1 = R2 + R3
    assert cpu.halted is True
    assert cpu.pc == WORD_SIZE * 2  # Advanced past both instructions
    assert cpu.registers[0] == 0  # R0 must remain zero



def test_execute_instructions_with_error():
    cpu = CPU()

    # Load a program with a valid instruction followed by an invalid one
    cpu.load_instructions = [
        ['ADD', 'R1', 'R2', 'R3'],
        ['INVALID_OP', 'R1', 'R2']
    ]

    # Set initial register values
    cpu.registers[2] = 5
    cpu.registers[3] = 10

    # Execute the program
    cpu.execute_instructions()

    # Check that the first instruction executed correctly
    assert cpu.registers[1] == 15

    # Check that the CPU halted after the error
    assert cpu.halted is True

    # Check that PC did not advance past the faulty instruction
    assert cpu.pc == WORD_SIZE  # Only one instruction executed