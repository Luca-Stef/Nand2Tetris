import sys

# Extract name of file to be translated
filepath = sys.argv[1][:-3]
filename = filepath.split("/")[-1]

# map segments 
segments = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": 5}

# Create a list structure containing commands
with open(sys.argv[1]) as f:
    VMCommands = []
    for line in f:
        line = line.partition('//')[0]
        line = line.rstrip()
        if line:
            line = line.split(" ")
            VMCommands.append(line)

def push(segment, i):
    """
    Translate push segment address command to assembly language
    """
    f.write(f"// push {segment} {i}\n")
    if segment == "constant":
        # D=i
        f.write(f"@{i}\nD=A\n")
        # *SP=D
        f.write("@SP\nA=M\nM=D\n")
        # SP++
        f.write("@SP\nM=M+1\n")

    elif segment == "temp":
        # D=RAM[5+i]
        f.write(f"@{i}\nD=A\n@5\nA=D+A\nD=M\n")
        # *SP=D
        f.write("@SP\nA=M\nM=D\n")
        # SP++
        f.write("@SP\nM=M+1\n")

    elif segment == "pointer":

        if i == "0":
            # D=THIS
            f.write(f"@THIS\nD=M\n")    
        else:
            # D=THAT
            f.write(f"@THAT\nD=M\n")    
        
        # *SP=D
        f.write("@SP\nA=M\nM=D\n")
        # SP++
        f.write("@SP\nM=M+1\n")

    elif segment == "static":
        # D=*filename.i
        f.write(f"@{filename}.{i}\nD=M\n")
        # *SP=D
        f.write("@SP\nA=M\nM=D\n")
        # SP++
        f.write("@SP\nM=M+1\n")

    else:
        # D=i
        f.write(f"@{i}\nD=A\n")
        # D=RAM[segment+i]
        f.write(f"@{segments[segment]}\nA=D+M\nD=M\n")
        # *SP=D
        f.write("@SP\nA=M\nM=D\n")
        # SP++
        f.write("@SP\nM=M+1\n")
    
    return

def pop(segment, i):
    """
    Translate pop segment address command to assembly language
    """
    f.write(f"// pop {segment} {i}\n")

    if segment == "temp":
        # RAM[R13]=segment+i
        f.write(f"@{segments[segment]}\nD=A\n@{i}\nD=D+A\n@R13\nM=D\n")
        # SP--
        f.write(f"@SP\nM=M-1\n")
        # *addr=*SP
        f.write("@SP\nA=M\nD=M\n@R13\nA=M\nM=D\n")
    
    elif segment == "pointer":
        # SP--
        f.write(f"@SP\nM=M-1\n")
        # D=*SP
        f.write(f"A=M\nD=M\n")
    
        if i == "0":
            # THIS=D
            f.write(f"@THIS\nM=D\n")
        else:
            # THAT=D
            f.write(f"@THAT\nM=D\n")
    
    elif segment == "static":
        # SP--
        f.write(f"@SP\nM=M-1\n")
        # D=*SP
        f.write(f"A=M\nD=M\n")
        # *filename.i=D
        f.write(f"@{filename}.{i}\nM=D\n")

    else:
        # RAM[R13]=segment+i
        f.write(f"@{segments[segment]}\nD=M\n@{i}\nD=D+A\n@R13\nM=D\n")
        # SP--
        f.write(f"@SP\nM=M-1\n")
        # *addr=*SP
        f.write("@SP\nA=M\nD=M\n@R13\nA=M\nM=D\n")
    
    return

def add():
    """
    Translate add to assembly language
    """
    # SP--
    f.write("// add\n@SP\nM=M-1\n")
    # D=*SP
    f.write("A=M\nD=M\n")
    # SP--
    f.write("@SP\nM=M-1\n")
    # *SP=D+*SP
    f.write("A=M\nM=D+M\n")
    # SP++
    f.write("@SP\nM=M+1\n")

def sub():
    """
    Translate sub to assembly language
    """
    # SP--
    f.write("// sub\n@SP\nM=M-1\n")
    # D=*SP
    f.write("A=M\nD=M\n")
    # SP--
    f.write("@SP\nM=M-1\n")
    # *SP=*SP-D
    f.write("A=M\nM=M-D\n")
    # SP++
    f.write("@SP\nM=M+1\n")

def neg():
    """
    Translates neg into assembly language
    """
    # SP--
    f.write("// neg\n@SP\nM=M-1\n")
    # *SP=-*SP
    f.write("A=M\nM=-M\n")
    # SP++
    f.write("@SP\nM=M+1\n")

def lt(jc):
    """
    Translate lt to assembly language
    """
    # SP--
    f.write("// lt\n@SP\nM=M-1\n")
    # D=*SP
    f.write("A=M\nD=M\n")
    # SP--
    f.write("@SP\nM=M-1\n")
    # D=*SP-D; (*SP<D) if D is negative, write true
    f.write("A=M\nD=M-D\n")
    # Write True
    f.write("M=-1\n")
    f.write(f"@JUMP_{jc}\n")
    f.write("D;JLT\n")
    # Write False
    f.write("@SP\nA=M\nM=0\n")
    f.write(f"(JUMP_{jc})\n")
    # SP++
    f.write("@SP\nM=M+1\n")

def gt(jc):
    """
    Translate gt to assembly language
    """
    # SP--
    f.write("// gt\n@SP\nM=M-1\n")
    # D=*SP
    f.write("A=M\nD=M\n")
    # SP--
    f.write("@SP\nM=M-1\n")
    # D=*SP-D; (*SP<D) if D is positive, write true
    f.write("A=M\nD=M-D\n")
    # Write True
    f.write("M=-1\n")
    f.write(f"@JUMP_{jc}\n")
    f.write("D;JGT\n")
    # Write False
    f.write("@SP\nA=M\nM=0\n")
    f.write(f"(JUMP_{jc})\n")
    # SP++
    f.write("@SP\nM=M+1\n")

def eq(jc):
    """
    Translate eq to assembly language
    """
    # SP--
    f.write("// eq\n@SP\nM=M-1\n")
    # D=*SP
    f.write("A=M\nD=M\n")
    # SP--
    f.write("@SP\nM=M-1\n")
    # D=*SP-D; (*SP<D) if D is zero, write true
    f.write("A=M\nD=M-D\n")
    # Write True
    f.write("M=-1\n")
    f.write(f"@JUMP_{jc}\n")
    f.write("D;JEQ\n")
    # Write False
    f.write("@SP\nA=M\nM=0\n")
    f.write(f"(JUMP_{jc})\n")
    # SP++
    f.write("@SP\nM=M+1\n")

def write_and():
    """
    Translate and to assembly language
    """
    # SP--
    f.write("// and\n@SP\nM=M-1\n")
    # D=*SP
    f.write("A=M\nD=M\n")
    # SP--
    f.write("@SP\nM=M-1\n")
    # *SP=*SP&D
    f.write("A=M\nM=D&M\n")
    # SP++
    f.write("@SP\nM=M+1\n")

def write_or():
    """
    Translate or to assembly language
    """
    # SP--
    f.write("// or\n@SP\nM=M-1\n")
    # D=*SP
    f.write("A=M\nD=M\n")
    # SP--
    f.write("@SP\nM=M-1\n")
    # *SP=*SP|D
    f.write("A=M\nM=D|M\n")
    # SP++
    f.write("@SP\nM=M+1\n")

def write_not():
    """
    Translate not to assembly language
    """
    # SP--
    f.write("// not\n@SP\nM=M-1\n")
    # *SP=!*SP
    f.write("A=M\nM=!M\n")
    # SP++
    f.write("@SP\nM=M+1\n")

f = open(f"{filepath}.asm", "a")
jump_counter = 0

for command in VMCommands:

    if command[0] == "push":
        push(command[1], command[2]) 

    if command[0] == "pop":
        pop(command[1], command[2])

    elif command[0] == "add":
        add()

    elif command[0] == "sub":
        sub()

    elif command[0] == "neg":
        neg()

    elif command[0] == "lt":
        lt(jump_counter)
    
    elif command[0] == "gt":
        gt(jump_counter)

    elif command[0] == "eq":
        eq(jump_counter)

    elif command[0] == "and":
        write_and()

    elif command[0] == "or":
        write_or()

    elif command[0] == "not":
        write_not()

    jump_counter += 1

f.close()