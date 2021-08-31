class CompilationEngine:

    """
    Compilation engine class
    """

    opIndex = {"+": "add\n", "-": "sub\n", "*": "call Math.multiply 2\n", "/": "call Math.divide 2\n", 
                "&amp;": "and\n", "|": "or\n", "&lt;": "lt\n", "&gt;": "gt\n", "=": "eq\n"}
    segmentIndex = {"field": "this", "var": "local", "static": "static", "argument": "argument"}

    def __init__(self, tokenFile, outputFile, symbolTable):

        self.f = outputFile
        self.tokenFile = tokenFile
        self.tokenFile.readline()
        self.currentLine = self.tokenFile.readline()
        self.currentToken = self.currentLine.split()[1]
        self.currentTokenType = self.currentLine.split()[0][1:-1]
        self.symbolTable = symbolTable
        self.whileIndex = 0
        self.ifIndex = 0

    def advance(self):
        self.currentLine = self.tokenFile.readline()
        try:
            self.currentToken = self.currentLine.split()[1]
            self.currentTokenType = self.currentLine.split()[0][1:-1]
        except IndexError:
            if self.currentLine == "</tokens>":
                pass
            else:
                raise IndexError

    def compileClass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        # class
        self.advance()
        # className
        line = self.currentLine.split() # define class
        self.className = line[1]
        self.advance()
        # {
        self.advance()

        while self.currentToken in ["static", "field"]:
            # classVarDec                    
            self.compileClassVarDec()

        while self.currentToken in ["constructor", "function", "method"]:
            # subroutineDec
            self.compileSubroutine()

        # }
        self.advance()
    
    def compileClassVarDec(self):
        """
        classVarDec: ('static'|'field') type varName (',' varName)* ';'
        """
        # static|field
        kind = self.currentToken
        self.advance()
        # type
        type = self.currentToken
        self.advance()
        # varName
        name = self.currentToken
        self.symbolTable.define(name, type, kind)
        index = self.symbolTable.indexOf(name)
        line = self.currentLine.split()
        # define
        self.advance()

        # (, varName)*
        while self.currentToken == ",":
            # ,
            self.advance()
            # varName
            name = self.currentToken
            self.symbolTable.define(name, type, kind)
            index = self.symbolTable.indexOf(name)
            line = self.currentLine.split()
            # define
            self.advance()

        # ;
        self.advance()

    def compileSubroutine(self):
        """
        subroutineDec: ('constructor'|'function'|'method')
                       ('void' | type) subroutineName '(' parameterList ')'
                       subroutineBody
        subroutineBody: '{' varDec* statements '}'
        """
        self.symbolTable.startSubroutine()
        nClassVar = self.symbolTable.varCount("field")
        # constructor|function|method
        funcionType = self.currentToken
        self.advance()
        # void|type
        self.advance()
        # subroutineName
        line = self.currentLine.split() # define subroutine
        fName = line[1]
        self.advance()
        # (
        self.advance()
        # parameterList
        self.compileParameterList()
        # )
        self.advance()
        # {
        self.advance()

        # varDec*
        nLocals = 0
        while self.currentToken == "var":
            nLocals += self.compileVarDec()

        # function name nLocals
        self.f.write(f"function {self.className}.{fName} {nLocals}\n")

        if funcionType == "constructor":
            self.f.write(f"push constant {nClassVar}\n")
            self.f.write("call Memory.alloc 1\n")
            self.f.write("pop pointer 0\n")

        elif funcionType == "method":
            self.f.write("push argument 0\n")
            self.f.write("pop pointer 0\n")

        # statements
        self.compileStatements()
        # }
        self.advance()

    def compileParameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        if self.currentTokenType == "keyword" or self.currentToken == "Array":
            # type
            type = self.currentToken
            self.advance()
            # varName
            kind = "argument"
            name = self.currentToken
            self.symbolTable.define(name, type, kind) # define
            index = self.symbolTable.indexOf(name)
            line = self.currentLine.split()
            self.advance()
            
            while self.currentToken == ",":
                # ,
                self.advance()
                # type
                type = self.currentToken
                self.advance()
                # varName
                name = self.currentToken
                self.symbolTable.define(name, type, kind) # define
                index = self.symbolTable.indexOf(name)
                line = self.currentLine.split()
                self.advance()

    def compileVarDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        # var
        self.advance()
        # type
        type = self.currentToken
        if self.currentTokenType == "identifier": # use class
            line = self.currentLine.split()
        self.advance()
        # varName
        kind = "var"
        name = self.currentToken
        self.symbolTable.define(name, type, kind) # define
        index = self.symbolTable.indexOf(name)
        line = self.currentLine.split()
        self.advance()

        nLocals = 1
        while self.currentToken == ",":
            nLocals += 1
            # ,
            self.advance()
            # varName
            name = self.currentToken
            self.symbolTable.define(name, type, kind) # define
            index = self.symbolTable.indexOf(name)
            line = self.currentLine.split()
            self.advance()

        # ;
        self.advance()
        return nLocals

    def compileStatements(self):
        """
        statements: statement*
        """
        while self.currentToken in ["let", "if", "while", "do", "return"]:
            
            if self.currentToken == "let":
                self.compileLet()

            elif self.currentToken == "if":
                self.compileIf()

            elif self.currentToken == "while":
                self.compileWhile()

            elif self.currentToken == "do":
                self.compileDo()

            elif self.currentToken == "return":
                self.compileReturn()

    def compileDo(self):
        """
        doStatement: 'do' subroutineCall ';'
        """
        # do
        self.advance()
        # subroutineCall
        self.compileSubroutineCall()
        self.f.write("pop temp 0\n")
        # ;
        self.advance()

    def compileSubroutineCall(self):
        """
        subroutineCall: subroutineName '(' expressionList ')' | (className |
                        varName) '.' subroutineName '(' expressionList ')'
        """
        # subRoutineName|className|varName
        name = self.currentToken
        line = self.currentLine.split()
        nArgs = 0
        self.advance()
        
        # className|varName
        if self.currentToken == ".":

            fName = name + self.currentToken

            # varName
            if self.symbolTable.search(name):
                nArgs += 1
                kind = self.symbolTable.kindOf(name)
                index = self.symbolTable.indexOf(name) # use

            # .
            self.advance()
            # subroutineName
            fName += self.currentToken # use subroutine
            self.advance()

        # subroutineName
        else:
            fName = self.className + "." + name # use subroutine

        # (
        self.advance()
        # expressionList
        nArgs += self.compileExpressionList()
        self.f.write(f"call {fName} {nArgs}\n")
        # )
        self.advance()

    def compileLet(self):
        """
        letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        """
        # let
        self.advance()
        # varName 
        line = self.currentLine.split()
        name = self.currentToken
        kind = self.symbolTable.kindOf(name)
        index = self.symbolTable.indexOf(name) # use
        self.advance()

        # array access
        if self.currentToken == "[":
            # [
            self.advance()
            # expression
            self.compileExpression()
            self.f.write(f"push {self.segmentIndex[kind]} {index}\n")
            self.f.write("add\n")
            # ]
            self.advance()
            # =
            self.advance()
            # expression
            self.compileExpression()
            self.f.write("pop temp 0\n")
            self.f.write("pop pointer 1\n")
            self.f.write("push temp 0\n")
            self.f.write("pop that 0\n")

        else:
            # =
            self.advance()
            # expression
            self.compileExpression()
            self.f.write(f"pop {self.segmentIndex[kind]} {index}\n")

        # ;
        self.advance()

    def compileWhile(self):
        """
        whileStatement: 'while' '(' expression ')' '{' statements '}'
        """
        L1 = f"WHILE_EXP{self.whileIndex}"
        L2 = f"WHILE_END{self.whileIndex}"
        self.whileIndex += 1
        # while
        self.advance()
        # (
        self.advance()
        # expression
        self.f.write(f"label {L1}\n")
        self.compileExpression()
        self.f.write("not\n")
        self.f.write(f"if-goto {L2}\n")
        # )
        self.advance()
        # {
        self.advance()
        # statements
        self.compileStatements()
        self.f.write(f"goto {L1}\n")
        self.f.write(f"label {L2}\n")
        # }
        self.advance()

    def compileReturn(self):
        """
        returnStatement 'return' expression? ';'
        """
        # return
        self.advance()

        # expression     
        if self.currentToken != ";":
            self.compileExpression()

        else:
            self.f.write("push constant 0\n")
        
        self.f.write("return\n")
        # ;
        self.advance()

    def compileIf(self):
        """
        ifStatement: 'if' '(' expression ')' '{' statements '}'
                     ('else' '{' statements '}')?
        """
        L1 = f"IF_FALSE{self.ifIndex}"
        L2 = f"IF_TRUE{self.ifIndex}"
        self.ifIndex += 1
        # if 
        self.advance()
        # (
        self.advance()
        # expression
        self.compileExpression()
        self.f.write("not\n")
        self.f.write(f"if-goto {L1}\n")
        # )
        self.advance()
        # {
        self.advance()
        # statements
        self.compileStatements()
        self.f.write(f"goto {L2}\n")
        self.f.write(f"label {L1}\n")
        # }
        self.advance()

        if self.currentToken == "else":
            # else
            self.advance()
            # {
            self.advance()
            # statements
            self.compileStatements()
            # }
            self.advance()

        self.f.write(f"label {L2}\n")
        
    def compileExpression(self):
        """
        expression: term (op term)*
        """
        # term
        self.compileTerm()
        
        while self.currentToken in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:
            # op
            op = self.currentToken
            self.advance()
            # term
            self.compileTerm()
            self.f.write(self.opIndex[op])

    def compileTerm(self):
        """
        term: integerConstant | stringConstant | keywordConstant |
              varName | varName '[' expression ']' | subroutineCall |
              '(' expression ')' | unaryOp term
        """
        # ( expression )
        if self.currentToken == "(":
            # (
            self.advance()
            # expression
            self.compileExpression()
            # )
            self.advance()

        # unaryOp term
        elif self.currentToken in ["-", "~"]:
            # unaryOp
            unaryOp = self.currentToken
            self.advance()
            # term
            self.compileTerm()
            self.f.write("neg\n" if unaryOp == "-" else "not\n")

        # integerConstant|stringConstant|keywordConstant
        elif self.currentTokenType in ["integerConstant", "stringConstant", "keyword"]:
            if self.currentTokenType == "integerConstant":
                integer = self.currentToken
                self.f.write("push constant " + integer + "\n")

            elif self.currentTokenType == "stringConstant":
                string = self.currentLine[17:-19]
                self.f.write(f"push constant {len(string)}\n")
                self.f.write("call String.new 1\n")
                for char in string:
                    self.f.write(f"push constant {ord(char)}\n")
                    self.f.write("call String.appendChar 2\n")

            elif self.currentTokenType == "keyword":
                keyword = self.currentToken
                if keyword == "true":
                    self.f.write("push constant 0\n")
                    self.f.write("not\n")

                elif keyword == "false":
                    self.f.write("push constant 0\n")

                elif keyword == "null":
                    self.f.write("push constant 0\n")

                elif keyword == "this":
                    self.f.write("push pointer 0\n")

            self.advance()

        # varName|varName[expression]|subroutineCall
        else:
            # varName|subroutineName|className
            name = self.currentToken
            line = self.currentLine.split()
            self.advance()
            
            # varName[expression]
            if self.currentToken == "[":
                kind = self.symbolTable.kindOf(name)
                index = self.symbolTable.indexOf(name) # use
                # [
                self.advance()
                # expression
                self.compileExpression()
                self.f.write(f"push {self.segmentIndex[kind]} {index}\n")
                self.f.write("add\n")
                self.f.write("pop pointer 1\n")
                self.f.write("push that 0\n")
                # ]
                self.advance()

            # subroutineCall
            elif self.currentToken in ["(", "."]:

                nArgs = 0
                
                # className|varName
                if self.currentToken == ".":

                    fName = name + "."
                    
                    # varName
                    if self.symbolTable.search(name):
                        nArgs += 1
                        kind = self.symbolTable.kindOf(name)
                        index = self.symbolTable.indexOf(name) # use

                    # .
                    self.advance()
                    # subroutineName
                    fName += self.currentToken
                    line = self.currentLine.split() # use subroutine
                    self.advance()

                else:
                    fName = className + "." + name

                # (
                self.advance()
                # expressionList
                nArgs += self.compileExpressionList()
                self.f.write(f"call {fName} {nArgs}\n")
                # )
                self.advance()

            # varName
            else:
                kind = self.symbolTable.kindOf(name)
                index = self.symbolTable.indexOf(name) # use
                self.f.write(f"push {self.segmentIndex[kind]} {index}\n")

    def compileExpressionList(self):
        """
        expressionList: (expression (',' expression)* )?
        """
        nArgs = 0
        if self.currentToken != ")":
            nArgs += 1
            # expression
            self.compileExpression()

            while self.currentToken == ",":
                nArgs += 1
                # ,
                self.advance()
                # expression
                self.compileExpression()
        return nArgs