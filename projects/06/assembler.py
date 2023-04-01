import sys
import re

START_ADDRESS_FOR_USER_DEFINED_VARIABLES = 10
DESTINATIONS = ['null', 'M', 'D', 'MD', 'A', 'AM', 'AD', 'AMD']
JUMPS = ['null', 'JGT', 'JEQ', 'JGE', 'JLT', 'JNE', 'JLE', 'JMP']
COMPUTE_BITS = {
    # when a=0:
    '0': '101010',
    '1': '111111',
    '-1': '111010',
    'D': '001100',
    'A': '110000',
    '!D': '001101',
    '!A': '110001',
    '-D': '001111',
    '-A': '110011',
    'D+1': '011111',
    'A+1': '110111',
    'D-1': '001110',
    'A-1': '110010',
    'D+A': '000010',
    'D-A': '010011',
    'A-D': '000111',
    'D&A': '000000',
    'D|A': '010101',
    # when a=1:
    'M': '110000',
    '!M': '110001',
    '-M': '110011',
    'M+1': '110111',
    'M-1': '110010',
    'D+M': '000010',
    'D-M': '010011',
    'M-D': '000111',
    'D&M': '000000',
    'D|M': '010101',
}


def parse_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.strip().split("\n")
    return lines


def is_a_instruction(instruction):
    return instruction.startswith('@')


def is_c_instruction(instruction):
    return not is_a_instruction(instruction) and not is_label(instruction)


def is_label(instruction):
    return instruction.startswith('(')


def parse_jump(instruction):
    if instruction.find(';') != -1:  # jump
        jmp = instruction.split(';')[1]
        jmp = bin(JUMPS.index(jmp))[2::].zfill(3)
    else:
        jmp = '000'
    return jmp


def parse_dest(instruction):
    if instruction.find('=') != -1:
        dest = instruction.split('=')[0]
        dest = bin(DESTINATIONS.index(dest))[2::].zfill(3)
    else:
        dest = '000'
    return dest


def parse_a(instruction):
    if instruction.find(';') != -1:
        return '0'
    elif instruction.find('=') != -1:
        var = instruction.split('=')[1]
        if var.find('M') != -1:
            return '1'
        else:
            return '0'


def parse_compute_bits(instruction):
    if instruction.find('=') != -1:
        comp = COMPUTE_BITS[instruction.split('=')[1]]
    elif instruction.find(';') != -1:
        comp = COMPUTE_BITS[instruction.split(';')[0]]
    else:
        raise Exception("Unknown comp instruction")
    return comp


def lookup_variable(value):
    if value in variable_names_lookup_table:
        return variable_names_lookup_table[value]
    else:
        # Append to lookup table
        if len(variable_names_lookup_table) == 0:
            variable_names_lookup_table[value] = START_ADDRESS_FOR_USER_DEFINED_VARIABLES
        else:
            next_number = max(variable_names_lookup_table.values()) + 1
            variable_names_lookup_table[value] = next_number
    return variable_names_lookup_table[value]


def assemble(instruction):
    if is_a_instruction(instruction):
        value = instruction.split('@')[1]
        if re.match(r"^@(\d+)", instruction):
            value = re.search(r"^@(\d+)", instruction).group(1)
            return bin(int(value))[2:].zfill(16)
        elif re.match(r"^R(\d+)", value):  # (R0,R1,R2 refers to RAM[0],RAM[1],RAM[2]...)
            address_number = re.search(r"^R(\d+)", value).group(1)
            return bin(int(address_number))[2:].zfill(16)
        else:
            address_number = lookup_variable(value)
            return bin(int(address_number))[2:].zfill(16)
    elif is_c_instruction(instruction):
        jmp = parse_jump(instruction)
        dest = parse_dest(instruction)
        comp = parse_compute_bits(instruction)
        a = parse_a(instruction)
        return '111' + a + comp + dest + jmp
    elif is_label(instruction):
        label = instruction.strip('(').strip(')')
        address_number = lookup_variable(label)
        return bin(int(address_number))[2:].zfill(16)
    else:
        raise Exception('Unknown instruction')


filename = sys.argv[1]
line_number = 0
variable_names_lookup_table = {}

lines = parse_file(filename)
for line in lines:
    line_number += 1
    if '//' in line:
        line = line.split('//')[0]
    if line == '':
        continue

    line = line.strip()
    print(assemble(line))
