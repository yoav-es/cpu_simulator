"""
CPU Simulator

MIPS-inspired CPU simulation. Loads instructions and memory from input files,
validates them, and executes the program.

Components: CPU (registers, execution), MemoryBus (storage), Cache (optimization).

Usage:
    python main.py --instructions files/instruction_input.txt \\
        --memory files/data_input.txt
"""

import argparse
import json
import logging
import sys

from cpu.cpu import CPU

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("CPUSimulator")


def main():
    parser = argparse.ArgumentParser(description="Run the CPU Simulator.")
    parser.add_argument(
        "--instructions", type=str, required=True, help="Path to instruction input file"
    )
    parser.add_argument(
        "--memory", type=str, required=True, help="Path to memory initialization file"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print PC and registers for each instruction",
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["text", "json"],
        default="text",
        help="Output format: text (default) or json for final state",
    )
    args = parser.parse_args()

    try:
        cpu_sim = CPU()
        logger.info("Loading instructions and memory...")
        cpu_sim._load_instructions(args.instructions)
        cpu_sim._load_memory(args.memory)
        cpu_sim._validate_instructions()
        logger.info("Starting instruction execution...")
        cpu_sim.execute_instructions(verbose=args.verbose)
        logger.info("Simulation complete.")
        if args.output == "json":
            result = {
                "halted": cpu_sim.halted,
                "pc": cpu_sim.pc,
                "registers": cpu_sim.registers,
            }
            print(json.dumps(result, indent=2))
        sys.exit(0)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Simulation failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
