import sys
from .memory_bus import MemoryBus
from .cache import Cache
from utils.constants import WORD_SIZE, BUS_LENGTH, INT16_MIN, INT16_MAX
import logging
import operator
logger = logging.getLogger(__name__)
logger.info("CPU initialized")

# CPU Simulator Class
class CPU:
    # Initialize CPU with registers, program counter, instruction set, memory bus, and cache
    def __init__(self) -> None:
        logger.info("Initializing CPU Simulator")
        self.registers = [0] * BUS_LENGTH
        self.pc = 0  # Program counter
        self.load_instructions = []
        self.cache = None
        self.memory = MemoryBus()
        self.halted = False
        # Define instruction set with expected argument counts
        self.instruction_set = {
            "ADD": {"args": 3},
            "ADDI": {"args": 3},
            "SUB": {"args": 3},
            "SUBI": {"args": 3},
            "SLT": {"args": 3},
            "BNE": {"args": 3},
            "J": {"args": 1},
            "JAL": {"args": 1},
            "LW": {"args": 2},
            "SW": {"args": 2},
            "CACHE": {"args": 1},
            "HALT": {"args": 1}
        }
    # load file and return lines for processing
    @staticmethod
    def _load_file_lines(filepath):
        logger.info(f"Loading file: {filepath}")
        with open(filepath, 'r') as file:
            return [line.strip() for line in file.readlines()]
    
    # Validate register indices
    @staticmethod
    def _valid_registers(*indices: int, allow_r0: bool = False) -> bool:
        return all(isinstance(idx, int) and 0 <= idx < BUS_LENGTH for idx in indices) and (allow_r0 or 0 not in indices)

    @staticmethod
    def validate_offset(offset: int, word_size: int) -> None:
        if not isinstance(offset, int):
            raise TypeError(f"Offset must be an integer, got {type(offset).__name__}")
        if word_size <= 0:
            raise ValueError(f"Word size must be positive, got {word_size}")
        if offset % word_size != 0 or not (INT16_MIN <= offset <= INT16_MAX):
            raise Exception(f"Invalid offset: {offset}")
        

    @staticmethod
    def _parse_args(args: list[str], imm: bool = False) -> tuple[int, int, int]:
        arg1 = int(args[0][1:])
        arg2 = int(args[1][1:])
        arg3 = CPU.validate_immediate_value(args[2][1:]) if imm else int(args[2][1:])
        return arg1, arg2, arg3


    @staticmethod
    def validate_immediate_value(value: str) -> int:
        """Validate a binary immediate string and return its signed integer value."""
        if not isinstance(value, str) or not value:
            raise ValueError("Immediate must be a non-empty binary string")
        if not all(c in '01' for c in value):
            raise ValueError(f"Immediate value is not a valid binary string: {value}")
        
        bits = len(value)
        if bits > BUS_LENGTH:
            raise ValueError(f"Immediate width greater than {BUS_LENGTH} bits not supported")
        
        unsigned = int(value, 2)
        sign_bit = 1 << (bits - 1)
        
        # Convert from two's complement to signed int
        signed = unsigned - (1 << bits) if unsigned & sign_bit else unsigned
        
        if not (-(2**31) <= signed <= (2**31 - 1)):
            raise ValueError(f"Immediate value out of {BUS_LENGTH}-bit signed range: {signed}")        
        return signed


    # Load instructions from file
    def load_instruction(self, instructions_file):
        if not instructions_file:
            logger.error("No instruction file provided.")
            sys.exit(1)
        logger.info("loading instructions")
        for line in self._load_file_lines(instructions_file):
            self.load_instructions.append(line.split(','))
    
    # Load memory initialization values from file
    def load_memory(self, data_file):
        if not data_file:
            logger.error("No data file provided.")
            sys.exit(1)
        logger.info("loading memory initialization values")
        try:
            for line in self._load_file_lines(data_file):
                entry = line.split(',')
                self.memory.store_word(int(entry[0],2), int(entry[1]))
                logger.info(f"Loaded memory initialization value: Address {entry[0]} Data {entry[1]}")
        except Exception as e:
            logger.error(f"Error loading memory initialization values: {e}")
            sys.exit(1)
        logger.info("Finished loading memory initialization values.")

    def validate_instructions(self) -> None:
        logger.info("Validating instructions")
        for instruction in self.load_instructions:
            opcode = instruction[0]
            args = instruction[1:]
            if opcode not in self.instruction_set:
                logger.warning(f"Unknown instruction: {opcode}")
                continue
            expected_arg_count = self.instruction_set[opcode]["args"]
            if len(args) != expected_arg_count:
                logger.warning(f"Incorrect number of arguments for {opcode}. Expected {expected_arg_count}, got {len(args)}")
                continue
            logger.info(f"Validated {opcode} with args: {args}")

    def execute_instructions(self) -> None:
        logger.info("Starting instruction execution")
        while not self.halted and self.pc < len(self.load_instructions):
            current_pc = self.pc
            opcode, *args = self.load_instructions[self.pc // WORD_SIZE]
            try:
                logger.info(f"Executing {opcode} with args: {args}")
                self.execute_instruction(opcode, args)
                # Ensure R0 is always zero
                self.registers[0] = 0
                if self.pc == current_pc:
                    self.pc += WORD_SIZE
            except Exception as e:
                logger.error(f"Error executing instruction at PC {self.pc}: {e}")
                self.halted = True
        logger.info("Finished instruction execution.")


    # # Execute arithmetic instruction (ADD, ADDI, SUB, SUBI)
    def execute_arithmetic(self, args: list[str], op_func, op_name: str, immediate: bool = False) -> None:
        if immediate:
            dest_idx, src_idx, value = self._parse_args(args, imm=True)
        else:
            dest_idx, src_idx, rt_idx = self._parse_args(args)
            value = self.registers[rt_idx]

        if not self._valid_registers(src_idx, dest_idx):
            raise Exception(f"Invalid register index: src={src_idx}, dest={dest_idx}")

        self.registers[dest_idx] = op_func(self.registers[src_idx], value)


    def execute_slt(self, args: list[str]) -> None:
        logger.info("Executing SLT instruction")
        dest_idx, src_idx, rt_idx = self._parse_args(args)

        if not self._valid_registers(src_idx, rt_idx, dest_idx):
            raise Exception(f"Invalid register index: src={src_idx}, rt={rt_idx}, dest={dest_idx}")

        self.registers[dest_idx] = int(self.registers[src_idx] < self.registers[rt_idx])
        logger.info(f"SLT executed: R{dest_idx} = (R{src_idx} < R{rt_idx}) → {self.registers[dest_idx]}")

    # Execute branch not equal instruction
    def execute_bne(self, args: list[str]) -> None:
        logger.info("Executing BNE instruction")
        rs_idx, rt_idx, offset = self._parse_args(args)
        if not self._valid_registers(rs_idx, rt_idx):
            raise Exception(f"Invalid register index: src={rs_idx}, rt={rt_idx}")
        self.validate_offset(offset, WORD_SIZE)
        if self.registers[rs_idx] != self.registers[rt_idx]:
            self.pc = self.pc + WORD_SIZE + offset * WORD_SIZE
            logger.info(f"BNE taken: PC updated to {self.pc}")

    # Execute jump instruction
    def execute_jump(self, args: list[str], link: bool = False) -> None:
        target = args[0]
        if not target.isdigit():
            raise Exception("Jump target must be a number")

        target_idx = int(target)
        if not (0 <= target_idx < len(self.load_instructions)):
            raise Exception("Jump target out of instruction range")
        # Handle JAL instruction
        if link:
            self.registers[7] = self.pc + WORD_SIZE  # Save return address in R7
            logger.info(f"JAL executed: Return address saved in R7: {self.registers[7]}")

        self.pc = target_idx * WORD_SIZE
        logger.info(f"{'JAL' if link else 'J'} executed: Jumped to instruction index {target_idx}")

    def execute_memory_action(self, args: list[str], code: str) -> None:
        rt, offset_expr = args
        rt_idx = int(rt[1:])
        offset_str, rs_str = offset_expr.replace(')', '').split('(')
        rs_idx = int(rs_str[1:])
        offset = int(offset_str)
        if not self.validate_offset(offset, WORD_SIZE):
            raise Exception(f"Invalid offset: {offset}")
        if not self._valid_registers(rt_idx):
            raise Exception(f"Invalid register index: src={rs_idx}, rt={rt_idx}")
        if code == 'LW':
            self.registers[rt_idx] = self.memory.load_word(self.registers[rs_idx] + offset)
        elif code == 'SW':
            address = self.registers[rs_idx] + offset
            self.memory.store_word(address, self.registers[rt_idx])


    def execute_cache(self, code: str) -> None:
        if not code.isdigit() or int(code) not in range(0, 3):
            raise Exception("Invalid CACHE operation code")
        int_code = int(code)
        operation = {0: "disable", 1: "enable", 2: "flush"}[int_code]
        logger.info(f"Handling CACHE operation: {code} ({operation})")

        match int_code:
            case 0:
                logger.info("Disabling cache")
                if self.cache is not None:
                    logger.info("Flushing cache before disabling")
                    self.cache.flush(self.memory)
                    self.cache = None
                else:
                    logger.info("Cache already disabled")
            case 1:
                if self.cache is None:
                    logger.info("Enabling cache")
                    self.cache = Cache()
                else:
                    logger.info("Cache already enabled")
            case 2:
                if self.cache is not None:
                    logger.info("Flushing cache to memory")
                    self.cache.flush(self.memory)
                else:
                    logger.info("Cache is disabled, cannot flush")



    # Execute instruction based on opcode
    def execute_instruction(self, opcode, args):
        match opcode:
            case "ADD":
                self.execute_arithmetic(args, operator.add, opcode)
            case "ADDI":
                self.execute_arithmetic(args, operator.add, opcode, immediate=True)
            case "SUB":
                self.execute_arithmetic(args, operator.sub, opcode)
            case "SUBI":
                self.execute_arithmetic(args, operator.sub, opcode, immediate=True)
            case "SLT":
              self.execute_slt(args)
            case "BNE":
              self.execute_bne(args)    
            case "J":
                self.execute_jump(args)
            case "JAL":
                self.execute_jump(args, link=True)
            case "LW":
                self.execute_memory_action(args, opcode)
            case "SW":
                self.execute_memory_action(args, opcode)
            case "CACHE":
                self.execute_cache(args[0])
            case "HALT":
                self.halted = True
                print("Halting execution.")
        logger.info(f"Executed instruction: {opcode} with args: {args}")
        return 
    