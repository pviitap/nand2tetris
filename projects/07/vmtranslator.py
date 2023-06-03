import sys
import re

SP_ADDRESS = 0
SP_START_VALUE = 256
LCL_ADDRESS = 1
ARG_ADDRESS = 2
THIS_ADDRESS = 3
THAT_ADDRESS = 4
TEMP_ADDRESS = 5
STATIC_ADDRESS = 16

class CodeWriter:
    label_count: int =1
    def get_next_label_count(this) -> int:
        this.label_count += 1
        return this.label_count

    def write_initialize_stack(this) -> None:
        print('  @' + str(SP_START_VALUE))
        print('  D=A')
        print('  @SP')
        print('  M=D')

    def write_push_constant(this, value: int) -> None:
        print('  @' + str(abs(value)))
        print('  D=A')
        print('  @SP')
        print('  A=M')
        if int(value) >= 0:
            print('  M=D')
        else:
            print('  M=-D')
        this.write_increment_sp()

    def write_not(this) -> None:
        this.write_operate_next_value('!')
    def write_neg(this) -> None:
        this.write_operate_next_value('-')

    def write_and(this) -> None:
        this.write_operate_next_values('&')
    def write_add(this) -> None:
        this.write_operate_next_values('+')
    def write_sub(this) -> None:
        this.write_operate_next_values('-')
    def write_or(this) -> None:
        this.write_operate_next_values('|')

    def write_eq(this) -> None:
        this.write_compare_values('JEQ')
    def write_lt(this) -> None:
        this.write_compare_values('JLT')
    def write_gt(this) -> None:
        this.write_compare_values('JGT')


    def write_increment_sp(this) -> None:
        print('  @SP')
        print('  M=M+1')

    def decrement_sp(this) -> None:
        print('  @SP')
        print('  M=M-1')

    def write_operate_next_values(this, op: str) -> None:
        # Pop first value from stack
        this.decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')
        print('  @tempvalue')
        print('  M=D')

        # Pop second value from stack
        this.decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')

        # Write operation for first and second values
        print('  @tempvalue')
        print('  D=D'+op+'M')

        # Save result to stack
        print('  @SP')
        print('  A=M')
        print('  M=D')

        this.write_increment_sp()

    def write_operate_next_value(this, op: str) -> None:
        # Pop first value from stack
        this.decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')

        # Write operation and save result to stack
        print('  @SP')
        print('  A=M')
        print('  M='+op +'D')
        this.write_increment_sp()

    def write_compare_values(this, op: str):
        c = codeWriter.get_next_label_count()

        # Pop first value from stack
        this.decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')
        print('  @tempvalue')
        print('  M=D')

        # Pop second value from stack
        this.decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')


        # Compare values
        print('  @tempvalue')
        print('  D=D-M')
        print('  @IS_TRUE' +str(c))
        print('  D;'+ op)

        print('  //false -> save 0 to stack')
        print('  @SP')
        print('  D=M')
        print('  A=D')
        print('  M=0')
        print('  @CONTINUE' + str(c))
        print('  0;JMP')

        print('  //true -> save -1 to stack')
        print('(IS_TRUE' + str(c) +')  ')
        print('  @SP')
        print('  D=M')
        print('  A=D')
        print('  M=-1')
        print('  @CONTINUE' + str(c))
        print('  0;JMP')


        print('(CONTINUE' + str(c) +')  ')

        this.write_increment_sp()

def translate(instruction: str, codeWriter: CodeWriter):
    match instruction:
        case 'add':
            codeWriter.write_add()
        case 'sub':
            codeWriter.write_sub()
        case 'neg':
            codeWriter.write_neg()
        case 'eq':
            codeWriter.write_eq()
        case 'lt':
            codeWriter.write_lt()
        case 'gt':
            codeWriter.write_gt()
        case 'and':
            codeWriter.write_and()
        case 'or':
            codeWriter.write_or()
        case 'not':
            codeWriter.write_not()
        case _ if instruction.startswith('push constant'):
            parsed_value = int(re.search(r'^push constant (\d+)', instruction).group(1))
            codeWriter.write_push_constant(parsed_value)
        case _ if instruction.startswith('push local'):
            parsed_value = int(re.search(r'^push local (\d+)', instruction).group(1))
        case _ if instruction.startswith('pop local'):
            parsed_value = int(re.search(r'^pop local (\d+)', instruction).group(1))
        case _ if instruction.startswith('pop argument'):
            parsed_value = int(re.search(r'^pop argument (\d+)', instruction).group(1))
        case _ if instruction.startswith('pop this'):
            parsed_value = int(re.search(r'^pop this (\d+)', instruction).group(1))
        case _ if instruction.startswith('pop that'):
            parsed_value = int(re.search(r'^pop that (\d+)', instruction).group(1))
        case _ if  instruction.startswith('pop temp'):
            parsed_value = int(re.search(r'^pop temp (\d+)', instruction).group(1))
        case _ :
            raise Exception('Unknown instruction ' + instruction)


def parse_file(filename: str):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.strip().split("\n")
    return lines
filename = sys.argv[1]
lines = parse_file(filename)
line_number = 0

codeWriter = CodeWriter()
codeWriter.write_initialize_stack()
for line in lines:
    line_number += 1
    if '//' in line:
        line = line.split('//')[0]
    if line == '':
        continue
    line = line.strip()
    translate(line, codeWriter)

