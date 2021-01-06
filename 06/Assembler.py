import sys

destinations={'':'000','M':'001','D':'010','MD':'011',
      'A':'100','AM':'101','AD':'110','AMD':'111'}
jumps={'':'000','JGT':'001','JEQ':'010','JGE':'011',
      'JLT':'100','JNE':'101','JLE':'110','JMP':'111'}
computations={'0':'0101010','1':'0111111','-1':'0111010','D':'0001100',
      'A':'0110000','M':'1110000','!D':'0001101','!A':'0110001',
      '!M':'1110001','-D':'0001111','-A':'0110011','-M':'1110011',
      'D+1':'0011111','A+1':'0110111','M+1':'1110111','D-1':'0001110',
      'A-1':'0110010','M-1':'1110010','D+A':'0000010','D+M':'1000010',
      'D-A':'0010011','D-M':'1010011','A-D':'0000111','M-D':'1000111',
      'D&A':'00000000','D&M':'1000000','D|A':'0010101','D|M':'1010101'}
symbols={'SP':0,'LCL':1,'ARG':2,'THIS':3,'THAT':4,'SCREEN':16384,'KBD':24576,
         'R0':0,'R1':1,'R1':1,'R2':2,'R3':3,'R4':4,'R5':5,'R6':6,'R7':7,
         'R8':8,'R9':9,'R10':10,'R11':11,'R12':12,'R13':13,'R14':14,'R15':15}


class Parser:

    def __init__(self, address):
        file = open(address, "r")
        instructions = file.read().split("\n")
        instructions = [line for line in instructions if line[0:2] != "//" and line != ""]
        file.close()
        instructions = [line.split("//")[0].strip() for line in instructions]
        self.instructions = instructions
        self.reset()
        self.n = 16

    def reset(self):
        self.c = 0
        self.current = self.instructions[self.c]

    def hasMoreCommands(self):
        return not len(self.instructions) == self.c
        
    def advance(self):
        self.c += 1
        try:
            self.current = self.instructions[self.c]
        except IndexError:
            pass

    def commandType(self):
        if self.current[0] == "@":
            return "A_COMMAND"
        elif self.current[0] == "(":
            return "L_COMMAND"
        else:
            return "C_COMMAND"
    
    def symbol(self):
        if self.commandType() == "A_COMMAND":
            return self.current[1:]
        elif self.commandType() == "L_COMMAND":
            return self.current[1:-1] 
        else:
            return "Not an A or L command"

    def dest(self):
        if self.commandType() == "C_COMMAND" and "=" in self.current:
            return self.current.split("=")[0]
        else:
            return ""

    def comp(self):
        if self.commandType() == "C_COMMAND":
            if "=" in self.current and ";" in self.current:
                return self.current.split(";")[0].split("=")[1]
            elif "=" in self.current:
                return self.current.split("=")[1]
            else:
                return self.current.split(";")[0]
        else:
            return ""

    def jump(self):
        if self.commandType() == "C_COMMAND" and ";" in self.current:
            return self.current.split(";")[1]
        else:
            return ""

    def code(self):
        if self.commandType() == "A_COMMAND":
            try:
                return format(int(self.symbol()), '016b')
            except ValueError:
                if self.symbol() in symbols.keys():
                    return format(symbols[self.symbol()], '016b')
                else:
                    symbols[self.symbol()] = self.n
                    self.n += 1
                    return format(self.n - 1, '016b')
        elif self.commandType() == "C_COMMAND":
            return "111" + computations[self.comp()] + destinations[self.dest()] + jumps[self.jump()]

    def symbolTable(self):
        if self.commandType() == "L_COMMAND":
            symbols[self.symbol()] = self.c
            self.instructions.remove(self.current)
            self.c -= 1


if __name__ == "__main__":

    parser = Parser(sys.argv[1])

    binary_instructions = ""

    while parser.hasMoreCommands():
        parser.symbolTable()
        parser.advance()

    parser.reset()

    while parser.hasMoreCommands():
        binary_instructions += parser.code() + "\n"
        parser.advance()

    file = open(sys.argv[2], "w")
    file.write(binary_instructions)
    file.close()