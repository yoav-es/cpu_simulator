# 🧠 CPU Simulator (MIPS-Inspired)

This project simulates a simplified CPU architecture in Python, modeling core components like the CPU, memory bus, and cache. Its primary goal is to mimic the behavior of a MIPS-like processor, providing a hands-on environment to explore instruction execution, memory access, and basic control flow in a RISC-style architecture.
---

## 🚀 Features

### 🧩 CPU Core
- Program counter and register file
- Instruction parsing and execution
- HALT logic and control flow

### 🗄️ Memory Bus
- 1MB addressable memory
- Word-level read/write interface
- Input file support for memory initialization

### 🧮 Cache System
- Direct-mapped cache with block-based storage
- Hit/miss detection and block replacement
- Write-back policy with flush support

## 📁 Project Structure

```
cpu-simulator/
├── src/
│   ├── cpu.py
│   ├── memory.py
│   ├── cache.py
│   └── cli.py
├── tests/
│   └── test_cpu.py
├── requirements.txt
├── Dockerfile
├── README.md
└── main.py
```

---

## 🧾 Instruction Set Architecture (ISA)

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
| `HALT`      | —                | Terminate execution                           |

---

## ⚙️ How It Works

### 1. Input Files
- **Instruction file**: Contains ISA commands (one per line)
- **Memory file**: Initializes memory with address-value pairs (binary or decimal)

### 2. Execution Flow
- CPU loads instructions and memory
- Instructions are parsed and executed sequentially
- Cache intercepts memory access and manages block-level data
- Console output logs each stage of execution

### 3. CLI Interface
- Uses `argparse` for command-line arguments
- Optional: wrap with `click` for enhanced UX
- To run the simulator with instruction and memory files:

  ```bash
  python main.py --instructions files/instruction_input.txt --memory files/data_input.txt
  ```
---

## 🧪 Testing

- Integration and unit tests using `pytest`
- Test coverage includes CPU execution, cache behavior, and memory access
- Example test: `test_valid_arithmetic_program` validates register and memory state after arithmetic operations

---

## 📁 File Format Notes

### Memory File
- Format: `address,value`
- Example (binary addresses):
```
   00000000,7 
   00000100,8
```

### Instruction File
- Format: one instruction per line
- Example:
```
   LW R1, 0(R4)
   LW R2, 4(R4)
   ADD R3, R1, R2 
   SW R3, 0(R4) 
   HALT
```
---
## 🐳 Docker Usage


To run the CPU simulator using Docker, first build the image from the project root:

```bash
docker build -t cpu_simulator .
```

This creates a Docker image named `cpu_simulator`. You can then run the simulator with command-line arguments:

```bash
docker run --rm cpu_simulator --instructions files/instruction_input.txt --memory files/data_input.txt
```

Make sure the input files are either included in the image or mounted from your host system. To mount files from your local `files/` directory:

```bash
docker run --rm -v ${PWD}/files:/cpu_simulator/files cpu_simulator --instructions files/instruction_input.txt --memory files/data_input.txt
```

To run tests using `pytest`:

```bash
docker run --rm cpu_simulator pytest
```
---

## 🛠️ Makefile Usage


This project includes a Makefile to simplify common tasks like building the Docker image, running the simulator, and executing tests. To use it, make sure you have `make` installed. On Windows, you can install it via Chocolatey (`choco install make`), use Git Bash, or run it from WSL.

To build the Docker image:

```bash
make build
```

To run the simulator with default input files:

```bash
make run
```

To run the simulator with custom input files, pass them as arguments:

```bash
make run INSTRUCTIONS=files/custom_instructions.txt MEMORY=files/custom_memory.txt
```

To mount input files from your local `files/` directory:

```bash
make run-mounted
```

To run the simulator locally with Python:

```bash
make local-run
```

To run tests using pytest inside Docker:

```bash
make test
```

To remove the Docker image:

```bash
make clean
```

You can override any variable defined in the Makefile by passing it on the command line. For example, to use a different instruction file:

```bash
make run INSTRUCTIONS=files/alt_instructions.txt
```

This makes it easy to switch inputs or configurations without editing the Makefile itself.