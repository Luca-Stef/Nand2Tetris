from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from SymbolTable import SymbolTable
import sys
import os

jackFiles = [file for file in os.listdir(sys.argv[1]) if file[-4:] == "jack"]

openTags = {"SYMBOL": "<symbol>", "STRING_CONST": "<stringConstant>", "INT_CONST": "<integerConstant>", "IDENTIFIER": 
            "<identifier>", "KEYWORD": "<keyword>"}

closeTags = {"SYMBOL": "</symbol>", "STRING_CONST": "</stringConstant>", "INT_CONST": "</integerConstant>", "IDENTIFIER": 
            "</identifier>", "KEYWORD": "</keyword>"}

for file in jackFiles:

    jackTokenizer = JackTokenizer(sys.argv[1] + "/" + file)
    symbolTable = SymbolTable()

    extractToken = {"SYMBOL": jackTokenizer.symbol, "STRING_CONST": jackTokenizer.stringVal, "INT_CONST": jackTokenizer.intVal, 
                    "IDENTIFIER": jackTokenizer.identifier, "KEYWORD": jackTokenizer.keyword}

    with open(f"{sys.argv[1]}/{file[:-5]}T.xml", "w") as tokenFile:
        
        tokenFile.write("<tokens>\n")
        while jackTokenizer.hasMoreTokens():

            tokenType = jackTokenizer.tokenType()
            openTag = openTags[tokenType]
            closeTag = closeTags[tokenType]
            token = extractToken[tokenType]()

            tokenFile.write(openTag + " ")
            tokenFile.write(token + " ")
            tokenFile.write(closeTag + "\n")

        tokenFile.write("</tokens>")

    with open(f"{sys.argv[1]}/{file[:-5]}T.xml", "r") as tokenFile, open(f"{sys.argv[1]}/{file[:-5]}.vm", "w") as outputFile:
        compilationEngine = CompilationEngine(tokenFile, outputFile, symbolTable)
        compilationEngine.compileClass()