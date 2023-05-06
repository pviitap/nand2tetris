import sys
import re

SP_ADDRESS = 0
LCL_ADDRESS = 1
ARG_ADDRESS = 2
THIS_ADDRESS = 3
THAT_ADDRESS = 4
TEMP_ADDRESS = 5
STATIC_ADDRESS = 16

def parse_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.strip().split("\n")
    return lines

def save_value_to_address(address, value):
    print('@' + str(abs(value)))
    print('D=A')
    print('@' + str(address))
    if int(value) >= 0:
        print('M=D')
    else:
        print('M=-D')

class Stack:
    sp = None
    stack = []

    def __init__(this, sp):
        this.sp = sp

    def push(this, value):
        this.stack.append(value)
        save_value_to_address(this.sp, value) 
        this.sp += 1
        save_value_to_address(SP_ADDRESS, this.sp)
    def pop(this):
        this.sp -= 1
        save_value_to_address(SP_ADDRESS, this.sp)
        return this.stack.pop()
    

def translate(instruction, stack):
    if instruction.startswith('push'):
        parsed_value = re.search(r'^push constant (\d+)', instruction).group(1)
        stack.push(int(parsed_value))
    elif instruction.startswith('pop local'):
        parsed_value = re.search(r'^pop local (\d+)', instruction).group(1)
        first = stack.pop()
    elif instruction.startswith('add'):
        stack.push(stack.pop() + stack.pop())
    elif instruction.startswith('sub'):
        value1 = stack.pop()
        value2 = stack.pop()
        stack.push(value2-value1)
    elif instruction.startswith('neg'):
        stack.push(-1 * stack.pop())
    elif instruction.startswith('eq'):
        if stack.pop() == stack.pop():
            stack.push(-1)
        else:
            stack.push(0)
    elif instruction.startswith('lt'):
        if stack.pop() > stack.pop():
            stack.push(-1)
        else:
            stack.push(0)
    elif instruction.startswith('gt'):
        if stack.pop() < stack.pop():
            stack.push(-1)
        else:
            stack.push(0)
    elif instruction.startswith('and'):
        stack.push(stack.pop() & stack.pop())
    elif instruction.startswith('or'):
        stack.push(stack.pop() | stack.pop())
    elif instruction.startswith('not'):
        stack.push(~stack.pop()) 
    else:
        raise Exception('Unknown instruction ' + instruction)

    return stack


stack = Stack(256)

filename = sys.argv[1]
lines = parse_file(filename)
line_number = 0
for line in lines:
    line_number += 1
    if '//' in line:
        line = line.split('//')[0]
    if line == '':
        continue
    line = line.strip()
    stack = translate(line, stack)

