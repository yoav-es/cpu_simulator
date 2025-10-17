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
            "HALT": {"args": 0}
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
            #HALT instruction check 
            if opcode == "HALT":
                print("HALT encountered. Terminating execution.")
                self.halted = True
                return  # or return if you're inside a method

            expected_arg_count = self.instruction_set[opcode]["args"]
            if len(args) != expected_arg_count:
                print(f"Invalid argument count for {opcode}: {args}")
                continue

            print(f"Parsed {opcode} with args: {args}")
            # self.execute_instruction(opcode, args)
            self.pc += 1
                #execute instructions here? 
        return print("Finished parsing instructions.")
    

    

cpu_sim = cpu()
cpu_sim.load_instruction('files/instruction_input.txt')
cpu_sim.parse_instructions()
cpu_sim.load_memory('files/data_input.txt')


# class memory 

# class alu 

# class bus

# class registers 

# class isa

# 