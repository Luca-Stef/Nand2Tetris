class JackTokenizer:

    """
    Tokenises the input and tags each token as symbol, keyword, identifier, string constant or integer 
    constant according to the Jack language grammar specification
    """

    keywords = ['class','constructor','function','method','field','static','var','int','char',
            'boolean','void','true','false','null','this','let','do','if','else','while','return']
    symbols = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']

    def __init__(self, filepath):
        """
        Opens input file, removes comments and whitespace
        """
        self.input = ""
        with open(filepath, "r") as f:
            lineIsComment = False
            for line in f:
                if "/**" in line:
                    lineIsComment = True
                if lineIsComment:
                    if "*/" in line:
                        lineIsComment = False
                    continue
                line = line.partition("//")[0].partition("/**")[0].strip()
                if line:
                    self.input += line
        self.c = 0
        self.start = 0
        self.inputLength = len(self.input)

    def hasMoreTokens(self):
        """
        Does the input file/stream have more tokens?
        """
        return self.c < self.inputLength

    def advance(self):
        """
        Advances to the next token
        """
        self.c += 1

    def tokenType(self):
        """
        Returns the token type, either symbol, string constant, integer constant, keyword or identifier
        """
        while self.input[self.c] == " ":
            self.advance()

        if self.input[self.c] in self.symbols:
            return "SYMBOL"

        elif self.input[self.c] == "\"":
            return "STRING_CONST"

        elif self.input[self.c].isnumeric():
            return "INT_CONST" 

        else:
            self.start = self.c
            while self.input[self.c] not in self.symbols + [" "]:
                self.advance()

            if self.input[self.start:self.c] in self.keywords:
                return "KEYWORD"

            else:
                return "IDENTIFIER"

    def keyword(self):
        return self.input[self.start:self.c]

    def symbol(self):
        output = self.input[self.c]
        if output == "<":
            output = "&lt;"
        elif output == ">":
            output = "&gt;"
        elif output == "\"":
            output = "&quot;"
        elif output == "&":
            output = "&amp;"
        self.advance()
        return output

    def identifier(self):
        return self.input[self.start:self.c]
    
    def intVal(self):
        self.start = self.c
        while self.input[self.c].isnumeric():
            self.advance()
        return self.input[self.start:self.c]

    def stringVal(self):
        self.advance()
        self.start = self.c
        while self.input[self.c] != "\"":
            self.advance()
        output = self.input[self.start:self.c]
        self.advance()
        return output