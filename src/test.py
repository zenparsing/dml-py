from parser import Parser

def print_tree(node, depth = 0):

    line = "";
    
    for i in range(depth):
        line += "   "
    
    line += "<" + node.type + ">"
    
    if hasattr(node, "value") and type(node.value) is str:
        line += " " + node.value
    
    print(line)
    
    for child in node:
        print_tree(child, depth + 1)


tree = Parser().parse("""

head {

    title { Document Title }
}

body {

    div#main { 

        [foo=bar] 
    
        here's some text
        
        p {
        
            A paragraph with a a { [href=`http://www.google.com`] link }.
        }
    } 

    div.footer { 

        Some footer text
    
    }
}

""")

print_tree(tree)
