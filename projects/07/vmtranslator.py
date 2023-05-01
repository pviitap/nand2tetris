import sys
import re


def parse_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.strip().split("\n")
    return lines


def save_value_to_address(address, value):
    print('@' + str(abs(int(value))))
    print('D=A')
    print('@' + str(address))
    if int(value) >= 0:
        print('M=D')
    else:
        print('M=-D')


def translate(instruction, stack):
    if instruction.startswith('push'):
        value = re.search(r'^push constant (\d+)', instruction).group(1)
        stack.append(int(value))
    elif instruction.startswith('add'):
        first = stack.pop()
        second = stack.pop()
        value = first + second
        stack.append(value)
    elif instruction.startswith('sub'):
        first = stack.pop()
        second = stack.pop()
        value = second - first
        print("// " + str(first) + "-" + str(second) + " = " + str(value))
        stack.append(value)
    elif instruction.startswith('neg'):
        first = stack.pop()
        value = -1 * first
        stack.append(value)
    elif instruction.startswith('eq'):
        first = stack.pop()
        second = stack.pop()
        if first == second:
            stack.append(-1)
        else:
            stack.append(0)
    elif instruction.startswith('lt'):
        first = stack.pop()
        second = stack.pop()
        if first > second:
            stack.append(-1)
        else:
            stack.append(0)
    elif instruction.startswith('gt'):
        first = stack.pop()
        second = stack.pop()
        if first < second:
            stack.append(-1)
        else:
            stack.append(0)
    elif instruction.startswith('and'):
        first = stack.pop()
        second = stack.pop()
        value = first & second
        stack.append(value)
    elif instruction.startswith('or'):
        first = stack.pop()
        second = stack.pop()
        value = first | second
        stack.append(value)
    elif instruction.startswith('not'):
        first = stack.pop()
        value = ~first
        stack.append(value)
    else:
        raise Exception('Unknown instruction ' + instruction)

    return stack


line_number = 0
stack = []
variable_names_lookup_table = {}
SP_ADDRESS = 0

filename = sys.argv[1]
lines = parse_file(filename)
for line in lines:
    line_number += 1
    if '//' in line:
        line = line.split('//')[0]
    if line == '':
        continue
    line = line.strip()
    stack = translate(line, stack)

sp = 256
for s in stack:
    save_value_to_address(sp, s)
    sp += 1

save_value_to_address(SP_ADDRESS, sp)
