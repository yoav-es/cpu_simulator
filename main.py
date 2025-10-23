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

import logging 
# from typing import Optional
from cpu.cpu import CPU
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger("CPUSimulator")

def main():
    cpu_sim = CPU()
    cpu_sim.load_instruction('files/instruction_input.txt')
    cpu_sim.load_memory('files/data_input.txt')
    cpu_sim.validate_instructions()
    cpu_sim.execute_instructions()
    cpu_sim.execute_instruction('ADDI', ['R1', 'R2', '000000011'])

if __name__ == "__main__":
    main()
