# CPU Simulator – Improvement Plan

This document outlines a structured improvement plan for the MIPS-inspired CPU simulator, based on a full codebase review.

---

## Guiding Principles

- **Modular:** Clear separation of concerns; components (CPU, memory, cache) are independent and composable.
- **Testable:** Core logic raises exceptions instead of exiting; no hidden side effects; injectable dependencies where useful.
- **Readable:** Consistent naming, clear docstrings, minimal nesting; code explains intent.
- **Reusable:** Components can be used in other contexts (e.g. cache with different memory backends) without tight coupling.
- **PEP-compliant:** Follow PEP 8 (style), PEP 257 (docstrings), and relevant PEPs for project structure and packaging.

---

## Executive Summary

The project is a solid educational CPU simulator with a clean architecture. Key strengths include a well-defined ISA, unit and integration tests, and CI/CD (GitHub Actions, Docker). The main gaps are: **cache is never used for memory access**, README vs. actual structure mismatch, some code quality issues, and missing tooling (coverage, linting in CI). **Makefile support will be removed**; use direct commands and scripts instead.

---

## 1. Critical Fixes (High Priority)

### 1.1 Cache Not Wired to Memory Access

**Issue:** The `Cache` class exists and can be enabled via `CACHE 1`, but **LW and SW always access `self.memory` directly**. When the cache is enabled, memory operations bypass it entirely.

**Location:** `cpu/cpu.py` – `execute_memory_action()`

```python
# Current (wrong): always uses memory directly
if code == 'LW':
    self.registers[rt_idx] = self.memory.load_word(address)
elif code == 'SW':
    self.memory.store_word(address, self.registers[rt_idx])
```

**Fix:** Route LW/SW through the cache when `self.cache` is not `None`:

- **LW:** If cache enabled → `self.cache.read(address, self.memory)`; else → `self.memory.load_word(address)`
- **SW:** If cache enabled → `self.cache.write(address, value, self.memory)`; else → `self.memory.store_word(address, value)`

Note: `cache.read()` returns `list[int]` (one element); adjust for that.

---

### 1.2 Cache Address Calculation Bug (Suspected)

**Issue:** In `cache.py`, `replace_block()` and `flush()` use:
```python
base_address = (block.tag << 11) | (index << 6)
```

With `BLOCK_SIZE=16` (→ 4 offset bits) and 64 cache lines (→ 6 index bits), the correct reconstruction is:
```python
base_address = (tag << (offset_bits + index_bits)) | (index << offset_bits)
```
i.e. `(tag << 10) | (index << 4)`.

The current `<< 11` and `<< 6` may misalign addresses and cause incorrect cache behavior.

**Action:** Make address encoding derive from `offset_bits` and `index_bits` instead of hardcoded shifts; add tests for `replace_block` and `flush` with varied addresses.

---

## 2. Documentation and Consistency

### 2.1 README vs. Project Layout

**Issue:** The README describes:
```
cpu-simulator/
  src/
    cpu.py, memory.py, cache.py, cli.py
```

**Actual layout:**
```
cpu_simulator/
  cpu/
    cpu.py, memory_bus.py, cache.py
  main.py (no separate cli.py)
  utils/
    constants.py
```

**Fix:** Update the README to match the real structure. Consider mentioning:
- `cpu/` (CPU, cache, memory bus)
- `utils/constants.py`
- `main.py` as entry point (no separate `cli.py`)
- **Remove all Makefile usage documentation**; document direct commands (`docker build`, `python main.py`, `pytest`) instead.

### 2.2 README File Format vs. Implementation

**Issue:** README says memory format is `address,value` with binary addresses, but `_load_memory` uses `int(entry[0], 2)` only for binary. No explicit support for decimal addresses (e.g. `256,8`).

**Action:** Document that addresses are binary (e.g. `00000100`), or support both (decimal with `0x` / `0b` prefix) and document it.

---

## 3. Code Quality

### 3.1 Remove Dead Code

- **cpu/cpu.py:** Delete the commented-out `_load_instructions` (lines ~47–63).
- **tests/unit/test_cpu_utils.py:** Duplicate memory-bus tests (lines 71–181) exist in `test_memory_bus.py`. Remove or consolidate.

### 3.2 Error Handling and Exit Strategy

**Issue:** CPU methods call `sys.exit(1)` on errors, which:
- Makes testing awkward (must catch `SystemExit`)
- Couples core logic to process exit

**Fix:** Prefer raising exceptions (e.g. `FileNotFoundError`, `ValueError`) and handle them in `main.py` only. This improves testability and separation of concerns.

### 3.3 Validation Exceptions

**Issue:** `_validate_offset` raises generic `Exception` instead of `ValueError` for invalid offsets.

**Fix:** Raise `ValueError` for invalid values. Use `TypeError` only for type errors.

### 3.4 Logging and Debug Output

**Issue:** `execute_instructions()` always does:
```python
print(f"PC: {self.pc} | Instruction: {instr}")
print(f"Registers before: {self.registers}")
...
print(f"Registers after: {self.registers}\n")
```

**Fix:** Gate verbose output behind a `--verbose` or `--debug` flag, or route it through logging so tests and production runs are not flooded.

---

## 4. Testing

### 4.1 Test Organization

- **test_cpu_utils.py:** Contains both CPU utility tests and duplicate `MemoryBus` tests. Split or move memory-bus tests to `test_memory_bus.py` and keep CPU utilities focused.

### 4.2 Coverage and Gaps

- Add `pytest-cov` to dependencies.
- Add a CI coverage step; document `pytest --cov=cpu --cov=utils` in README.
- Cover:
  - Cache integration when cache is enabled (LW/SW via cache).
  - Instruction parsing edge cases (e.g. malformed `offset(Rs)`).
  - HALT on invalid opcode and error paths in `execute_instructions`.

### 4.3 Integration Tests with Cache

- Add integration tests that enable the cache and run LW/SW, then verify correctness of register and memory state.
- Verify cache flush semantics (CACHE 2) before and after memory writes.

---

## 5. Configuration and Constants

### 5.1 Cache Block Size Mismatch

**Issue:** `utils/constants.py` has `BLOCK_SIZE = 16`, but `cache.py` Block docstring says "8-word block."

**Fix:** Align comment and constant (use `BLOCK_SIZE` consistently).

### 5.2 Memory Size Semantics

**Issue:** `MEMORY_SIZE = 1024 * 1024` – documentation says 1MB addressable memory. Need a clear definition: byte-addressed vs. word-addressed, and what each storage slot represents.

**Action:** Add short comments in `constants.py` and/or README.

---

## 6. Python and Tooling

### 6.1 pyproject.toml vs. requirements.txt

- `pyproject.toml` already lists pytest; `requirements.txt` also lists it.
- Prefer a single source of truth. Use `pyproject.toml` and, if needed, generate `requirements.txt` from it.

### 6.2 Python Version Consistency

- `pyproject.toml`: `requires-python = ">=3.10"`
- CI and Docker: Python 3.13.9
- README: mentions Python 3.13.9

**Action:** Decide minimum supported version (e.g. 3.10) and document it. Ensure CI tests against at least 3.10 and 3.13.

### 6.3 CI Improvements

- **Branches:** Workflows trigger on `main`; repo default may be `master`. Align `on.push.branches` with the actual default branch.
- **Linting:** `pyproject.toml` configures flake8 and black but CI does not run them. Add:
  ```yaml
  - run: pip install black flake8
  - run: black --check .
  - run: flake8 .
  ```
- **Install method:** Prefer `pip install -e .` or `pip install .` from the project root for a single, consistent environment.

### 6.4 Remove Makefile Support

**Decision:** Remove the Makefile entirely. Do not maintain Make targets or cross-platform Make logic.

**Rationale:** Reduces maintenance, avoids Windows/Unix script-path differences, and keeps the project simple.

**Replacements (document in README):**
- Build Docker image: `docker build -t cpu_simulator .`
- Run simulator: `python main.py --instructions files/... --memory files/...`
- Run tests: `pytest` (or `python -m pytest`)
- Run tests with coverage: `pytest --cov=cpu --cov=utils` (after adding pytest-cov)
- Optional: a simple `scripts/run.sh` or `scripts/test.sh` if desired, but prefer standard commands

---

## 7. Modularity, Testability, Readability, Reusability

### 7.1 Modularity

**Current issues:**
- `CPU` creates and owns `MemoryBus` and `Cache` directly; no dependency injection.
- File I/O, validation, and execution are mixed in `CPU`; loading logic is not easily reusable.

**Improvements:**
- Allow `CPU` to accept optional `memory` and `cache_factory` (or similar) for testing and reuse.
- Extract instruction loading/parsing into a small module (e.g. `utils/loader.py`) that returns structured data; `CPU` consumes that data.
- Keep `MemoryBus` and `Cache` as standalone components that communicate via clear interfaces.

### 7.2 Testability

**Current issues:**
- `sys.exit(1)` in core code forces `pytest.raises(SystemExit)` or similar.
- Verbose `print()` in `execute_instructions` clutters test output unless captured.
- Some logic depends on file paths; tests use real files under `files/`.

**Improvements:**
- Raise exceptions instead of `sys.exit`; handle exit only in `main.py`.
- Gate all console output behind a flag or logging level; tests run with output suppressed.
- Prefer `tmp_path` and in-memory data for tests where possible; keep file-based tests only where file behavior is under test.

### 7.3 Readability

**Current issues:**
- Inconsistent style (e.g. `#imports` comment, mixed spacing).
- Some methods are long; dispatch and execution could be split for clarity.
- Magic numbers (e.g. `registers[7]` for JAL) should use named constants.

**Improvements:**
- Run `black` and `isort`; fix any remaining style issues.
- Use constants (e.g. `LINK_REGISTER = 7`) instead of literals.
- Break long methods into smaller, well-named helpers.
- Add/improve docstrings for public methods and modules.

### 7.4 Reusability

**Current issues:**
- `Cache` is tied to `MemoryBus`; could be generalized to any backend with `load_word`/`store_word`.
- Instruction format (comma vs space, parsing rules) is embedded in `CPU`; not reusable for other tools.

**Improvements:**
- Define a simple `MemoryBackend` protocol (load_word, store_word); `MemoryBus` and any mock implement it.
- Consider an `Instruction` dataclass or similar so parsing produces a shared representation usable by other tools.

---

## 8. PEP Adherence

### 8.1 PEP 8 – Style

- Run `black` (line length 88 per pyproject.toml) and `flake8`.
- Fix: import order (stdlib, third-party, local); no trailing whitespace; consistent naming (`snake_case` for functions/variables, `CamelCase` for classes).
- Remove `#imports`-style comments; use proper grouping per PEP 8.

### 8.2 PEP 257 – Docstrings

- All public modules, classes, and functions must have docstrings.
- Use one-line summary where sufficient; multi-line for complex logic.
- Prefer `"""Summary. Optional details."""` style.

### 8.3 PEP 484 / 585 – Type Hints

- Add type hints to public function signatures and, where useful, to variables.
- Use `list[str]` instead of `List[str]` (Python 3.9+).

### 8.4 PEP 517 / 518 – Build and Packaging

- `pyproject.toml` already uses `setuptools`; ensure `[project]` metadata is complete (authors, license, classifiers if desired).
- Consider `pip install -e .` as the recommended install method in README.

### 8.5 Import Layout

- Group: standard library → third-party → local.
- One import per line for `from x import a, b` when long; blank line between groups.
- Use `isort` with `profile = "black"` (already in pyproject.toml).

---

## 9. Architecture and Extensibility

### 9.1 CLI Options

- Add `--verbose` / `--quiet` to control logging and register output.
- Consider `--no-color` for CI or non-TTY environments (if color is ever added).

### 9.2 Instruction Set

- README lists `NOP` implicitly; it is implemented but not in the ISA table. Either add it or note it as an extension.

### 9.3 Output Format

- Consider optional structured output (e.g. JSON) for programmatic use or automated checks.

---

## 10. Suggested Implementation Order

| Phase | Items | Effort |
|-------|-------|--------|
| 1     | Wire cache to LW/SW; fix cache address formula | Medium |
| 2     | Add integration tests for cache; fix duplicate tests | Low |
| 3     | Remove dead code; replace `sys.exit` with exceptions | Low |
| 4     | Add `--verbose` flag; move prints to logging | Low |
| 5     | Update README layout and file formats | Low |
| 6     | Add flake8/black to CI; add coverage | Low |
| 7     | **Remove Makefile**; document commands in README | Low |
| 8     | Refactor for modularity (DI, loaders); add PEP-compliant docstrings and type hints | Medium |
| 9     | Optional: structured output, extended ISA docs | Low |

---

## 11. Out of Scope (Future Ideas)

- More cache policies (e.g. write-through).
- Instruction-level tracing / debugging mode.
- Interactive or step-through execution.
- Assembly parser for labels (e.g. for J/BNE).

---

*Plan created from full codebase review. Last updated: 2025-02-19*
