class SymbolTable:

    """
    Implements symbol table functionality for class level and subroutine level symbol tables.
    """

    def __init__(self):

        self.classTable = {}
        self.subTable = {}
        self.runningIndex = {"static": 0, "field": 0, "var": 0, "argument": 0}


    def startSubroutine(self):

        self.subTable = {}
        self.runningIndex["var"] = 0
        self.runningIndex["argument"] = 0
        

    def define(self, name, type, kind):

        if kind in ["static", "field"]:
            self.classTable[name] = {"type": type, "kind": kind, "#": self.runningIndex[kind]}

        elif kind in ["var", "argument"]:
            self.subTable[name] = {"type": type, "kind": kind, "#": self.runningIndex[kind]}

        self.runningIndex[kind] += 1
        

    def varCount(self, kind):
        
        return self.runningIndex[kind] + 1


    def kindOf(self, name):

        if name in self.classTable.keys():
            return self.classTable[name]["kind"]

        elif name in self.subTable.keys():
            return self.subTable[name]["kind"]

        else:
            raise NameError(f"Name {name} is not defined")


    def typeOf(self, name):
        
        if name in self.classTable.keys():
            return self.classTable[name]["type"]

        elif name in self.subTable.keys():
            return self.subTable[name]["type"]

        else:
            raise NameError(f"Name {name} is not defined")


    def indexOf(self, name):

        if name in self.classTable.keys():
            return str(self.classTable[name]["#"])

        elif name in self.subTable.keys():
            return str(self.subTable[name]["#"])

        else:
            raise NameError(f"Name {name} is not defined")


    def search(self, name):

        if name in self.classTable.keys():
            return True

        elif name in self.subTable.keys():
            return True

        else:
            return False