class CompilationEngine:

    """
    Compilation engine class
    """

    def __init__(self, tokenFile, outputFile):
        self.f = outputFile
        self.tokenFile = tokenFile
        self.tokenFile.readline()
        self.currentLine = self.tokenFile.readline()
        self.currentToken = self.currentLine.split()[1]
        self.currentTokenType = self.currentLine.split()[0][1:-1]

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
        self.f.write("<class>\n")
        # class
        self.f.write(self.currentLine)
        self.advance()
        # className
        self.f.write(self.currentLine)
        self.advance()
        # {
        self.f.write(self.currentLine)
        self.advance()

        while self.currentToken in ["static", "field"]:
            # classVarDec                    
            self.compileClassVarDec()

        while self.currentToken in ["constructor", "function", "method"]:
            # subroutineDec
            self.compileSubroutine()

        # }
        self.f.write(self.currentLine)
        self.advance()
        # close class
        self.f.write("</class>\n")
    
    def compileClassVarDec(self):
        """
        classVarDec: ('static'|'field') type varName (',' varName)* ';'
        """
        # classVarDec
        self.f.write("<classVarDec>\n")
        # static|field
        self.f.write(self.currentLine)
        self.advance()
        # type
        self.f.write(self.currentLine)
        self.advance()
        # varName
        self.f.write(self.currentLine)
        self.advance()

        # (, varName)*
        while self.currentToken == ",":
            # ,
            self.f.write(self.currentLine)
            self.advance()
            # varName
            self.f.write(self.currentLine)
            self.advance()

        # ;
        self.f.write(self.currentLine)
        self.advance()
        #close classVarDec
        self.f.write("</classVarDec>\n")

    def compileSubroutine(self):
        """
        subroutineDec: ('constructor'|'function'|'method')
                       ('void' | type) subroutineName '(' parameterList ')'
                       subroutineBody
        subroutineBody: '{' varDec* statements '}'
        """
        self.f.write("<subroutineDec>\n")
        # constructor|function|method
        self.f.write(self.currentLine)
        self.advance()
        # void|type
        self.f.write(self.currentLine)
        self.advance()
        # subroutineName
        self.f.write(self.currentLine)
        self.advance()
        # (
        self.f.write(self.currentLine)
        self.advance()
        # parameterList
        self.compileParameterList()
        # )
        self.f.write(self.currentLine)
        self.advance()
        # subRoutineBody
        self.f.write("<subroutineBody>\n")
        # {
        self.f.write(self.currentLine)
        self.advance()

        # varDec*
        while self.currentToken == "var":
            self.compileVarDec()

        # statements
        self.compileStatements()
        # }
        self.f.write(self.currentLine)
        self.advance()
        # close subRoutineBody
        self.f.write("</subroutineBody>\n")
        # close subRoutineDec
        self.f.write("</subroutineDec>\n")

    def compileParameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        # parameterList
        self.f.write("<parameterList>\n")

        if self.currentTokenType == "keyword" or self.currentToken == "Array":
            # type
            self.f.write(self.currentLine)
            self.advance()
            # varName
            self.f.write(self.currentLine)
            self.advance()
            
            while self.currentToken == ",":
                # ,
                self.f.write(self.currentLine)
                self.advance()
                # type
                self.f.write(self.currentLine)
                self.advance()
                # varName
                self.f.write(self.currentLine)
                self.advance()

        # close parameterList
        self.f.write("</parameterList>\n")

    def compileVarDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        # varDec
        self.f.write("<varDec>\n")
        # var
        self.f.write(self.currentLine)
        self.advance()
        # type
        self.f.write(self.currentLine)
        self.advance()
        # varName
        self.f.write(self.currentLine)
        self.advance()

        while self.currentToken == ",":
            # ,
            self.f.write(self.currentLine)
            self.advance()
            # varName
            self.f.write(self.currentLine)
            self.advance()

        # ;
        self.f.write(self.currentLine)
        self.advance()
        # close varDec
        self.f.write("</varDec>\n")

    def compileStatements(self):
        """
        statements: statement*
        """
        # statements
        self.f.write("<statements>\n")

        while self.currentToken in ["let", "if", "while", "do", "return"]:
            
            if self.currentToken == "let":
                self.compileLet()

            elif self.currentToken == "if":
                self.compileIf()

            elif self.currentToken == "while":
                self.compileWhile()

            elif self.currentToken == "do":
                self.compileDo()

            else:
                self.compileReturn()

        # close statements
        self.f.write("</statements>\n")

    def compileDo(self):
        """
        doStatement: 'do' subroutineCall ';'
        """
        # doStatement
        self.f.write("<doStatement>\n")
        # do
        self.f.write(self.currentLine)
        self.advance()
        # subroutineCall
        self.compileSubroutineCall()
        # ;
        self.f.write(self.currentLine)
        self.advance()
        # close doStatement
        self.f.write("</doStatement>\n")

    def compileSubroutineCall(self):
        """
        subroutineCall: subroutineName '(' expressionList ')' | (className |
                        varName) '.' subroutineName '(' expressionList ')'
        """
        # subRoutineName|className|varName
        self.f.write(self.currentLine)
        self.advance()
        
        if self.currentToken == ".":
            # .
            self.f.write(self.currentLine)
            self.advance()
            # subroutineName
            self.f.write(self.currentLine)
            self.advance()

        # (
        self.f.write(self.currentLine)
        self.advance()
        # expressionList
        self.compileExpressionList()
        # )
        self.f.write(self.currentLine)
        self.advance()

    def compileLet(self):
        """
        letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        """
        # letStatement
        self.f.write("<letStatement>\n")
        # let
        self.f.write(self.currentLine)
        self.advance()
        # varName
        self.f.write(self.currentLine)
        self.advance()

        if self.currentToken == "[":
            # [
            self.f.write(self.currentLine)
            self.advance()
            # expression
            self.compileExpression()
            # ]
            self.f.write(self.currentLine)
            self.advance()

        # =
        self.f.write(self.currentLine)
        self.advance()
        # expression
        self.compileExpression()
        # ;
        self.f.write(self.currentLine)
        self.advance()
        # close letStatement
        self.f.write("</letStatement>\n")

    def compileWhile(self):
        """
        whileStatement: 'while' '(' expression ')' '{' statements '}'
        """
        # whileStatement
        self.f.write("<whileStatement>\n")
        # while
        self.f.write(self.currentLine)
        self.advance()
        # (
        self.f.write(self.currentLine)
        self.advance()
        # expression
        self.compileExpression()
        # )
        self.f.write(self.currentLine)
        self.advance()
        # {
        self.f.write(self.currentLine)
        self.advance()
        # statements
        self.compileStatements()
        # }
        self.f.write(self.currentLine)
        self.advance()
        # close whileStatement
        self.f.write("</whileStatement>\n")

    def compileReturn(self):
        """
        returnStatement 'return' expression? ';'
        """
        # returnStatement
        self.f.write("<returnStatement>\n")
        # return
        self.f.write(self.currentLine)
        self.advance()

        # expression     
        if self.currentToken != ";":
            self.compileExpression()
        
        # ;
        self.f.write(self.currentLine)
        self.advance()
        # close returnStatement
        self.f.write("</returnStatement>\n")

    def compileIf(self):
        """
        ifStatement: 'if' '(' expression ')' '{' statements '}'
                     ('else' '{' statements '}')?
        """
        # ifStatement
        self.f.write("<ifStatement>\n")
        # if 
        self.f.write(self.currentLine)
        self.advance()
        # (
        self.f.write(self.currentLine)
        self.advance()
        # expression
        self.compileExpression()
        # )
        self.f.write(self.currentLine)
        self.advance()
        # {
        self.f.write(self.currentLine)
        self.advance()
        # statements
        self.compileStatements()
        # }
        self.f.write(self.currentLine)
        self.advance()

        if self.currentToken == "else":
            # else
            self.f.write(self.currentLine)
            self.advance()
            # {
            self.f.write(self.currentLine)
            self.advance()
            # statements
            self.compileStatements()
            # }
            self.f.write(self.currentLine)
            self.advance()

        # close ifStatement
        self.f.write("</ifStatement>\n")

    def compileExpression(self):
        """
        expression: term (op term)*
        """
        # expression
        self.f.write("<expression>\n")
        # term
        self.compileTerm()
        
        while self.currentToken in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:
            # op
            self.f.write(self.currentLine)
            self.advance()
            # term
            self.compileTerm()

        # close expression
        self.f.write("</expression>\n")

    def compileTerm(self):
        """
        term: integerConstant | stringConstant | keywordConstant |
              varName | varName '[' expression ']' | subroutineCall |
              '(' expression ')' | unaryOp term
        """
        # term
        self.f.write("<term>\n")

        # ( expression )
        if self.currentToken == "(":
            # (
            self.f.write(self.currentLine)
            self.advance()
            # expression
            self.compileExpression()
            # )
            self.f.write(self.currentLine)
            self.advance()

        # unaryOp term
        elif self.currentToken in ["-", "~"]:
            # unaryOp
            self.f.write(self.currentLine)
            self.advance()
            # term
            self.compileTerm()

        # integerConstant|stringConstant|keywordConstant
        elif self.currentTokenType in ["integerConstant", "stringConstant", "keyword"]:
            self.f.write(self.currentLine)
            self.advance()

        # varName|varName[expression]|subroutineCall
        else:
            # varName|subroutineName
            self.f.write(self.currentLine)
            self.advance()
            
            if self.currentToken == "[":
                # [
                self.f.write(self.currentLine)
                self.advance()
                # expression
                self.compileExpression()
                # ]
                self.f.write(self.currentLine)
                self.advance()

            elif self.currentToken in ["(", "."]:

                if self.currentToken == ".":
                    # .
                    self.f.write(self.currentLine)
                    self.advance()
                    # subroutineName
                    self.f.write(self.currentLine)
                    self.advance()

                # (
                self.f.write(self.currentLine)
                self.advance()
                # expressionList
                self.compileExpressionList()
                # )
                self.f.write(self.currentLine)
                self.advance()

        # close term
        self.f.write("</term>\n")

    def compileExpressionList(self):
        """
        expressionList: (expression (',' expression)* )?
        """
        # expressionList
        self.f.write("<expressionList>\n")

        if self.currentToken != ")":
            # expression
            self.compileExpression()

            while self.currentToken == ",":
                # ,
                self.f.write(self.currentLine)
                self.advance()
                # expression
                self.compileExpression()

        # close expressionList
        self.f.write("</expressionList>\n")