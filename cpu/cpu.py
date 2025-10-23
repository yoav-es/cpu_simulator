import sys
from .memory_bus import MemoryBus
from .cache import Cache
import logging
import operator
logger = logging.getLogger(__name__)
logger.info("CPU initialized")

# CPU Simulator Class
class CPU:
    # Initialize CPU with registers, program counter, instruction set, memory bus, and cache
    def __init__(self) -> None:
        logger.info("Initializing CPU Simulator")
        self.registers = [0] * 32
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
        return all(isinstance(idx, int) and 0 <= idx < 32 for idx in indices) and (allow_r0 or 0 not in indices)

    def validate_immediate_value(self, value: str, bits: int | None = None) -> int:
        """
        Validate a binary immediate string and return its signed integer value.
        If bits is None, use the length of the provided string.
        """
        if not isinstance(value, str) or not value:
            raise ValueError("Immediate must be a non-empty binary string")
        if not all(c in '01' for c in value):
            raise ValueError(f"Immediate value is not a valid binary string: {value}")
        bits = bits or len(value)
        if bits > 32:
            raise ValueError("Immediate width greater than 32 bits not supported")
        unsigned = int(value, 2)
        sign_bit = 1 << (bits - 1)
        # convert from two's complement to signed int
        if unsigned & sign_bit:
            signed = unsigned - (1 << bits)
        else:
            signed = unsigned
        # optional range check for 32-bit signed
        if not (-(2**31) <= signed <= (2**31 - 1)):
            raise ValueError(f"Immediate value out of 32-bit signed range: {signed}")
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

    # parse and execute instructions
    def parse_instructions(self) -> None:
        logger.info("Parsing instructions")
        for instruction in self.load_instructions:
            opcode = instruction[0]
            args = instruction[1:]
            #Invalid instruction check
            if opcode not in self.instruction_set:
                logger.warning(f"Unknown instruction: {opcode}")
                continue
            # Argument count check
            expected_arg_count = self.instruction_set[opcode]["args"]
            if len(args) != expected_arg_count:
                logger.warning(f"Incorrect number of arguments for {opcode}. Expected {expected_arg_count}, got {len(args)}")
                continue
            logger.info(f"Parsed {opcode} with args: {args}")
        # Execute instructions
        while not self.halted and self.pc < len(self.load_instructions):
            current_pc = self.pc
            opcode, *args = self.load_instructions[self.pc // 4]
            try:
                logger.info(f"Executing {opcode} with args: {args}")
                self.execute_instruction(opcode, args)
                self.registers[0] = 0
                if self.pc == current_pc:
                    self.pc += 4
            except Exception as e:
                logger.error(f"Error executing instruction at PC {self.pc}: {e}")
                self.halted = True
        logger.info("Finished parsing instructions.")
    
    # # Execute arithmetic instruction (ADD, ADDI, SUB, SUBI)
    def execute_arithmetic(self, args: list[str], op_func, op_name: str, immediate: bool = False) -> None:
        if immediate:
            dest, src, immd = args
            dest_idx = int(dest[1:])
            src_idx = int(src[1:])
            value = self.validate_immediate_value(immd)
            instr_name = f"{op_name}I"
        else:
            dest, src, rt = args
            dest_idx = int(dest[1:])
            src_idx = int(src[1:])
            rt_idx = int(rt[1:])
            value = self.registers[rt_idx]
            instr_name = op_name

        if not self._valid_registers(src_idx, dest_idx):
            raise Exception(f"Invalid register index: src={src_idx}, dest={dest_idx}")

        result = op_func(self.registers[src_idx], value)
        if dest_idx != 0:
            self.registers[dest_idx] = result

        logger.info(f"{instr_name} executed: R{dest_idx} = R{src_idx} {op_name} {value} → {result}")




    # Execute set on less than instruction
    def execute_slt(self, args: list[str]) -> None:
        logger.info("Executing SLT instruction")
        dest, src, rt = args
        dest_idx = int(dest[1:])
        src_idx = int(src[1:])
        rt_idx = int(rt[1:])
        if not self._valid_registers(src_idx, rt_idx, dest_idx):
            raise Exception(f"Invalid register index: src={src_idx}, rt={rt_idx}, dest={dest_idx}")
        self.registers[dest_idx] = 1 if self.registers[src_idx] < self.registers[rt_idx] else 0
        logger.info(f"SLT executed: R{dest_idx} = (R{src_idx} < R{rt_idx}) → {self.registers[dest_idx]}")

    # Execute branch not equal instruction
    def execute_bne(self, args: list[str]) -> None:
        logger.info("Executing BNE instruction")
        rs, rt, offset = args
        rs_idx = int(rs[1:])
        rt_idx = int(rt[1:])
        offset = int(offset)
        if not self._valid_registers(rs_idx, rt_idx):
            raise Exception(f"Invalid register index: src={rs_idx}, rt={rt_idx}")
        if offset % 4 != 0 or not (-32768 <= offset <= 32767):
            raise Exception(f"Invalid branch offset: {offset}")
        if self.registers[rs_idx] != self.registers[rt_idx]:
            self.pc = self.pc + 4 + offset * 4
            logger.info(f"BNE taken: PC updated to {self.pc}")        

    # Execute jump instruction
    def execute_jump(self, args: list[str],link: bool = False) -> None:
        target = args[0]
        if not target.isdigit():
            raise Exception("Jump target must be a number")
        target_idx = int(target)
        if not (0 <= target_idx < len(self.load_instructions)):
            raise Exception("Jump target out of instruction range")
        if link:
            self.registers[7] = self.pc + 4  # Save return address in R31
            logger.info(f"JAL executed: Return address saved in R7: {self.registers[7]}")
        self.pc = target_idx * 4
        logger.info(f"Jump executed to instruction index: {target_idx}")

    # Execute load word instruction
    def execute_lw(self, args: list[str]) -> None:
        rt, offset_expr = args
        rt_idx = int(rt[1:])
        offset_str, rs_str = offset_expr.replace(')', '').split('(')
        offset = int(offset_str)
        rs_idx = int(rs_str[1:])
        if not self._valid_registers(rs_idx, rt_idx, offset):
            raise Exception(f"Invalid register index: src={rs_idx}, rt={rt_idx}")
        if offset % 4 != 0 or not (-32768 <= offset <= 32767):
            raise Exception(f"Invalid store offset: {offset}")
        self.registers[rt_idx] = self.memory.load_word(self.registers[rs_idx] + offset)

    # Execute store word instruction
    def execute_sw(self, args: list[str]) -> None:
        rt, offset_expr = args
        rt_idx = int(rt[1:])
        offset_str, rs_str = offset_expr.replace(')', '').split('(')
        offset = int(offset_str)
        rs_idx = int(rs_str[1:])
        if not self._valid_registers(rs_idx, rt_idx):
            raise Exception(f"Invalid register index: src={rs_idx}, rt={rt_idx}")
        if offset % 4 != 0 or not (-32768 <= offset <= 32767):
            raise Exception(f"Invalid store offset: {offset}")
        address = self.registers[rs_idx] + offset
        self.memory.store_word(address, self.registers[rt_idx])

    # Execute cache operation
    def execute_cache(self, code) -> None:
        if not code.isdigit() or int(code) not in range(0, 3):# Valid CACHE operation codes: 0-cache off, 1-cache on, 2 - flush cache
            raise Exception("Invalid CACHE operation code")
        logger.info(f"Executing CACHE operation with code: {code}")
        status = True if self.cache is None else False
        match code:
            case '0':
                logger.info("Disabling cache")
                if status:
                    logger.info("Flushing cache before disabling")
                    self.cache = None
                else:
                    logger.info("Cache already disabled")
            case '1':
                if status is None:
                    logger.info("Enabling cache")
                    self.cache = Cache()
                else:
                    logger.info("Cache already enabled")
            case '2':
                if status:
                    raise Exception("Cache is not enabled; cannot flush")
                else:
                    logger.info("Flushing cache to memory")
                    self.cache.flush(self.memory)

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
                self.execute_lw(args)
            case "SW":
                self.execute_sw(args)
            case "CACHE":
                self.execute_cache(args[0])
            case "HALT":
                self.halted = True
                print("Halting execution.")
        logger.info(f"Executed instruction: {opcode} with args: {args}")
        return 
