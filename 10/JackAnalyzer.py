import JackTokenizer
import CompilationEngine
import sys
import os

jackFiles = [file for file in os.listdir(sys.argv[1]) if file[-4:] == "jack"]

openTags = {"SYMBOL": "<symbol>", "STRING_CONST": "<stringConstant>", "INT_CONST": "<integerConstant>", "IDENTIFIER": 
            "<identifier>", "KEYWORD": "<keyword>"}

closeTags = {"SYMBOL": "</symbol>", "STRING_CONST": "</stringConstant>", "INT_CONST": "</integerConstant>", "IDENTIFIER": 
            "</identifier>", "KEYWORD": "</keyword>"}

for file in jackFiles:

    jackTokenizer = JackTokenizer.JackTokenizer(sys.argv[1] + "/" + file)

    extractToken = {"SYMBOL": jackTokenizer.symbol, "STRING_CONST": jackTokenizer.stringVal, "INT_CONST": jackTokenizer.intVal, 
                    "IDENTIFIER": jackTokenizer.identifier, "KEYWORD": jackTokenizer.keyword}

    with open(f"{sys.argv[1]}/{file[:-5]}T.xml", "w") as tokenFile:
        tokenFile.write("<tokens>\n")
        while jackTokenizer.hasMoreTokens():
            tokenType = jackTokenizer.tokenType()
            tokenFile.write(openTags[tokenType])
            tokenFile.write(" ")
            tokenFile.write(extractToken[tokenType]())
            tokenFile.write(" ")
            tokenFile.write(closeTags[tokenType])
            tokenFile.write("\n")
        tokenFile.write("</tokens>")

    with open(f"{sys.argv[1]}/{file[:-5]}T.xml", "r") as tokenFile, open(f"{sys.argv[1]}/{file[:-5]}.xml", "w") as outputFile:
        compilationEngine = CompilationEngine.CompilationEngine(tokenFile, outputFile)
        compilationEngine.compileClass()