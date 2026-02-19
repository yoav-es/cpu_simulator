# CPU Simulator (MIPS-Inspired)

This project simulates a simplified CPU architecture in Python, modeling core components like the CPU, memory bus, and cache. Its primary goal is to mimic the behavior of a MIPS-like processor, providing a hands-on environment to explore instruction execution, memory access, and basic control flow in a RISC-style architecture.

---

## Features

### CPU Core
- Program counter and register file
- Instruction parsing and execution
- HALT logic and control flow

### Memory Bus
- 1MB addressable memory
- Word-level read/write interface
- Input file support for memory initialization

### Cache System
- Direct-mapped cache with block-based storage
- Hit/miss detection and block replacement
- Write-back policy with flush support

---

## Recent Improvements

The following improvements were implemented to enhance modularity, testability, and adherence to PEP style:

### Functionality
- **Cache integration**: LW and SW now route through the cache when enabled via `CACHE 1`; previously memory bypassed the cache entirely
- **Cache address formula**: Fixed block base-address calculation; addresses now derive correctly from `offset_bits` and `index_bits`
- **Flush on HALT**: Dirty cache blocks are flushed to memory when execution halts

### CLI
- **`--verbose` / `-v`**: Print PC and registers for each instruction (default is quiet)
- **`--output json` / `-o json`**: Output final state (halted, pc, registers) as JSON for programmatic use

### Code Quality
- Replaced `sys.exit` with exceptions; error handling centralized in `main.py`
- Raised `ValueError` instead of generic `Exception` for invalid offsets
- Removed dead code and duplicate tests
- Introduced `LINK_REGISTER` constant; improved type hints and docstrings

### Testing
- 77 unit and integration tests
- ~93% code coverage (`cpu`, `cache`, `memory_bus`, `utils`)
- New cache integration test for LW/SW with cache enabled
- Removed duplicate MemoryBus tests from `test_cpu_utils.py`

### CI/CD
- black lint in GitHub Actions
- Coverage reporting via `pytest --cov=cpu --cov=utils`
- Workflows trigger on both `main` and `master` branches

### Documentation
- Project structure aligned with actual layout
- Memory file format clarified (binary addresses)
- NOP added to ISA table
- Direct commands documented (Makefile no longer used)

---

## Project Structure

```
cpu_simulator/
  cpu/
    cpu.py          # CPU core and instruction execution
    memory_bus.py   # Memory storage
    cache.py        # Cache with write-back policy
  utils/
    constants.py    # Architecture constants
  main.py           # Entry point and CLI
  tests/
    unit/           # Unit tests
    integration/    # Integration tests
  files/            # Sample instruction and memory files
  pyproject.toml    # Project configuration
  Dockerfile
```

---

## Instruction Set Architecture (ISA)

| Instruction | Operands         | Description                                   |
|-------------|------------------|-----------------------------------------------|
| `ADD`       | Rd, Rs, Rt       | `Rd ← Rs + Rt`                                |
| `ADDI`      | Rt, Rs, immd     | `Rt ← Rs + immd`                              |
| `SUB`       | Rd, Rs, Rt       | `Rd ← Rs - Rt`                                |
| `SUBI`      | Rd, Rs, immd     | `Rd ← Rs - immd`                              |
| `SLT`       | Rd, Rs, Rt       | `Rd ← (Rs < Rt) ? 1 : 0`                      |
| `BNE`       | Rs, Rt, offset   | `If Rs ≠ Rt → PC ← (PC + 4) + offset × 4`     |
| `J`         | target           | `PC ← target × 4`                             |
| `JAL`       | target           | `R7 ← PC + 4; PC ← target × 4`                |
| `LW`        | Rt, offset(Rs)   | `Rt ← MEM[Rs + offset]`                       |
| `SW`        | Rt, offset(Rs)   | `MEM[Rs + offset] ← Rt`                       |
| `CACHE`     | Code             | `0 = off`, `1 = on`, `2 = flush`              |
| `NOP`       | —                | No operation                                  |
| `HALT`      | —                | Terminate execution                           |

---

## How to Run

### Prerequisites

- Python 3.10 or higher
- pip

### Install

```bash
pip install -e .
```

Or install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Run the Simulator

```bash
python main.py --instructions files/instruction_input.txt --memory files/data_input.txt
```

With verbose output (PC and registers for each instruction):

```bash
python main.py --instructions files/instruction_input.txt --memory files/data_input.txt --verbose
```

Output final state as JSON:

```bash
python main.py --instructions files/instruction_input.txt --memory files/data_input.txt --output json
```

### Run Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=cpu --cov=utils
```

---

## Docker

Build the image:

```bash
docker build -t cpu_simulator .
```

Run the simulator:

```bash
docker run --rm cpu_simulator --instructions files/instruction_input.txt --memory files/data_input.txt
```

To mount local files:

```bash
docker run --rm -v ${PWD}/files:/cpu_simulator/files cpu_simulator --instructions files/instruction_input.txt --memory files/data_input.txt
```

Run tests:

```bash
docker run --rm cpu_simulator pytest
```

---

## File Formats

### Memory File

- Format: `address,value` (one pair per line)
- Address: **binary string** (e.g. `00000000`, `00000100`)
- Value: decimal integer

Example:

```
00000000,7
00000100,8
```

### Instruction File

- One instruction per line
- Use spaces or commas to separate operands
- Lines starting with `#` and empty lines are ignored

Example:

```
LW R1, 0(R4)
LW R2, 4(R4)
ADD R3, R1, R2
SW R3, 0(R4)
HALT
```

---

## Local Development

1. Create a virtual environment:

       python -m venv venv

2. Activate it:

   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install: `pip install -e .`

4. Run tests: `pytest`
