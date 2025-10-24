"""
CPU Simulator

This script initializes and runs a simplified CPU simulation using MIPS-like instructions.
It loads instructions and memory data from input files, validates them, and executes the program.

Components:
- CPU: Executes instructions and manages registers
- MemoryBus: Stores and retrieves data
- Cache: Optimizes memory access

Usage:
    python main.py --instructions files/instruction_input.txt --memory files/data_input.txt
"""

import argparse
import logging
from cpu.cpu import CPU

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger("CPUSimulator")

def main():
    parser = argparse.ArgumentParser(description="Run the CPU Simulator.")
    parser.add_argument('--instructions', type=str, required=True, help='Path to instruction input file')
    parser.add_argument('--memory', type=str, required=True, help='Path to memory initialization file')
    args = parser.parse_args()

    try:
        cpu_sim = CPU()
        logger.info("Loading instructions and memory...")
        cpu_sim.load_instruction(args.instructions)
        cpu_sim.load_memory(args.memory)
        cpu_sim.validate_instructions()
        logger.info("Starting instruction execution...")
        cpu_sim.execute_instructions()

        # Optional: manual instruction test
        # cpu_sim.execute_instruction('ADDI', ['R1', 'R2', '000000011'])

        logger.info("Simulation complete.")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")

if __name__ == "__main__":
    main()