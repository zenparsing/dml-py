import re

ws_chars = re.compile(r"[\x09\x0B-\x0C\x20\xA0\u1680\u180E\u2000-\u200A\u202F\u205F\u3000\uFEFF]")
nl_chars = re.compile(r"[\r\n\u2028\u2029]")
backtick3 = re.compile(r"```")

def binary_search(list, value):
    """Returns the index of a value within a sorted list.
    
    If the value is not found within the list, then the appropriate
    insertion position is returned."""

    right = len(list) - 1
    left = 0
    
    while left <= right:
        
        mid = (left + right) >> 1
        test = list[mid]
        
        if value == test: 
            return mid
        
        if value < test: right = mid - 1
        else: left = mid + 1
    
    return left


def is_ascii_whitespace(chr):
    """Returns True if the specified character is ASCII whitespace, but
    not a newline character."""

    c = ord(chr)
    return c == 9 or c == 11 or c == 12 or c == 32
    

def is_identifier_char(chr, first = False):
    """Returns True if the specified character is an identifier character."""

    c = ord(chr)
    
    if c >= 128:
        return not (ws_chars.match(chr) or nl_chars.match(chr))
    
    return (
        c >= 65 and c <= 90 or              # A-Z
        c >= 97 and c <= 122 or             # a-z
        c > 47 and c < 58 and not first or  # 0-9
        c == 45 and not first or            # -
        c == 95                             # _
    )


def is_text_char(chr):
    """Returns True if the specified character is a text character."""

    c = ord(chr)
    
    if c >= 127:
        return not (ws_chars.match(chr) or nl_chars.match(chr))
    
    return not (
        c == 0 or
        c == 32 or   # " "
        c == 9 or    # "\t"
        c == 11 or   # "\v"
        c == 12 or   # "\f"
        c == 13 or   # "\r"
        c == 10 or   # "\n"
        c == 96 or   # "`"
        c == 123 or  # "{"
        c == 124     # "}"
    )


class Scanner:

    def __init__(self, input = ""):
    
        self.input = input
        self.offset = 0
        self.lines = [-1]
        self.last_line_break = -1
        
        self.type = ""
        self.start = 0
        self.end = 0
        self.value = ""
        self.error = ""
        self.newlines = 0
    
    
    def next(self, context):
        """Reads the next token from the input stream and returns the token type."""
    
        self.error = ""
        self.newlines = 0
        
        type = None 
        start = 0
        
        while type is None:
        
            start = self.offset
            type = "eof" if start >= len(self.input) else self.Start(context)
        
        self.type = type
        self.start = start
        self.end = self.offset
        
        return type
    
    
    def line_number(self, offset):
        """Returns the line number of the specified input offset."""
    
        return binary_search(self.lines, offset)
    
    
    def position(self, offset):
        """Returns line and column data for the specifed input offset."""
    
        line = self.line_number(offset)
        pos = self.lines[line - 1]
        column = offset - pos
        
        return { 
        
            "line": line, 
            "column": column,
            "line_offset": pos + 1
        }
    
    
    def add_line_break(self, offset):
        """Adds a line break at the specified offset."""
    
        if offset > self.last_line_break:
            self.last_line_break = offset
            self.lines.append(offset)
    
    
    def peek(self):
        """Returns the next unread character from the input string."""
    
        return self.get_char(self.offset)
    
    
    def peek_at(self, lookahead):
        """Returns a character from the input string, relative to the current position."""
    
        return self.get_char(self.offset + lookahead)
    
    
    def peek_code(self):
        """Returns the character code of the next unread character."""
    
        return ord(self.get_char(self.offset))
    
    
    def get_char(self, index):
        """Returns the character at the specified offset, or the empty string if the
        current position is greater than or equal to the input length."""
    
        if index >= len(self.input):
            return "";
        
        return self.input[index]
        
    
    def advance(self):
        """Advances the current position one character."""
    
        offset = self.offset
        self.offset += 1
        return offset

    
    def Start(self, context):
    
        c = self.peek()
        
        if ord(c) < 128:
        
            # ASCII Characters (fast path)
            
            if is_ascii_whitespace(c): 
                return self.Whitespace()
            
            if c == "\n" or c == "\r":
                return self.Newline(c)
            
            if c == "`":
                return self.RawString()
            
            if c == "{" or c == "}":
                return self.PunctuatorChar()
            
            if c == "[":
            
                if context == "head" or context == "selector":
                    return self.PunctuatorChar()
                
                return self.Text()
            
            if c == "]" or c == "=" or c == "." or c == ":" or c == "#":
            
                if context == "selector":
                    return self.PunctuatorChar()
                
                return self.Text()
            
            if c == "-":
                
                if context == "selector":
                    return self.Identifier(True)
                
                return self.Text()
                    
        else:
        
            # Non-ASCII Characters (slow path)
            
            if nl_chars.match(c):
                return self.Newline()
            
            if ws_chars.match(c):
                return self.UnicodeWhitespace()
        
        if context != "selector":
            return self.Text()
        
        if is_identifier_char(c, True):
            return self.Identifier()
            
        return self.Error("Unrecognized token")
    
    
    def Newline(self, chr):
        
        self.add_line_break(self.advance())
        
        # Treat /r/n as a single newline
        if chr == "\r" and self.peek() == "\n":
            self.advance()
        
        self.newlines += 1
        
        return None;
    
    
    def Whitespace(self):
    
        self.advance()
        
        while is_ascii_whitespace(self.peek()):
            self.advance()
        
        return None
    
    
    def UnicodeWhitespace(self):
    
        self.advance()
        
        while ws_chars.match(self.peek()):
            self.advance()
        
        return None
    
    
    def PunctuatorChar(self):
    
        self.value = self.peek()
        self.advance()
        
        return self.value

    def RawString(self):
    
        type = "raw-string"
        val = ""
        count = 1
        
        self.advance()
        
        # Count the number of adjacent backticks
        while self.peek() == "`":
            count += 1
            self.advance()
        
        if count == 1:
        
            # Inline raw string
            
            while (True):
            
                chr = self.peek()
                
                if chr == "":
                    break
                
                if chr == "`":
                
                    if self.peek_at(1) == "`":
                    
                        # Two consecutive backticks are a literal backtick
                        self.advance()
                        
                    else:
                    
                        # End of raw string
                        break
                
                val += chr
                self.advance()
            
            if chr == "":
                return self.Error("Unterminated raw string")
            
            self.advance()
        
        elif count == 2:
        
            # Literal backtick
            
            val = "`"
            
        else:
        
            # Raw block
            
            type = "raw-block"
            start = self.offset
            
            while True:
            
                match = backtick3.search(self.input, self.offset)
            
                if not match:
                    return self.Error("Unterminated raw block")
            
                self.offset = match.start()
                len = 3
                
                while len < count and self.peek() == "`":
                
                    len += 1
                    self.advance()
                
                if len == count:
                    break
            
            val = self.input[start:self.offset - count]
        
        self.value = val
        
        return type
        
    
    def Identifier(self, dash = False):
    
        start = self.offset
        first = dash
        
        self.advance()
        
        while is_identifier_char(self.peek(), first):
        
            self.advance()
            first = False
        
        self.value = self.input[start:self.offset]
        
        return "identifier"

    
    def Text(self):
    
        start = self.offset
        
        self.advance()
        
        while is_text_char(self.peek()):
            self.advance()
        
        self.value = self.input[start:self.offset]
        
        return "text"

    
    def Error(self, msg):

        self.error = msg
        self.advance()
        
        return "illegal"

