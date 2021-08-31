import sys
import os

# Extract name of file to be translated
dir = 0
filepath = sys.argv[1]
filename = filepath.split("/")[-1].partition(".")[0]
vmfiles = [filepath]
if not filepath[-3:] == ".vm":
    dir = 1
    vmfiles = [file for file in os.listdir(filepath) if file[-3:] == ".vm"]
    vmfilenames = [file[:-3] for file in vmfiles]
current_file = ""

# map segments 
segments = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": 5}
VMCommands = []

# Create a list containing commands
if dir == 0:
    outputfile = filepath[:-3] + ".asm"
    with open(filepath) as vm:
        for line in vm:
            line = line.partition('//')[0]
            line = line.rstrip()
            if line:
                line = line.split(" ")
                VMCommands.append(line)

else:
    dir = 1
    outputfile = filepath + "/" + filename + ".asm"
    for file in vmfiles:
        with open(filepath + "/" + file) as vm:
            for line in vm:
                line = line.partition('//')[0]
                line = line.rstrip()
                if line:
                    line = line.split(" ")
                    VMCommands.append(line)

jump_counter = 0
return_counter = 0
f = open(outputfile, "w")

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
        f.write(f"@{current_file}.{i}\nD=M\n")
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
        # RAM[addr]=segment+i
        f.write(f"@{segments[segment]}\nD=A\n@{i}\nD=D+A\n@addr\nM=D\n")
        # SP--
        f.write(f"@SP\nM=M-1\n")
        # *addr=*SP
        f.write("@SP\nA=M\nD=M\n@addr\nA=M\nM=D\n")
    
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
        f.write(f"@{current_file}.{i}\nM=D\n")

    else:
        # RAM[addr]=segment+i
        f.write(f"@{segments[segment]}\nD=M\n@{i}\nD=D+A\n@addr\nM=D\n")
        # SP--
        f.write(f"@SP\nM=M-1\n")
        # *addr=*SP
        f.write("@SP\nA=M\nD=M\n@addr\nA=M\nM=D\n")
    
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

def writeIf(label):
    f.write(f"// if-goto {label}\n")
    # SP--
    f.write("@SP\nM=M-1\n")
    # D=*SP
    f.write("A=M\nD=M\n")
    # jump if *SP!=0
    f.write(f"@{label}\nD;JNE\n")

def writeGoto(label):
    f.write(f"// goto {label}\n@{label}\n0;JMP\n")

def writeLabel(label):
    f.write(f"// label {label}\n({label})\n")

def writeCall(functionName, nArgs, return_counter):
    f.write(f"// call {functionName} {nArgs}\n")
    # push return-address
    f.write(f"@return{functionName}{return_counter}\nD=A\n")
    f.write("@SP\nA=M\nM=D\n")
    f.write("@SP\nM=M+1\n")
    # push LCL
    f.write(f"@LCL\nD=M\n")
    f.write("@SP\nA=M\nM=D\n")
    f.write("@SP\nM=M+1\n")
    # push ARG
    f.write(f"@ARG\nD=M\n")
    f.write("@SP\nA=M\nM=D\n")
    f.write("@SP\nM=M+1\n")
    # push THIS
    f.write(f"@THIS\nD=M\n")
    f.write("@SP\nA=M\nM=D\n")
    f.write("@SP\nM=M+1\n")
    # push THAT
    f.write(f"@THAT\nD=M\n")
    f.write("@SP\nA=M\nM=D\n")
    f.write("@SP\nM=M+1\n")
    # ARG = SP - nArgs - 5
    f.write(f"@SP\nD=M\n@{nArgs}\nD=D-A\n@5\nD=D-A\n")
    f.write("@ARG\nM=D\n")
    # LCL = SP
    f.write("@SP\nD=M\n")
    f.write("@LCL\nM=D\n")
    # goto functionName
    f.write(f"@{functionName}\n0;JMP\n")
    # (return-address)
    f.write(f"(return{functionName}{return_counter})\n")
    return_counter += 1
    return return_counter

def writeFunction(functionName, nVars, current_file):

    f.write(f"// function {functionName} {nVars}\n")

    # declare label
    f.write(f"({functionName})\n")

    # push constant 0 nVars times
    for _ in range(int(nVars)):
        f.write(f"@0\nD=A\n")
        f.write("@SP\nA=M\nM=D\n")
        f.write("@SP\nM=M+1\n")

    current_file = functionName.partition(".")[0]
    return current_file

def writeReturn():
    f.write("// return\n")
    # FRAME = LCL
    f.write("@LCL\nD=M\n@FRAME\nM=D\n")
    # RET = *(FRAME-5)
    f.write("@5\nD=D-A\nA=D\nD=M\n@RET\nM=D\n")
    # *ARG = pop()
    f.write(f"@SP\nM=M-1\n")
    f.write("A=M\nD=M\n@ARG\nA=M\nM=D\n")
    # SP = ARG+1
    f.write("@ARG\nD=M+1\n@SP\nM=D\n")
    # THAT = *(FRAME-1)
    f.write("@FRAME\nD=M\n@1\nD=D-A\nA=D\nD=M\n@THAT\nM=D\n")
    # THIS = *(FRAME-2)
    f.write("@FRAME\nD=M\n@2\nD=D-A\nA=D\nD=M\n@THIS\nM=D\n")
    # ARG = *(FRAME-3)
    f.write("@FRAME\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n")
    # LCL = *(FRAME-4)
    f.write("@FRAME\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n")
    # goto RET
    f.write("@RET\nA=M\n0;JMP\n")

def writeInit():
    # SP=256
    f.write("// Bootstrap\n@256\nD=A\n@SP\nM=D\n")
    # call Sys.init
    writeCall("Sys.init", "0", 0)

if len(vmfiles) > 1:
    writeInit()

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

    elif command[0] == "label":
        writeLabel(command[1])

    elif command[0] == "goto":
        writeGoto(command[1])

    elif command[0] == "if-goto":
        writeIf(command[1])

    elif command[0] == "call":
        return_counter = writeCall(command[1], command[2], return_counter)  # The problem solved here was correctly matching labels
                                                                            # generated by the call command. We had to disambiguate 
    elif command[0] == "function":                                          # between several return labels generated by the same function
        current_file = writeFunction(command[1], command[2], current_file)

    elif command[0] == "return":
        writeReturn()

    jump_counter += 1

f.close()