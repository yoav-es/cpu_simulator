# 🧠 CPU Simulator (MIPS-Inspired)

This project simulates a simplified CPU architecture in Python, modeling core components like the CPU, memory bus, and cache. It’s designed for educational and portfolio purposes — not for real embedded hardware — but it demonstrates key architectural concepts and system-level interactions.

---

## 🚀 Features

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

### Instruction Set Architecture (ISA)

| Instruction | Operands         | Meaning                                      |
|-------------|------------------|----------------------------------------------|
| `ADD`       | Rd, Rs, Rt       | Rd ← Rs + Rt                                 |
| `ADDI`      | Rt, Rs, immd     | Rt ← Rs + immd                               |
| `SUB`       | Rd, Rs, Rt       | Rd ← Rs - Rt                                 |
| `SUBI`      | Rd, Rs, immd     | Rd ← Rs - immd                               | 
| `SLT`       | Rd, Rs, Rt       | Rd ← (Rs < Rt) ? 1 : 0                       |
| `BNE`       | Rs, Rt, offset   | If Rs ≠ Rt → PC ← (PC + 4) + offset × 4      |
| `J`         | target           | PC ← target × 4                              |
| `JAL`       | target           | R7 ← PC + 4; PC ← target × 4                 |
| `LW`        | Rt, offset(Rs)   | Rt ← MEM[Rs + offset]                        |
| `SW`        | Rt, offset(Rs)   | MEM[Rs + offset] ← Rt                        |
| `CACHE`     | Code             | 0 = off, 1 = on, 2 = flush                   |
| `HALT`      | ;                | Terminate execution                          |

---

## 📦 How It Works

1. **Input Files**
   - Instruction file: contains ISA commands
   - Memory file: initializes memory with address-value pairs

2. **Execution Flow**
   - CPU loads instructions and memory
   - Instructions are parsed and executed sequentially
   - Cache intercepts memory access and manages block-level data
   - Console output logs each stage of execution

3. **CLI Interface**
   - Uses `argparse` for command-line arguments
   - Optional: wrap with `click` for enhanced UX

---

