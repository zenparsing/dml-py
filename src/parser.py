import ast
from scanner import Scanner

class ParseError(Exception):

    def __init__(self, msg, line, column, filename = ""):
    
        self.message = msg
        self.line = line
        self.column = column
        self.filename = filename
    
    # TODO: Add a __str__ method which displays line and column info
    # TODO: Add a class method which will take a string input and a parse
    #       error, and output a string which shows where the syntax error
    #       occurred (perhaps with a wavy line underneath).
    

class Parser:

    def __init__(self):
    
        self.scanner = None
        self.peeking = False
        self.end_offset = 0
    
    
    def parse(self, input):
    
        self.scanner = Scanner(input)
        self.peeking = False
        self.end_offset = 0
        
        return self.Start()
    
    
    def peek_start(self, context = None):
    
        return self.peek_token(context).start
    
    
    def peek_token(self, context = None):
    
        if not self.peeking:
            self.scanner.next(context)
            self.peeking = True
        
        
        return self.scanner
    
    
    def peek(self, context = None):
    
        return self.peek_token(context).type
    
    
    def read(self, type, context = None):
    
        tok = self.peek_token(context)
        
        if type and tok.type != type:
            self.unexpected()
        
        self.peeking = False
        self.end_offset = tok.end
        
        return tok
    
    
    def rewind(self, offset):
    
        self.scanner.offset = offset
        self.end_offset = offset
        self.peeking = False
    
    
    def fail(self, msg):
    
        pos = self.scanner.position(self.scanner.offset)
        raise ParseError(msg, pos["line"], pos["column"])
    
    def unexpected(self):
    
        type = self.peek()
        
        self.fail("Unexpected end of input" if type == "eof" else "Unexpected token " + type)
    
    
    def Start(self):
    
        start = self.peek_start("head")
        return ast.Element([], self.ElementBody(True), start, self.end_offset)
    
    
    def Element(self):
    
        start = self.peek_start("selector")
        selectors = [] if self.peek("selector") == "{" else self.SelectorList()
        
        return ast.Element(selectors, self.ElementBody(), start, self.end_offset)
    
    
    def ElementBody(self, root = False):
    
        start = self.peek_start("head")
        attributes = []
        children = []
        node = None
        
        if not root:
            self.read("{")
        
        while self.peek("head") == "[":
            attributes.append(self.Attribute())
        
        while True:
        
            tok = self.peek_token()
            t = tok.type
        
            if t == "eof":
                if not root: self.unexpected()
                break
                
            elif t == "}":
                if root: self.unexpected()
                break
            
            elif t == "{":
                if tok.newlines == 0 and node != None and node.type != "Element":
                    self.rewind(children.pop().start)
                
                node = self.Element()
            
            elif t == "raw-string":
                node = self.RawString()
            
            elif t == "raw-block":
                node = self.RawBlock()
            
            elif t == "text":
                node = self.Text()
            
            else:
                self.unexpected()
            
            children.append(node)
        
        
        if not root:
            self.read("}")
        
        return ast.ElementBody(attributes, children, start, self.end_offset)
    
    
    def SelectorList(self):
    
        start = self.peek_start("selector")
        list = []
        
        if self.peek("selector") == "identifier":
            list.append(self.NameSelector())
        
        while True:
        
            t = self.peek("selector")
            
            if t == "#":
                list.append(self.IdSelector())
            elif t == ".":
                list.append(self.ClassSelector())
            else:
                break
        
        return list
    
    
    def NameSelector(self):
    
        start = self.peek_start("selector")
        name = self.Identifier()
        namespace = None
        
        if self.peek("selector") == ":":
        
            namespace = name
            self.read(":", "selector")
            name = self.Identifier()
        
        
        return ast.NameSelector(namespace, name, start, self.end_offset)
    
    
    def IdSelector(self):
    
        start = self.peek_start("selector")
        self.read("#", "selector")
        return ast.IdSelector(self.Identifier(), start, self.end_offset)
    
    
    def ClassSelector(self):
    
        start = self.peek_start("selector")
        self.read(".", "selector")
        return ast.ClassSelector(self.Identifier(), start, self.end_offset)
    
    
    def Attribute(self):
    
        start = self.peek_start("selector")
        key = None
        value = None
        
        self.read("[", "selector")
        
        key = self.Identifier()
        
        if self.peek("selector") == "=":
        
            self.read(None, "selector")
            
            t = self.peek("selector")
            
            if t == "raw-string":
                value = self.RawString()
            elif t == "identifier":
                value = self.Identifier()
            else:
                self.unexpected()
            
        self.read("]", "selector")
        
        return ast.Attribute(key, value, start, self.end_offset)
    
    
    def Identifier(self):
    
        tok = self.read("identifier", "selector")
        return ast.Identifier(tok.value, tok.start, tok.end)
    
    
    def Text(self):
    
        tok = self.read("text")
        return ast.Text(tok.value, tok.newlines, tok.start, tok.end)
    
    
    def RawString(self):
    
        tok = self.read("raw-string")
        return ast.RawString(tok.value, tok.newlines, tok.start, tok.end)
    
    
    def RawBlock(self):
    
        tok = self.read("raw-block")
        return ast.RawBlock(tok.value, tok.newlines, tok.start, tok.end)

