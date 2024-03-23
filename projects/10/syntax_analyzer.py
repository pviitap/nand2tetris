import sys
import xml.dom.minidom
from pprint import pprint

SYMBOLS = list(';[](){}=.,+-*/|&<>')
OPERATORS = list('=+-*/|&<>')
KEYWORDS = 'class constructor method function this var static field int boolean char void let do if else while return true false null'.split(' ')

def tokenize(lines):
    tokens = []
    lines_without_comments = [line.split('//')[0].strip('\n').strip('\t').strip(' ') for line in lines
                              if not line.startswith(('//', '/**'))]

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
    return list(filter(lambda token: token[1] != '' and token[1] != ' ', tokens))

def print_xml(tokens):
    doc = xml.dom.minidom.Document()
    root = doc.createElement("tokens")
    for token in tokens:
        child_element = doc.createElement(token[0])
        text_node = doc.createTextNode(token[1])
        child_element.appendChild(text_node)
        root.appendChild(child_element)
    doc.appendChild(root)
    return doc.documentElement.toprettyxml(indent="").strip()

class TreeNode:
    def __init__(self, name, value = None, children = None):
        self.name = name
        self.value = value
        if children is None:
            children = []
        self.children = children
    def addChild(self, node):
        self.children.append(node)

def print_tree(node, indent=0):
    if node is not None:
        print("  " * indent + str(node.name) + ' ' + str(node.value))
        for child in node.children:
            print_tree(child, indent + 1)


def find_char(tokens, char):
        pos = 0
        for t in list(tokens):
            if t[1] == char:
                return pos
            pos += 1

def find_matching_pair(tokens, opening_char, closing_char):
        pos = 0
        count_opening = 0
        for t in list(tokens):
            if t[1] == closing_char and count_opening == 0:
                return pos
            elif t[1] == closing_char and count_opening != 0:
                count_opening -= 1
            elif t[1] == opening_char:
                count_opening += 1
            pos += 1
        raise SyntaxError(opening_char +' was never closed')

def compile_subroutinedec(curtoken, tokens_left, parsetree):
        # subroutineDec* = ('constructor'|'function'|'method') ('void'|type) subroutineName (parameterList) subroutineBody
        subroutineDec = TreeNode('subroutineDec')

        # 'constructor'|'function'|'method'
        if curtoken[1] not in ('constructor','function','method'):
            pprint(curtoken)
            raise(SyntaxError('error parsing subroutineDec'))
        else:
            subroutineDec.addChild(TreeNode(curtoken[0],curtoken[1]))
            curtoken = tokens_left[0]
            tokens_left = tokens_left[1:]

        # 'void'| type
        if curtoken[1] == 'void':
            curtoken, tokens_left = compile('void', curtoken, tokens_left, subroutineDec)
        else:
            subroutineDec.addChild(TreeNode(curtoken[0],curtoken[1]))
            curtoken = tokens_left[0]
            tokens_left = tokens_left[1:]


        # subroutineName
        subroutineDec.addChild(TreeNode(curtoken[0],curtoken[1]))
        curtoken = tokens_left[0]
        tokens_left = tokens_left[1:]

        curtoken, tokens_left = compile('(', curtoken, tokens_left, subroutineDec)
        parameterList = TreeNode('parameterList')
        if curtoken[1] != ')':
            curtoken, tokens_left = compile_parameterList(curtoken,tokens_left,parameterList)
        subroutineDec.addChild(parameterList)
        curtoken, tokens_left = compile(')', curtoken, tokens_left, subroutineDec)


        # subroutineBody
        subroutineBody = TreeNode('subroutineBody')
        subroutineDec.addChild(subroutineBody)

        curtoken, tokens_left = compile('{', curtoken, tokens_left, subroutineBody)

        # varDec* = 'var' type varName (',' varName)*;
        while curtoken[1] == 'var':
            varDec = TreeNode('varDec')
            curtoken, tokens_left = compile('var', curtoken, tokens_left, varDec)

            # type
            varDec.addChild(TreeNode(curtoken[0],curtoken[1]))
            curtoken = tokens_left[0]
            tokens_left = tokens_left[1:]

            #varName (',' varName)*;
            curtoken, tokens_left = compile_varnames(curtoken, tokens_left, varDec)

            curtoken, tokens_left = compile(';', curtoken, tokens_left, varDec)
            subroutineBody.addChild(varDec)

        # statements*
        # let|if|while|do|return
        #while curtoken[1] in ['let','if','while','do','return']:

        pos = find_matching_pair(tokens_left,'{','}')
        statements = parse_tokens(curtoken,tokens_left[:pos],TreeNode('statements'))

        curtoken = tokens_left[pos]
        tokens_left = tokens_left[pos+1:]

        subroutineBody.addChild(statements)
        curtoken, tokens_left = compile('}', curtoken, tokens_left, subroutineBody)
        parsetree.addChild(subroutineDec)

        return (curtoken, tokens_left)

def compile_varnames(curtoken, tokens_left, parsetree):
    #varName
    parsetree.addChild(TreeNode(curtoken[0],curtoken[1]))
    curtoken = tokens_left[0]
    tokens_left = tokens_left[1:]

    while curtoken[1] == ',':
        curtoken, tokens_left = compile(',', curtoken, tokens_left, parsetree)

        #varName
        parsetree.addChild(TreeNode(curtoken[0],curtoken[1]))
        curtoken = tokens_left[0]
        tokens_left = tokens_left[1:]
    return (curtoken, tokens_left)

def compile_parameterList(curtoken, tokens_left, parsetree):
    # type varName (, type varName)
    parsetree.addChild(TreeNode(curtoken[0],curtoken[1]))
    curtoken = tokens_left[0]
    tokens_left = tokens_left[1:]

    parsetree.addChild(TreeNode(curtoken[0],curtoken[1]))
    curtoken = tokens_left[0]
    tokens_left = tokens_left[1:]

    while curtoken[1] == ',':
        curtoken, tokens_left = compile(',', curtoken, tokens_left, parsetree)

        #type
        parsetree.addChild(TreeNode(curtoken[0],curtoken[1]))
        curtoken = tokens_left[0]
        tokens_left = tokens_left[1:]

        #varName
        parsetree.addChild(TreeNode(curtoken[0],curtoken[1]))
        curtoken = tokens_left[0]
        tokens_left = tokens_left[1:]
    return (curtoken, tokens_left)

def compile_class(curtoken, tokens_left, parsetree):
        # 'class' className '{' classVarDec* subroutineDec* '}'
        node = TreeNode('class')
        curtoken, tokens_left = compile('class', curtoken, tokens_left, node)

        # className
        node.addChild(TreeNode(curtoken[0],curtoken[1]))
        curtoken = tokens_left[0]
        tokens_left = tokens_left[1:]

        curtoken, tokens_left = compile('{', curtoken, tokens_left, node)

        # classVarDec* = (static|field) type varName (, varName)* ;
        if curtoken[1] in ['static', 'field']:
            while curtoken[1] in ['static', 'field']:
                classVarDec = TreeNode('classVarDec')

                # static|field
                classVarDec.addChild(TreeNode(curtoken[0],curtoken[1]))
                curtoken = tokens_left[0]
                tokens_left = tokens_left[1:]
                # type
                classVarDec.addChild(TreeNode(curtoken[0],curtoken[1]))
                curtoken = tokens_left[0]
                tokens_left = tokens_left[1:]

                # varName (, varName)
                curtoken, tokens_left = compile_varnames(curtoken,tokens_left,classVarDec)

                curtoken, tokens_left = compile(';', curtoken, tokens_left, classVarDec)
                node.addChild(classVarDec)

        # subroutineDec* = ('constructor'|'function'|'method') ('void'|type) subroutineName (parameterList) subroutineBody
        while curtoken[1] == 'constructor' or curtoken[1] == 'function' or curtoken[1] == 'method':
            curtoken, tokens_left = compile_subroutinedec(curtoken,tokens_left,node)


        parsetree.addChild(node)

        if curtoken[1] == '}':
            node.addChild(TreeNode(curtoken[0],curtoken[1]))
        else:
             raise(SyntaxError('Could not compile class, missing ending }'))

        return parse_tokens(curtoken, tokens_left, parsetree)

def compile_let(curtoken, tokens_left, parsetree):
        #letStatement = let varName '('[expression]')'? '=' expression ;
        letStatement = TreeNode('letStatement')

        curtoken, tokens_left = compile('let', curtoken, tokens_left, letStatement)

        varname = TreeNode('identifier',curtoken[1])
        letStatement.addChild(varname)
        curtoken = tokens_left[0]
        tokens_left = tokens_left[1:]

        if curtoken[1] == '[':
            expression = TreeNode('expression')

            curtoken, tokens_left = compile('[', curtoken, tokens_left, letStatement)
            pos = find_char(tokens_left,']')
            expressions = compile_expression(curtoken,tokens_left[:pos],expression)
            letStatement.addChild(expressions)
            curtoken = tokens_left[pos]
            tokens_left = tokens_left[pos+1:]

            curtoken, tokens_left = compile(']', curtoken, tokens_left, letStatement)


        curtoken, tokens_left = compile('=', curtoken, tokens_left, letStatement)

        expression = TreeNode('expression')
        pos = find_char(tokens_left,';')
        expressions = compile_expression(curtoken,tokens_left[:pos],expression)
        letStatement.addChild(expressions)
        curtoken = tokens_left[pos]
        tokens_left = tokens_left[pos+1:]

        if len(tokens_left)>0:
            curtoken, tokens_left = compile(';', curtoken, tokens_left, letStatement)
            parsetree.addChild(letStatement)
        else:
            letStatement.addChild(TreeNode(curtoken[0],curtoken[1]))
            parsetree.addChild(letStatement)
            return parsetree
            
        return parse_tokens(curtoken, tokens_left, parsetree)


def compile(token, curtoken, tokens_left, parsetree):
        if curtoken[1] != token:
            message = (curtoken[1] + ' does not match ' + token )
            raise(SyntaxError(message))
        node = TreeNode(curtoken[0],curtoken[1])
        parsetree.addChild(node)
        curtoken = tokens_left[0]
        tokens_left = tokens_left[1:]
        return (curtoken, tokens_left)

def compile_return(curtoken, tokens_left, parsetree):
        returnStatement = TreeNode('returnStatement')
        curtoken, tokens_left = compile('return', curtoken, tokens_left, returnStatement)
        if curtoken[1] != ';':
            expression = TreeNode('expression')
            pos = find_char(tokens_left,';')
            expressions = compile_expression(curtoken,tokens_left[:pos],expression)
            returnStatement.addChild(expressions)
            curtoken = tokens_left[pos]
            tokens_left = tokens_left[pos+1:]

        returnStatement.addChild(TreeNode(curtoken[0],curtoken[1]))
        parsetree.addChild(returnStatement)
        return (curtoken, tokens_left)

def compile_if(curtoken, tokens_left, parsetree):
        #ifStatement = 'if' '(' expression ')' {' statements* '}' (else' '(' expression ')' { statements } ')'?
        ifStatement = TreeNode('ifStatement')

        curtoken, tokens_left = compile('if', curtoken, tokens_left, ifStatement)
        curtoken, tokens_left = compile('(', curtoken, tokens_left, ifStatement)

        #expression = term(op term)*
        pos = find_char(tokens_left,')')
        expression = compile_expression(curtoken,tokens_left[0:pos],TreeNode('expression'))
        ifStatement.addChild(expression)
        curtoken = tokens_left[pos]
        tokens_left = tokens_left[pos+1:]

        curtoken, tokens_left = compile(')', curtoken, tokens_left, ifStatement)

        pos = find_matching_pair(tokens_left,'{','}')
        curtoken, tokens_left = compile('{', curtoken, tokens_left, ifStatement)

        statements = TreeNode('statements')
        if curtoken[1] != '}':
            #pos = find_matching_pair(tokens_left,'{','}')
            ifStatements = parse_tokens(curtoken,tokens_left[:pos-1],statements)
            curtoken = tokens_left[pos-1]
            tokens_left = tokens_left[pos:]

        ifStatement.addChild(statements)

        curtoken, tokens_left = compile('}', curtoken, tokens_left, ifStatement)

        if curtoken[1] == 'else':
            curtoken, tokens_left = compile('else', curtoken, tokens_left, ifStatement)
            pos = find_matching_pair(tokens_left,'{','}')
            curtoken, tokens_left = compile('{', curtoken, tokens_left, ifStatement)

            if curtoken[1] == '}':
                ifStatement.addChild(TreeNode('statements'))
            else:
                # find matching }
                #TODO fix
                elseStatements = parse_tokens(curtoken,tokens_left[:pos],TreeNode('statements'))
                curtoken = tokens_left[pos-1]
                tokens_left = tokens_left[pos:]
                ifStatement.addChild(elseStatements)
            curtoken, tokens_left = compile('}', curtoken, tokens_left, ifStatement)

        parsetree.addChild(ifStatement)
        return parse_tokens(curtoken, tokens_left, parsetree)

def compile_do(curtoken, tokens_left, parsetree):
        #doStatement = do identifier '.' identifier(expressionList*) ;
        doStatement = TreeNode('doStatement')

        curtoken, tokens_left = compile('do', curtoken, tokens_left, doStatement)

        varname = TreeNode('identifier',curtoken[1])
        doStatement.addChild(varname)
        curtoken = tokens_left[0]
        tokens_left = tokens_left[1:]

        if curtoken[1] == '.':
            curtoken, tokens_left = compile('.', curtoken, tokens_left, doStatement)

            varname = TreeNode('identifier',curtoken[1])
            doStatement.addChild(varname)
            curtoken = tokens_left[0]
            tokens_left = tokens_left[1:]

        #expressionList*
        curtoken, tokens_left = compile('(', curtoken, tokens_left, doStatement)
        pos = find_matching_pair(tokens_left,'(',')')
        pprint(curtoken)
        pprint(tokens_left[:pos])
        expressionList = compile_expressionList(curtoken, tokens_left[:pos], doStatement)
        print_tree(expressionList)
        print("TODO")
        exit()
        curtoken = tokens_left[pos-1]
        tokens_left = tokens_left[pos:]

        curtoken, tokens_left = compile(')', curtoken, tokens_left, doStatement)


        if len(tokens_left)>0:
            curtoken, tokens_left = compile(';', curtoken, tokens_left, doStatement)
            parsetree.addChild(doStatement)
        else:
            doStatement.addChild(TreeNode(curtoken[0],curtoken[1]))
            parsetree.addChild(doStatement)
            return parsetree

        return parse_tokens(curtoken, tokens_left, parsetree)

def compile_while(curtoken, tokens_left, parsetree):
        # whileStatement = 'while' '(' expression ')' '{' statements '}'
        whileStatement = TreeNode('whileStatement')

        curtoken, tokens_left = compile('while', curtoken, tokens_left, whileStatement)

        curtoken, tokens_left = compile('(', curtoken, tokens_left, whileStatement)


        expression = TreeNode('expression')
        # find matching )
        pos = find_matching_pair(tokens_left,'(',')')

        expressions = compile_expression(curtoken,tokens_left[:pos],expression)

        whileStatement.addChild(expressions)
        curtoken = tokens_left[pos]
        tokens_left = tokens_left[pos+1:]

        curtoken, tokens_left = compile(')', curtoken, tokens_left, whileStatement)

        curtoken, tokens_left = compile('{', curtoken, tokens_left, whileStatement)

        # find matching }
        pos = find_matching_pair(tokens_left,'{','}')+1
        statements = parse_tokens(curtoken,tokens_left[:pos-1],TreeNode('statements'))

        whileStatement.addChild(statements)
        curtoken = tokens_left[pos-1]
        tokens_left = tokens_left[pos:]


        if len(tokens_left)>0:
            curtoken, tokens_left = compile('}', curtoken, tokens_left, whileStatement)
            parsetree.addChild(whileStatement)
        else:
            whileStatement.addChild(TreeNode(curtoken[0],curtoken[1]))
            parsetree.addChild(whileStatement)
            return parsetree

        return parse_tokens(curtoken, tokens_left, parsetree)

def compile_expressionList(curtoken, tokens_left, parsetree):
    # expressionList = (expression (', expression)* )? 
    expressionList = TreeNode('expressionList')

    while curtoken[1] != ')':
        pos = find_char(tokens_left,',')
        if pos == None:
            pos = len(tokens_left)
            expressions = compile_expression(curtoken,tokens_left[:pos],TreeNode('expression'))
            return expressionList
        else:
            expressions = compile_expression(curtoken,tokens_left[:pos],TreeNode('expression'))
            curtoken = tokens_left[pos]
            tokens_left = tokens_left[pos+1:]

        expressionList.addChild(expressions)

        if curtoken[1] == ',':
            curtoken, tokens_left = compile(',', curtoken, tokens_left, expressionList)

    return expressionList


def compile_expression(curtoken, tokens_left, parsetree):
    #expression = term (op term)*

    term = TreeNode('term')

    while len(tokens_left) > 0:
        if curtoken[0] == 'symbol' and curtoken[1] in OPERATORS:
            #add current term to parsetree and start new term
            parsetree.addChild(term)
            term = TreeNode('term')
            parsetree.addChild(TreeNode(curtoken[0],curtoken[1]))
            curtoken = tokens_left[0]
            tokens_left = tokens_left[1:]
        elif curtoken[0] == 'symbol' and curtoken[1] == '(':
            expressionList = TreeNode('expressionList')
            expression = TreeNode('expression')
            pos = find_matching_pair(tokens_left,'(',')')
            curtoken, tokens_left = compile('(', curtoken, tokens_left, term)
            children = compile_expression(curtoken,tokens_left[:pos-1],expression)
            expressionList.addChild(children)
            term.addChild(expressionList)
            curtoken = tokens_left[pos-1]
            tokens_left = tokens_left[pos:]
        elif curtoken[0] == 'symbol' and curtoken[1] == '[':
            expression = TreeNode('expression')
            pos = find_matching_pair(tokens_left,'[',']')
            curtoken, tokens_left = compile('[', curtoken, tokens_left, term)
            children = compile_expression(curtoken,tokens_left[:pos-1],expression)
            term.addChild(expression)
            curtoken = tokens_left[pos-1]
            tokens_left = tokens_left[pos:]
        else:
            term.addChild(TreeNode(curtoken[0],curtoken[1]))
            curtoken = tokens_left[0]
            tokens_left = tokens_left[1:]

    term.addChild(TreeNode(curtoken[0],curtoken[1]))
    parsetree.addChild(term)
    return parsetree


def parse_tokens(curtoken, tokens_left, parsetree):

    """
    print("---")
    print("curtoken:")
    print(curtoken)
    print("tokens left:")
    print(tokens_left)
    print("")
    print("")
    """

    if curtoken[0] == 'integerConstant':
        term = TreeNode('term')
        curnode = TreeNode('constant',curtoken[1])
        term.addChild(curnode)
        parsetree.addChild(term)
    elif curtoken[0] == 'keyword' and curtoken[1] == 'class':
        return compile_class(curtoken, tokens_left, parsetree)
    elif curtoken[0] == 'keyword' and curtoken[1] == 'let':
        return compile_let(curtoken, tokens_left, parsetree)
    elif curtoken[0] == 'keyword' and curtoken[1] == 'if':
        return compile_if(curtoken, tokens_left, parsetree)
    elif curtoken[0] == 'keyword' and curtoken[1] == 'do':
        return compile_do(curtoken, tokens_left, parsetree)
    elif curtoken[0] == 'keyword' and curtoken[1] == 'while':
        return compile_while(curtoken, tokens_left, parsetree)
    elif curtoken[0] == 'keyword' and curtoken[1] == 'return':
        curtoken, tokens_left = compile_return(curtoken, tokens_left, parsetree)
    else:
        curnode = TreeNode(curtoken[0],curtoken[1])
        parsetree.addChild(curnode)

    if len(tokens_left) == 0:
        return parsetree
    else:
        curtoken = tokens_left[0]
        tokens_left = tokens_left[1:]
        return parse_tokens(curtoken, tokens_left, parsetree)



filename = sys.argv[1]
with open(filename, 'r') as f:
    lines = [line for line in f]

#lines = ['while (count < 100) {', 'let count = count + 1;' , '}', 'while (count < 220) {', 'let count = count + 2;' , '}']
#lines = ['while (count < 100) {', 'let count = count + 1;','let foo = foo + 1;' , '}']
#lines = ['class SquareGame {','field Square square;','}']
#lines = ['class SquareGame {','function void main() {', 'do Output.printInt(sum / length);', 'return;', '}', '}']


tokens = tokenize(lines)

root = TreeNode('root')
curtoken = tokens[0]
parsetree = parse_tokens(curtoken, tokens[1:], root)
#print_tree(parsetree)

def print_tokens(doc, tokens):
    element = doc.createElement('tokens')
    for token in tokens:
        e = doc.createElement(token[0])
        text_node = doc.createTextNode(token[1])
        e.appendChild(text_node)
        element.appendChild(e)
    doc.appendChild(element)
    print(doc.documentElement.toprettyxml().strip())

def create_xml_tree(doc,element,parsetree):
    e = doc.createElement(parsetree.name)
    if parsetree.value != None:
        text_node = doc.createTextNode(parsetree.value)
        e.appendChild(text_node)
    element.appendChild(e)

    if len(parsetree.children) == 0:
        return doc
    
    for children in parsetree.children:
        create_xml_tree(doc, e, children)

doc = xml.dom.minidom.Document()

# print tokens:
#print_tokens(doc,tokens)
#exit()

create_xml_tree(doc,doc,parsetree)

#print(doc.documentElement.toprettyxml(indent="  ").strip())
#print(doc.documentElement.toprettyxml().strip())
rootTag = doc.documentElement.getElementsByTagName('class')[0]
print(rootTag.toprettyxml(indent="  ").strip())
