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


class cpu:
    def __init__(self) -> None:
        
        self.registers = [32] * 0  # Example: 32 registers initialized to 0
        self.pc = 0  # Program counter
        self.load_instructions = []
        self.memory_intialization_values = []
        self.halted = False
        # self.memory = memory() - not implemented yet
        # self.cache = cache() - not implemented yet

        self.instruction_set = {
            "ADD": {"args": 3},
            "ADDI": {"args": 3},
            "J": {"args": 1},
            "CACHE": {"args": 1},
            "HALT": {"args": 1}
        }


    def _load_file_lines(self, filepath):
        with open(filepath, 'r') as file:
            return [line.strip() for line in file.readlines()]
    
    def load_instruction(self, instructions_file):
        for line in self._load_file_lines(instructions_file):
            self.load_instructions.append(line.split(','))

    def load_memory(self, data_file):
        for line in self._load_file_lines(data_file):
            entry = line.split(',')
            self.memory_intialization_values.append((int(entry[0],2), int(entry[1])))
            print(f"Loaded memory initialization value: Address {entry[0]} Data {entry[1]}")

    def parse_instructions(self) -> None:
        for instruction in self.load_instructions:
            opcode = instruction[0]
            args = instruction[1:]
            #Invalid instruction check
            if opcode not in self.instruction_set:
                print(f"Unknown instruction: {opcode}")
                continue

            expected_arg_count = self.instruction_set[opcode]["args"]
            if len(args) != expected_arg_count:
                print(f"Invalid argument count for {opcode}: {args}")
                continue
            print(f"Parsed {opcode} with args: {args}")

        while not self.halted and self.pc < len(self.load_instructions):
            current_pc = self.pc
            opcode, *args = self.load_instructions[self.pc // 4]
            self.execute_instruction(opcode, args)
            self.registers[0] = 0
            if self.pc == current_pc:
                self.pc += 4
        return print("Finished parsing instructions.")
    
    def valid_registers(*indices, allow_r0=False):
            return all(0 <= idx < 32 for idx in indices) and (allow_r0 or 0 not in indices)

    def execute_instruction(self, opcode, args):
        match opcode:
            case "ADD":
                Rd, Rs, Rt = args
                rs_idx = int(Rs[1:])
                rt_idx = int(Rt[1:])
                rd_idx = int(Rd[1:])
                if valid_registers(rs_idx, rt_idx, rd_idx):
                    self.registers[rd_idx] = self.registers[rs_idx] + self.registers[rt_idx]
                else: 
                    raise Exception("Invalid register index")
            case "ADDI":
                Rt, Rs, immd = args
                rt_idx = int(Rt[1:])
                rs_idx = int(Rs[1:])
                immd   = int(immd, 2)
                if -(2**31) <= immd <= (2**31 - 1):
                    if all(0 <= idx < 32 for idx in [rs_idx, rt_idx]) and rt_idx != 0:
                        self.registers[rt_idx] = self.registers[rs_idx] + immd
                    else:
                        raise Exception("Invalid register index")
                else:
                    raise Exception("Immediate value out of range")                
            case "J":
                target = args[0]
                if not target.isdigit():
                    raise Exception("Jump target must be a number")

                target_idx = int(target)
                if not (0 <= target_idx < len(self.load_instructions)):
                    raise Exception("Jump target out of instruction range")

                self.pc = target_idx * 4
                print(f"Jumping to byte address: {self.pc}")

            case "CACHE":
                code = (args[0])
                if not code.isdigit() or int(code) not in range(0, 3):# Valid CACHE operation codes: 0-cache off, 1-cache on, 2 - flush cache
                    raise Exception("Invalid CACHE operation code")
                print(f"CACHE operation with code: {code}")
                # Cache operations not implemented yet
                # call to self. cache with code - not implemented yet

            case "HALT":
                self.halted = True
                self.pc = 0
                print("Halting execution.")
        return 



cpu_sim = cpu()
cpu_sim.load_instruction('files/instruction_input.txt')
cpu_sim.parse_instructions()
cpu_sim.load_memory('files/data_input.txt')


# class memory 
"""
- Design Memory class:
- Address-value mapping
- Read/write interface
"""
# class cache
"""
- Basic structure (e.g., direct-mapped or associative)
- Hit/miss logic
- Integration with memory
"""