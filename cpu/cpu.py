import logging
import operator

from utils.constants import BUS_LENGTH, INT16_MAX, INT16_MIN, LINK_REGISTER, WORD_SIZE

from .cache import Cache
from .memory_bus import MemoryBus

logger = logging.getLogger(__name__)
logger.info("CPU initialized")


# CPU Simulator Class
class CPU:
    """CPU Simulator Class"""

    def __init__(self) -> None:
        """Initialize CPU with registers, program counter, memory, and cache."""
        logger.info("Initializing CPU Simulator")
        self.registers = [0] * 32
        self.pc = 0  # Program counter
        self.load_instructions = []
        self.cache = None
        self.memory = MemoryBus()
        self.halted = False
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
            "HALT": {"args": 1},
        }

    # file loading and handling
    @staticmethod
    def _load_file_lines(filepath):
        """Load lines from a file and return them as a list."""
        logger.info(f"Loading file: {filepath}")
        with open(filepath, "r") as file:
            return [line.strip() for line in file.readlines()]

    def _load_instructions(self, instructions_file: str) -> None:
        """Load instructions from file into the CPU."""
        if not instructions_file:
            raise ValueError("No instruction file provided.")
        logger.info("Loading instructions")
        lines = self._load_file_lines(instructions_file)
        try:
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.replace(",", " ").split()
                self.load_instructions.append(parts)
        except Exception as e:
            logger.error("Error parsing instructions: %s", e)
            raise ValueError(f"Error parsing instructions: {e}") from e
        logger.info("Finished loading instructions.")

    def _load_memory(self, data_file: str) -> None:
        """Load memory initialization values from file."""
        if not data_file:
            raise ValueError("No data file provided.")
        logger.info("Loading memory initialization values")
        lines = self._load_file_lines(data_file)
        try:
            for line in lines:
                entry = line.split(",")
                self.memory.store_word(int(entry[0], 2), int(entry[1]))
                logger.info(
                    "Loaded memory initialization value: Address %s Data %s",
                    entry[0],
                    entry[1],
                )
        except Exception as e:
            logger.error("Error loading memory initialization values: %s", e)
            raise ValueError(f"Error loading memory initialization values: {e}") from e
        logger.info("Finished loading memory initialization values.")

    # input validation

    @staticmethod
    def _valid_registers(*indices: int, allow_r0: bool = False) -> bool:
        """Validate register indices."""
        return all(
            isinstance(idx, int) and 0 <= idx < BUS_LENGTH for idx in indices
        ) and (allow_r0 or 0 not in indices)

    @staticmethod
    def _validate_offset(offset: int, word_size: int) -> None:
        """Validate offset for branch and memory instructions."""
        if not isinstance(offset, int):
            raise TypeError(f"Offset must be an integer, got {type(offset).__name__}")
        if word_size <= 0:
            raise ValueError(f"Word size must be positive, got {word_size}")
        if offset % word_size != 0 or not (INT16_MIN <= offset <= INT16_MAX):
            raise ValueError(f"Invalid offset: {offset}")

    @staticmethod
    def _validate_immediate_value(value: str) -> int:
        """Validate a decimal immediate string and return its signed integer value."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Immediate must be a non-empty string")
        try:
            signed = int(value)
        except ValueError:
            raise ValueError(f"Immediate value is not a valid integer: {value}")
        # Check 32-bit signed integer range
        if not (-(2**31) <= signed <= (2**31 - 1)):
            raise ValueError(f"Immediate value out of 32-bit signed range: {signed}")
        return signed

    def _validate_instructions(self) -> None:
        """Validate loaded instructions against the instruction set."""
        logger.info("Validating instructions")
        # Iterate through loaded instructions and validate each
        for instruction in self.load_instructions:
            opcode = instruction[0]
            args = instruction[1:]
            if opcode not in self.instruction_set:
                logger.warning(f"Unknown instruction: {opcode}")
                continue
            expected_arg_count = self.instruction_set[opcode]["args"]
            if len(args) != expected_arg_count:
                logger.warning(
                    "Incorrect number of arguments for %s. Expected %s, got %s",
                    opcode,
                    expected_arg_count,
                    len(args),
                )
                continue
            logger.info(f"Validated {opcode} with args: {args}")

    # Argument parsing
    @staticmethod
    def _parse_args(args: list[str], imm: bool = False) -> tuple[int, int, int]:
        """Parse instruction arguments and return register indices and immediate value if applicable."""
        arg1 = int(args[0][1:])
        arg2 = int(args[1][1:])
        arg3 = (
            CPU._validate_immediate_value(args[2]) if imm else int(args[2][1:])
        )
        return arg1, arg2, arg3

    @staticmethod
    def _parse_memory_args(args: list[str]) -> tuple[int, int, int]:
        """
        Parse LW/SW-style arguments: [rt, offset(rs)]
        Returns: rt index, rs index, offset
        """
        if len(args) != 2:
            raise ValueError(
                f"Expected 2 arguments for memory instruction, got {len(args)}: {args}"
            )

        rt = args[0]
        offset_expr = args[1]

        if not offset_expr.endswith(")") or "(" not in offset_expr:
            raise ValueError(f"Malformed memory operand: {offset_expr}")

        try:
            offset_str, rs_str = offset_expr.replace(")", "").split("(")
            rt_idx = int(rt[1:])
            rs_idx = int(rs_str[1:])
            offset = int(offset_str)
        except Exception as e:
            raise ValueError(f"Failed to parse memory args: {args}") from e

        return rt_idx, rs_idx, offset

    # Instruction handlers
    def execute_arithmetic(
        self, args: list[str], op_func, op_name: str, immediate: bool = False
    ) -> None:
        """Execute arithmetic instructions (ADD, ADDI, SUB, SUBI)."""
        if immediate:
            dest_idx, src_idx, value = self._parse_args(args, imm=True)
        else:
            dest_idx, src_idx, rt_idx = self._parse_args(args)
            value = self.registers[rt_idx]

        if not self._valid_registers(src_idx, dest_idx):
            raise Exception(f"Invalid register index: src={src_idx}, dest={dest_idx}")

        self.registers[dest_idx] = op_func(self.registers[src_idx], value)

    def execute_slt(self, args: list[str]) -> None:
        """Execute set on less than instruction."""
        logger.info("Executing SLT instruction")
        dest_idx, src_idx, rt_idx = self._parse_args(args)

        if not self._valid_registers(src_idx, rt_idx, dest_idx):
            raise Exception(
                f"Invalid register index: src={src_idx}, rt={rt_idx}, dest={dest_idx}"
            )

        self.registers[dest_idx] = int(self.registers[src_idx] < self.registers[rt_idx])
        logger.info(
            "SLT executed: R%s = (R%s < R%s) → %s",
            dest_idx,
            src_idx,
            rt_idx,
            self.registers[dest_idx],
        )

    def execute_bne(self, args: list[str]) -> None:
        """Execute branch not equal instruction."""
        logger.info("Executing BNE instruction")
        rs_idx, rt_idx, offset = self._parse_args(args, imm=True)
        if not self._valid_registers(rs_idx, rt_idx):
            raise Exception(f"Invalid register index: src={rs_idx}, rt={rt_idx}")
        # Offset validation
        offset = int(offset) * WORD_SIZE
        self._validate_offset(offset, WORD_SIZE)
        if self.registers[rs_idx] != self.registers[rt_idx]:
            self.pc = self.pc + WORD_SIZE + offset
            logger.info(f"BNE taken: PC updated to {self.pc}")

    def execute_jump(self, args: list[str], link: bool = False) -> None:
        """Execute jump (J) and jump and link (JAL) instructions."""
        target = args[0]
        if not target.isdigit():
            raise Exception("Jump target must be a number")

        target_index = int(target)
        if not (0 <= target_index < len(self.load_instructions)):
            raise Exception(
                f"Jump target {target_index} out of instruction range "
                f"(max index: {len(self.load_instructions) - 1})"
            )

        if link:
            self.registers[LINK_REGISTER] = self.pc + WORD_SIZE
            logger.info(
                f"JAL executed: Return address saved in R7: {self.registers[7]}"
            )

        target_address = target_index * WORD_SIZE
        self.pc = target_address
        logger.info(
            "%s executed: Jumped to instruction index %s",
            "JAL" if link else "J",
            target_index,
        )

    def execute_memory_action(self, args: list[str], code: str) -> None:
        """Execute load word (LW) and store word (SW) instructions."""
        rt_idx, rs_idx, offset = self._parse_memory_args(args)
        self._validate_offset(offset, WORD_SIZE)
        if not self._valid_registers(rt_idx, rs_idx, allow_r0=True):
            raise Exception(f"Invalid register index: src={rs_idx}, rt={rt_idx}")
        address = self.registers[rs_idx] + offset
        if code == "LW":
            if self.cache is not None:
                value = self.cache.read(address, self.memory)[0]
                self.registers[rt_idx] = value
            else:
                self.registers[rt_idx] = self.memory.load_word(address)
        elif code == "SW":
            if self.cache is not None:
                self.cache.write(address, self.registers[rt_idx], self.memory)
            else:
                self.memory.store_word(address, self.registers[rt_idx])
        else:
            raise Exception(f"Unsupported memory operation: {code}")

    def execute_cache(self, code: str) -> None:
        """Execute CACHE instruction: disable, enable, or flush the cache."""
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

    # instruction dispatching
    def dispatch_instruction(self, opcode, args):
        """Execute a single instruction based on the opcode and arguments."""
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
                if self.cache is not None:
                    self.cache.flush(self.memory)
                self.halted = True
            case "NOP":
                pass  # Do nothing
            case _:
                raise ValueError(f"Unknown opcode: {opcode}")

        logger.info(f"Executed instruction: {opcode} with args: {args}")
        return

    def execute_instructions(self, verbose: bool = False) -> None:
        """Execute loaded instructions sequentially."""
        logger.info("Starting instruction execution")

        while not self.halted and self.pc < len(self.load_instructions) * WORD_SIZE:
            current_pc = self.pc
            instr_index = self.pc // WORD_SIZE
            instr = self.load_instructions[instr_index]
            opcode, *args = self.load_instructions[self.pc // WORD_SIZE]

            if verbose:
                logger.info("PC: %s | Instruction: %s", self.pc, instr)
                logger.info("Registers before: %s", self.registers)

            try:
                logger.debug("Executing %s with args: %s", opcode, args)
                self.dispatch_instruction(opcode, args)
                self.registers[0] = 0
                if self.pc == current_pc:
                    self.pc += WORD_SIZE

                if verbose:
                    logger.info("Registers after: %s", self.registers)

            except Exception as e:
                # Jump to invalid instruction index halts execution.
                logger.error(
                    "Error executing %s instruction at PC %s: %s",
                    opcode,
                    self.pc,
                    e,
                )
                self.halted = True
                logger.info("HALT executed due to error")
                return
        logger.info(".")
