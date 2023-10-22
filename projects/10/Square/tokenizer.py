import sys
import xml.dom.minidom

SYMBOLS = list(';[](){}=.,+-*/|&')
KEYWORDS = 'class constructor method function this var static field int boolean char void let do if else while return true false null'.split(' ')

filename = sys.argv[1]
with open(filename, 'r') as f:
    lines = [line for line in f]

lines_without_comments = [line.split('//')[0].strip('\n').strip(' ') for line in lines
                              if not line.startswith(('//', '/**'))]

tokens = []
for line in lines_without_comments:
    curpos = 0
    curtoken = ""
    curstring = ""
    start_string = False
    for char in line:
        if curpos == len(line) - 1 or char in SYMBOLS or char == ' ':  # End of curtoken
            if curtoken in KEYWORDS:
                tokens.append(('keyword', curtoken))
            elif curtoken.isdigit():
                tokens.append(('integerConstant', curtoken))
            else:
                tokens.append(('identifier', curtoken))
            curtoken = ""
            if char in SYMBOLS:
                tokens.append(('symbol', char))
        elif char == '"' and not start_string:  # Start of curstring
            start_string = True
        elif char == '"' and start_string:  # End of curstring
            tokens.append(('stringConstant', curstring))
            curstring = ""
            start_string = False
        elif char != '"' and start_string:  # Append to curstring
            curstring = curstring + char
        else:  # Append to curtoken
            curtoken = curtoken + char

        curpos += 1

tokens = list(filter(lambda token: token[1] != '' and token[1] != ' ', tokens))

doc = xml.dom.minidom.Document()
root = doc.createElement("tokens")
for token in tokens:
    child_element = doc.createElement(token[0])
    text_node = doc.createTextNode(token[1])
    child_element.appendChild(text_node)
    root.appendChild(child_element)
doc.appendChild(root)

print(doc.documentElement.toprettyxml(indent="").strip())
