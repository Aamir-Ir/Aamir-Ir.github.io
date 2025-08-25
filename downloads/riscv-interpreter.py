# README: Look for README (cntrl + F) to find execution instructions. 

class RISC_V_Interpreter:

    ''''
        Intial Constructor Method Used to define the basic instances of the object. 

        ->  RISC_V_Interpreter
            
            1) RISC-V 32 Bit ISA with 32 Registers.
            2) Memory Simulation to showcase how the load/store instructions are handled.
            3) PC used to keep track of the sequential flow of the program along with help with Jump type instructions.
            4) Instruction count used to count the number of instructions. (Since it is a Single Cycle Processor the Cycle Count = Instructions Count and CPI = 1 = IPC).
            5) Recently Added: Labels are stored if a program contains labels in the input. Used mainly for jump instruction programs. 
    '''

    def __init__(self):
        self.registers = {i: 0 for i in range(32)}      # Each Register Declared and Initialized to 0. (All 32 of them).
        self.memory = {}                                # Simulated memory by the end will showcase what was stored in memory by sw instructions and if something is not there it will be removed by lw. This is what happens in RIPES I will mention this int he report.
        self.pc = 0                                     # Program Counter
        self.instrCount = 0                             # Instruction Counter.
        self.labels = {}                                # File Parsing will set this variable.
        
        # All possible instructions that can be dealt with by the RISC_V_Interpreter are stored in a dictionary format with appropriate instance calls to invoke them when parsing.

        self.instructions = {
            "ADD": self.ADD,                            # Addition Instruction.
            "SUB": self.SUB,                            # Subtraction Instruction.
            "LI": self.LI,                              # Load Immediate Instruction.
            "LW": self.LW,                              # Load Word Instruction.
            "SW": self.SW,                              # Store Word Instruction.
            "BEQ": self.BEQ,                            # Branch If Equal Instruction.
            "JAL": self.JAL,                            # Jump And Link Register Instruction.
            "J": self.J                                 # Jump Instruction to a specfic label.
        }

    # Addition Method. RD = R1 + R2.

    def ADD(self, RD, R1, R2):
        self.registers[RD] = self.registers[R1] + self.registers[R2]
    
    # Subtraction Method. RD = R1 - R2.

    def SUB(self, RD, R1, R2):
        self.registers[RD] = self.registers[R1] - self.registers[R2]
    
    # Load Immediate Method. RD = IMM.

    def LI(self, RD, IMM):
        self.registers[RD] = IMM

    # Load Word Method. RD = Base Register (Rbase) + OFFSET.

    def LW(self, RD, Rbase, OFFSET):
        address = self.registers[Rbase] + OFFSET
        self.registers[RD] = self.memory.get(address, 0)
    
    # Store Word Method. In Memory at Base Register (Rbase) + OFFSET store R1.

    def SW(self, R1, Rbase, OFFSET):
        address = self.registers[Rbase] + OFFSET
        self.memory[address] = self.registers[R1]

    # Branch If Equal. IF R1 = R2 Branch.
    
    def BEQ(self, R1, R2, OFFSET):
        if self.registers[R1] == self.registers[R2]:
            print("BEQ condition met (would branch to PC +", OFFSET, ") but executing sequentially.")
            # For this simulation we do not change self.pc.
    
    # Jump And Link Register.

    def JAL(self, *args):

        # Modified to accept either one operand (label only) or two operands (RD and OFFSET)
        
        # Case 1: If a label is given.

        if len(args) == 1:
            OFFSET = args[0]
            RD = 1  # Default link register (RA) if not specified.

        # Case 2: If Two operands are given RD and OFFSET.

        elif len(args) == 2:
            RD, OFFSET = args
        
        # Case 3: Something went wrong in the file input the form must be wrong.

        else:
            raise ValueError("Invalid number of operands for JAL")
        
        # Store return address

        self.registers[RD] = self.pc + 1
        
        # Jump by OFFSET.

        self.pc += OFFSET  
    
    # Jump Instruction.

    def J(self, OFFSET):

        # Case 1: Reset

        if OFFSET == 0:
            
            # Stop the execution by forcing PC to be beyond the program length. I believe this will always work especially since j is at the end of a function.

            self.pc = 10**9

        # Case 2: Continue.

        else:

            # Adjust PC (subtract 1 because execute_program will add 1).

            self.pc += OFFSET - 1

    # Execute the Program Method used to run the RISC_V_Interpreter.

    def execute_program(self, program_code):

        # While the Program Counter has instructions to run keep reading. 

        while self.pc < len(program_code):
            self.instrCount += 1                                                # Reads a line + 1 to the Instruction Count.
            instruction = program_code[self.pc].split()                         # Split the instruction and place into the program code list, while holding the current instruction.
            opcode = instruction[0].upper()                                     # Convert opcode to uppercase for robustness.
            
            # Process operands: try converting to integers; if it fails it then becomes a label as it is not compatible with an integer type.
            
            operands = []

            # Read the instruction.

            for token in instruction[1:]:
            
                # Base Case: We have registers in the instrucitons. 

                try:
                    operand = int(token)

                # Label Case: We have a label as no integers were detected.

                except ValueError:

                    # The OPCODES preceding a label.

                    if opcode in ["BEQ", "JAL", "J"]:
                        operand = self.labels[token] - self.pc

                    # Only OPCODES labels.

                    else:
                        operand = self.labels[token]

                operands.append(operand)
            
            if opcode in self.instructions:
                self.instructions[opcode](*operands)
            
            # Always move to next instruction for sequential execution

            self.pc += 1 

        # Dump final register values that are 0 to make it easy to read.

        print("\nFinal Register State (Only Included Non-Zero Registers):")
        
        for reg, value in self.registers.items():
            if value != 0:
                print(f"R{reg}: {value}")

        # Printing out the state of the memory.

        print("\nMemory State:")
        print(self.memory)

        # Printing out the Execution Metrics.
        #  
        print("\nExecution Metrics:")
        print(f"- Total Instructions Executed: {self.instrCount}")
        print(f"- Total Cycles Used: {self.instrCount}")
        print("- CPI = IPC = 1 (Single Cycle Processor).\n")

# Load Program from the file input. On command terminal type: "filename.txt" (Do not forget the .txt extention)

filename = input("Enter the filename: ")

program_code = []       # Used to store each instruction.
labels = {}             # Used to store labels and mapping them to specific instructions.
current_index = 0

# Expected flow of program.

try:
    
    # Read filename.

    with open(filename, "r") as file:
        textfile_lines = file.readlines()
        
        # Ignore the first line (variable assignment) if needed.
    
        for line in textfile_lines[1:]:
            line = line.strip().strip('",')             #  Remove quotes in the instructions.
            if not line or line == "]":                 #  Remove Brackets in the instructions.
                continue

            line = line.replace(",", "")                # Remove commas from the line.
            
            # If the line is a label (ends with ':'), record its position.

            if line.endswith(":"):
                label_name = line[:-1]
                labels[label_name] = current_index
            else:
                program_code.append(line)
                current_index += 1

    # Print out the summary of what was parsed from the file.
    print("\nSummary of Parsed File (Including Instructions + Labels):")
    print("Parsed Program List:", program_code)
    print("Labels:", labels)

# Errors that are not part of the expected flow of the program.

except FileNotFoundError:
    print(f"Error: The file '{filename}' was not found.")
    exit()
except Exception as e:
    print(f"An error occurred: {e}")
    exit()

# Main of the program think of this as the starting point from the POV of the compiler and run the program.

class_interpreter = RISC_V_Interpreter()              # Declare and intialize the RISC_V_Interpreter.
class_interpreter.labels = labels                     # Send the labels to the interpreter after reading the file.
class_interpreter.execute_program(program_code)       # Actually Execute the code noe.

# README: You have to input a text file with its name: "filename.txt" to run the program. I tested the testcases given on courselink with this method. 