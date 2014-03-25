from parser import Parser

class Element:

    def __init__(self):
    
        self.namespace = ""
        self.name = ""
        self.id = ""
        self.attributes = dict()
        self.classes = set()
        self.children = list()


class Text:

    def __init__(self, value):
        
        self.value = value
        self.children = []


def parse(input):

    return from_ast(Parser().parse(input))
    

def from_ast(ast):

    def visit(node, element):
        
        t = node.type
        e = None
        
        if t == "Element":
            
            e = Element()
            element.children.append(e)
            
            for child in node:
                visit(child, e)
        
        elif t == "ElementBody":
        
            for child in node:
                visit(child, element)
            
        elif t == "NameSelector":
        
            if node.namespace != None:
                element.namespace = node.namespace.value
            
            element.name = node.name.value
        
        elif t == "IdSelector":
            
            element.id = node.id.value
        
        elif t == "ClassSelector":
        
            element.classes.add(node.name.value)
        
        elif t == "Attribute":
        
            element.attributes[node.key.value] = node.value.value if node.value else None
        
        elif t == "Text" or t == "RawString" or t == "RawBlock":
        
            element.children.append(Text(node.value))
            
        
    doc = Element()
    
    for node in ast.selectors:
        visit(node, doc)
    
    visit(ast.body, doc)
    
    return doc

