import sys
from .memory_bus import MemoryBus
from .cache import Cache
import logging
logger = logging.getLogger(__name__)

logger.info("CPU initialized")


class CPU:
    def __init__(self) -> None:
        logger.info("Initializing CPU Simulator")
        self.registers = [0] * 32
        self.pc = 0  # Program counter
        self.load_instructions = []
        self.cache = Cache()
        self.memory = MemoryBus()
        self.halted = False
        # self.cache = cache() - not implemented yet

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

    @staticmethod
    def _load_file_lines(filepath):
        logger.info(f"Loading file: {filepath}")
        with open(filepath, 'r') as file:
            return [line.strip() for line in file.readlines()]
    
    @staticmethod
    def _valid_registers(*indices: int, allow_r0: bool = False) -> bool:
        return all(isinstance(idx, int) and 0 <= idx < 32 for idx in indices) and (allow_r0 or 0 not in indices)

    def load_instruction(self, instructions_file):
        if not instructions_file:
            logger.error("No instruction file provided.")
            sys.exit(1)
        logger.info("loading instructions")
        for line in self._load_file_lines(instructions_file):
            self.load_instructions.append(line.split(','))

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

    def parse_instructions(self) -> None:
        logger.info("Parsing instructions")
        for instruction in self.load_instructions:
            opcode = instruction[0]
            args = instruction[1:]
            #Invalid instruction check
            if opcode not in self.instruction_set:
                logger.warning(f"Unknown instruction: {opcode}")
                continue

            expected_arg_count = self.instruction_set[opcode]["args"]
            if len(args) != expected_arg_count:
                logger.warning(f"Incorrect number of arguments for {opcode}. Expected {expected_arg_count}, got {len(args)}")
                continue
            logger.info(f"Parsed {opcode} with args: {args}")

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
    

    def execute_add(self, args: list[str], immediate: bool = False) -> None:
        if immediate:
            dest, src, immd = args
            dest_idx = int(dest[1:])
            src_idx = int(src[1:])
            if not all(c in '01' for c in immd):
                raise ValueError(f"Immediate value is not a valid binary string: {immd}")
            value = int(immd, 2)
            instr_name = "ADDI"
        else:
            dest, src, rt = args
            dest_idx = int(dest[1:])
            src_idx = int(src[1:])
            rt_idx = int(rt[1:])
            value = self.registers[rt_idx]
            instr_name = "ADD"

        if not self._valid_registers(src_idx, dest_idx):
            raise Exception(f"Invalid register index: src={src_idx}, dest={dest_idx}")

        if immediate and not (-(2**31) <= value <= (2**31 - 1)):
            raise Exception(f"Immediate value out of range: {value}")

        result = self.registers[src_idx] + value
        if dest_idx != 0:
            self.registers[dest_idx] = result

        logger.info(f"{instr_name} executed: R{dest_idx} = R{src_idx} + {value} → {result}")


    def execute_sub(self, args: list[str], immediate: bool = False) -> None:
        if immediate:
            dest, src, immd = args
            dest_idx = int(dest[1:])
            src_idx = int(src[1:])
            if not all(c in '01' for c in immd):
                raise ValueError(f"Immediate value is not a valid binary string: {immd}")
            value = int(immd, 2)
            instr_name = "SUBI"
        else:
            dest, src, rt = args
            dest_idx = int(dest[1:])
            src_idx = int(src[1:])
            rt_idx = int(rt[1:])
            value = self.registers[rt_idx]
            instr_name = "SUB"

        if not self._valid_registers(src_idx, dest_idx):
            raise Exception(f"Invalid register index: src={src_idx}, dest={dest_idx}")

        if immediate and not (-(2**31) <= value <= (2**31 - 1)):
            raise Exception(f"Immediate value out of range: {value}")

        result = self.registers[src_idx] - value
        if dest_idx != 0:
            self.registers[dest_idx] = result

        logger.info(f"{instr_name} executed: R{dest_idx} = R{src_idx} - {value} → {result}")


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


    def execute_cache(self, code) -> None:
        if not code.isdigit() or int(code) not in range(0, 3):# Valid CACHE operation codes: 0-cache off, 1-cache on, 2 - flush cache
            raise Exception("Invalid CACHE operation code")
        logger.info(f"Executing CACHE operation with code: {code}")
        # Cache operations not implemented yet
        # call to self. cache with code - not implemented yet

    def execute_instruction(self, opcode, args):
        match opcode:
            case "ADD":
                self.execute_add(args)
            case "ADDI":
                self.execute_add(args, immediate=True)    
            case "SUB":
              self.execute_sub(args)
            case "SUBI":
              self.execute_sub(args)
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
