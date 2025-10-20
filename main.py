"""
CPU Simulator
need to be able to - fetch and parse instructions from input file
need to be able to - fetch and parse initialization values for the Memory Bus from a separate input file
send CPU instructions and initial Memory Bus values to the CPU and Memory Bus, respectively
provide console output to the user documenting the stages of input processing
implement an ISA that can handle MIPS Instructions such as the following:

Using classes to represent CPU, cache, and memory
Simulating instruction fetching and execution
Showing how data moves between components
"""
import sys
import logging 
import math
from typing import Optional


MEMORY_SIZE = 2**20  # 1 MB memory size

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger("CPUSimulator")


class cpu:
    def __init__(self) -> None:
        logger.info("Initializing CPU Simulator")
        self.registers = [0] * 32
        self.pc = 0  # Program counter
        self.load_instructions = []
        self.memory = memory_bus()
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

# class memory 
class memory_bus:
    def __init__(self) -> None:
        logger.info("Initializing Memory")
        self.memory_size = MEMORY_SIZE  # 1 MB memory
        self.address_range = range(0, self.memory_size) # Valid address range
        self.storage = {i: 0 for i in range(self.memory_size)} # Initialize memory with zeros
        self.word_mask = 0xFFFFFFFF  # 32-bit word mask
        self.cache = None  # Placeholder for cache integration
        logger.info("Memory initialized with size 1 MB")

    def _validate_address(self, address: int) -> None:
        if not isinstance(address, int):
            raise TypeError("Address must be an integer")
        if address not in self.address_range:
            raise ValueError(f"Address {address} out of range. Valid range: 0 to {self.memory_size - 1}")

    def load_word(self, address: int) -> int:
        try:
            self._validate_address(address)
            logger.info(f"Loading word from address {address}")
        except (TypeError, ValueError) as e:
            logger.error(f"Error loading word: {e}")
            raise
        return self.storage.get(address, 0)

    
    def store_word(self, address: int, value: int) -> None:
        try:
            self._validate_address(address)
            logger.info(f"Loading word from address {address}")
        except (TypeError, ValueError) as e:
            logger.error(f"Error storing word: {e}")
            raise
        masked_value = value & self.word_mask
        self.storage[address] = masked_value
        logger.info(f"Stored word at address {address}: {value}")

class Block:
    def __init__(self, tag: int = 0, data: Optional[list[int]] = None) -> None:
        self.tag = tag
        self.valid = False
        self.dirty = False
        self.data = data if data is not None else [0] * 8  # 8-word block


# class cache
class cache:
    def __init__(self) -> None:
        logger.info("Initializing Cache")
        self.word_size = 4  # 4 bytes per word
        self.cache_size = 1024  # 1 KB cache size
        self.block_size = 8  # 8 words per block
        self.cache_lines = self.cache_size // (self.block_size * self.word_size)
        self.address_size = int(math.log2(MEMORY_SIZE))
        self.blocks = [Block() for _ in range(self.cache_lines)]        
        logger.info(f"Cache initialized with {self.cache_lines} lines")
        logger.info(f"Cache parameters - Word Size: {self.word_size} bytes, Cache Size: {self.cache_size} bytes, Block Size: {self.block_size} words")

    def decode_address(self, address: int) -> tuple[int, int, int]:
        offset = address & 0b111
        index = (address >> 3) & 0b11111
        tag = address >> 8
        return tag, index, offset

    def hit_or_miss(self, block: Block, tag: int) -> bool:
        return block.valid and block.tag == tag

    def read(self, address: int, memory: memory_bus) -> Optional[list[int]]:
        tag, index, offset = self.decode_address(address)
        block = self.blocks[index]
        if self.hit_or_miss(block, tag):
            logger.info(f"Reading from cache for address {address}")
            return block.data[offset:offset+1]
        logger.info(f"Cache miss on read for address {address}")
        # implement block fetch from memory
        new_block = self.evict_and_get_block(tag, index, memory)
        return new_block.data[offset:offset+1]

    def write(self, address: int, value: int, memory: memory_bus) -> None:
        tag, index, offset = self.decode_address(address)
        block = self.blocks[index]
        if self.hit_or_miss(block, tag):
            logger.info(f"Writing to cache for address {address}")
            block.data[offset] = value
            block.dirty = True
            return
            # Update cache block data
        logger.info(f"Cache miss on write to address {address}")
        # call block replacement policy 
        logger.info(f"Evicting block and fetching new block for address {address}")
        new_block = self.evict_and_get_block(tag, index, memory)
        new_block.data[offset] = value
        block.dirty = True
        logger.info(f"Writing to cache for address {address}")


    def evict_and_get_block(self, tag: int, index: int, memory: memory_bus) -> Block:
        block = self.blocks[index]
        # calcuate base address of block in memory
        base_address = (block.tag << 8) | (index << 3)
        if block.valid and block.dirty:
            # Write back data to memory
            for i in range(self.block_size):
                memory.store_word(base_address + i * 4, block.data[i])
        # calculate base address for new block
        base_address = (tag << 8) | (index << 3)
        # Create new block 
        new_block = Block(tag=tag)
        # load data from memory into new block
        for i in range(self.block_size):
            word = memory.load_word(base_address + i * 4)
            new_block.data[i] = word
        new_block.valid = True
        # evict old block and replace with new block
        self.blocks[index] = new_block
        return new_block
    
    def flush(self, memory: memory_bus) -> None:
        logger.info("flushing cache to memory")
        for index, block in enumerate(self.blocks):
            base_address = (block.tag << 8) | (index << 3)
            if block.valid and block.dirty:
                for i in range(self.block_size):
                    memory.store_word(base_address + i * 4, block.data[i])
                block.dirty = False
        logger.info("Cache flush complete")


# Main execution
cpu_sim = cpu()
cpu_sim.load_instruction('files/instruction_input.txt')
cpu_sim.parse_instructions()
cpu_sim.load_memory('files/data_input.txt')
cpu_sim.parse_instructions()
cpu_sim.execute_instruction('ADDI', ['R1', 'R2', '000000011'])  # Example execution

