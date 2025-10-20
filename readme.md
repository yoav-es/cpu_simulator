Project Ideas
While it is completely up to you to decide what to implement for your CPU simulator, here are some ideas for what your program could accomplish:

Create classes that mimic the functionalities of a CPU, cache, and memory bus
Fetch and parse instructions from an input file
Fetch and parse initialization values for the Memory Bus from a separate input file
Send CPU instructions and initial Memory Bus values to the CPU and Memory Bus, respectively
Provide console output to the user documenting the stages of input processing
Implement an ISA that can handle MIPS Instructions such as the following:

Instruction	Operand	Meaning
ADD	Rd, Rs, Rt	Rd <- Rs + Rt;
ADDI	Rt, Rs, immd	Rt <- Rs + immd
SUB	Rd, Rs, Rt	Rd <- Rs - Rt
SLT	Rd, Rs, Rt	If (Rs < Rt) then Rd <- 1 else Rd <- 0
BNE	Rs, Rt, offset	If (Rs not equal Rt) then PC <- (PC + 4) + offset * 4
J	target	PC <- target * 4
JAL	target	R7 <- PC + 4; PC <- target *4
LW	Rt, offset(Rs)	Rt <- MEM[Rs + offset]
SW	Rt, offset(Rs)	MEM[Rs + offset] <- Rt
CACHE	Code	Code = 0(Cache off) Code = 1(Cache on), Code = 2(Flush cache)
HALT	;	Terminate Execution

"✅ Today’s Progress
- CPU class with:
- Program counter
- Register file
- Instruction/data loading
- Instruction parsing with validation
- Memory input format locked (binary address, decimal value)
- HALT logic scoped for future control flow

🔜 Tomorrow’s Goals
- Implement execute_instruction(opcode, args) method
- Design Memory class:
- Address-value mapping
- Read/write interface
- Design Cache class:
- Basic structure (e.g., direct-mapped or associative)
- Hit/miss logic
- Integration with memory

- decode_address()
- hit_or_miss()
- read() and write() with mocked memory
- evict_and_get_block() logic

🔗 Integration Testing
- Simulate full read/write cycles
- Validate memory state after flush
- Test cache hit/miss behavior over sequences

🖥️ Terminal App Packaging
- Use argparse for CLI arguments
- Optionally wrap with click for nicer UX
- Add a main() function that runs the simulation loop
