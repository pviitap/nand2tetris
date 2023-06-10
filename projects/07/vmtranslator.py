import sys
import re

SP_ADDRESS = 0
SP_START_VALUE = 256
LCL_ADDRESS = 1
ARG_ADDRESS = 2
THIS_ADDRESS = 3
THAT_ADDRESS = 4
TEMP_ADDRESS_START = 5
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

    def write_end_loop(this) -> None:
        print('(END)')
        print('  @END')
        print('  0;JMP')

    def write_push_to_constant(this, value: int) -> None:
        print('  @' + str(abs(value)))
        print('  D=A')
        print('  @SP')
        print('  A=M')
        if int(value) >= 0:
            print('  M=D')
        else:
            print('  M=-D')
        this.write_increment_sp()

    def write_pop_to(this, base_address: int, index: int):
        # SP--
        # RAM[ RAM[base_address] + index ] <- RAM[SP]

        this.write_decrement_sp()

        print('  @' + str(base_address))
        print('  D=M')
        print('  @' + str(index))
        print('  D=A+D')
        print('  @tmp')
        print('  M=D')

        print('  @SP')
        print('  A=M')
        print('  D=M')

        print('  @tmp')
        print('  A=M')
        print('  M=D')


    def write_push_to(this, base_address: int, index: int):
        # RAM[SP] <- RAM[ RAM[base_address] + index ]
        # SP++
        print('  @' + str(base_address))
        print('  D=M')
        print('  @' + str(index))
        print('  D=A+D')
        print('  A=D')
        print('  D=M')


        print('  @SP')
        print('  A=M')
        print('  M=D')
        this.write_increment_sp()

    def write_pop_to_pointer(this, index: int):
        # SP--
        # RAM[ index ] <- RAM[SP]

        this.write_decrement_sp()

        print('  @SP')
        print('  A=M')
        print('  D=M')

        print('  @' + str(index))
        print('  M=D')


    def write_push_to_pointer(this, index: int):
        # RAM[SP] <- RAM[ index ]
        # SP++
        print('  @' + str(index))
        print('  D=M')

        print('  @SP')
        print('  A=M')
        print('  M=D')
        this.write_increment_sp()


    def write_not(this) -> None:
        this.write_operate_stack_top_value('!')
    def write_neg(this) -> None:
        this.write_operate_stack_top_value('-')

    def write_and(this) -> None:
        this.write_stack_operation('&')
    def write_add(this) -> None:
        this.write_stack_operation('+')
    def write_sub(this) -> None:
        this.write_stack_operation('-')
    def write_or(this) -> None:
        this.write_stack_operation('|')

    def write_eq(this) -> None:
        this.write_compare_stack_values('JEQ')
    def write_lt(this) -> None:
        this.write_compare_stack_values('JLT')
    def write_gt(this) -> None:
        this.write_compare_stack_values('JGT')

    def write_increment_sp(this) -> None:
        print('  @SP')
        print('  M=M+1')

    def write_decrement_sp(this) -> None:
        print('  @SP')
        print('  M=M-1')

    def write_stack_operation(this, op: str) -> None:
        # Pop first value from stack
        this.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')
        print('  @tmp')
        print('  M=D')

        # Pop second value from stack
        this.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')

        # Write operation for first and second values
        print('  @tmp')
        print('  D=D'+op+'M')

        # Save result to stack
        print('  @SP')
        print('  A=M')
        print('  M=D')

        this.write_increment_sp()

    def write_operate_stack_top_value(this, op: str) -> None:
        # Pop first value from stack
        this.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')

        # Write operation and save result to stack
        print('  @SP')
        print('  A=M')
        print('  M='+op +'D')
        this.write_increment_sp()

    def write_compare_stack_values(this, op: str):
        c = codeWriter.get_next_label_count()

        # Pop first value from stack
        this.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')
        print('  @tmp')
        print('  M=D')

        # Pop second value from stack
        this.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')


        # Compare values
        print('  @tmp')
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
            codeWriter.write_push_to_constant(parsed_value)
        case _ if instruction.startswith('push local'):
            parsed_value = int(re.search(r'^push local (\d+)', instruction).group(1))
            codeWriter.write_push_to(LCL_ADDRESS, parsed_value)
        case _ if instruction.startswith('push that'):
            parsed_value = int(re.search(r'^push that (\d+)', instruction).group(1))
            codeWriter.write_push_to(THAT_ADDRESS, parsed_value)
        case _ if instruction.startswith('push this'):
            parsed_value = int(re.search(r'^push this (\d+)', instruction).group(1))
            codeWriter.write_push_to(THIS_ADDRESS, parsed_value)
        case _ if instruction.startswith('push argument'):
            parsed_value = int(re.search(r'^push argument (\d+)', instruction).group(1))
            codeWriter.write_push_to(ARG_ADDRESS, parsed_value)
        case _ if instruction.startswith('push temp'):
            parsed_value = int(re.search(r'^push temp (\d+)', instruction).group(1))
            codeWriter.write_push_to_pointer(TEMP_ADDRESS_START + parsed_value)
        case _ if instruction.startswith('pop local'):
            parsed_value = int(re.search(r'^pop local (\d+)', instruction).group(1))
            codeWriter.write_pop_to(LCL_ADDRESS, parsed_value)
        case _ if instruction.startswith('pop argument'):
            parsed_value = int(re.search(r'^pop argument (\d+)', instruction).group(1))
            codeWriter.write_pop_to(ARG_ADDRESS, parsed_value)
        case _ if instruction.startswith('pop this'):
            parsed_value = int(re.search(r'^pop this (\d+)', instruction).group(1))
            codeWriter.write_pop_to(THIS_ADDRESS, parsed_value)
        case _ if instruction.startswith('pop that'):
            parsed_value = int(re.search(r'^pop that (\d+)', instruction).group(1))
            codeWriter.write_pop_to(THAT_ADDRESS, parsed_value)
        case _ if  instruction.startswith('pop temp'):
            parsed_value = int(re.search(r'^pop temp (\d+)', instruction).group(1))
            codeWriter.write_pop_to_pointer(TEMP_ADDRESS_START + parsed_value)
        case _ if instruction.startswith('pop pointer 0'):
            codeWriter.write_pop_to_pointer(THIS_ADDRESS)
        case _ if instruction.startswith('pop pointer 1'):
            codeWriter.write_pop_to_pointer(THAT_ADDRESS)
        case _ if instruction.startswith('push pointer 0'):
            codeWriter.write_push_to_pointer(THIS_ADDRESS)
        case _ if instruction.startswith('push pointer 1'):
            codeWriter.write_push_to_pointer(THAT_ADDRESS)
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

codeWriter.write_end_loop()

