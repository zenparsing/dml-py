def node_type(c):
    """Assigns a node type name based on the class name"""
    
    c.type = c.__name__
    return c

@node_type
class Element:
    
    def __init__(self, selectors, body, start, end):
        
        self.selectors = selectors
        self.body = body
        self.start = start
        self.end = end
    
    def __iter__(self):
        yield from self.selectors
        yield self.body
        

@node_type
class ElementBody:

    def __init__(self, attributes, children, start, end):
    
        self.attributes = attributes
        self.children = children
        self.start = start
        self.end = end
    
    def __iter__(self):
        yield from self.attributes
        yield from self.children
        

@node_type
class NameSelector:

    def __init__(self, namespace, name, start, end):
    
        self.namespace = namespace
        self.name = name
        self.start = start
        self.end = end
    
    def __iter__(self):
        if self.namespace != None: yield self.namespace
        yield self.name


@node_type
class IdSelector:

    def __init__(self, id, start, end):
    
        self.id = id
        self.start = start
        self.end = end
    
    def __iter__(self):
        yield self.id


@node_type
class ClassSelector:

    def __init__(self, name, start, end):
    
        self.name = name
        self.start = start
        self.end = end
    
    def __iter__(self):
        yield self.name
        

@node_type
class Attribute:

    def __init__(self, key, value, start, end):
    
        self.key = key
        self.value = value
        self.start = start
        self.end = end

    def __iter__(self):
        yield self.key
        yield self.value
        

@node_type
class Identifier:

    def __init__(self, value, start, end):
    
        self.value = value
        self.start = start
        self.end = end

    def __iter__(self):
        yield from []
    

class TextNode:

    def __init__(self, value, newlines, start, end):
    
        self.value = value
        self.newlines = newlines
        self.start = start
        self.end = end

    def __iter__(self):
        yield from []


@node_type
class RawString(TextNode): pass

@node_type
class RawBlock(TextNode): pass

@node_type
class Text(TextNode): pass
