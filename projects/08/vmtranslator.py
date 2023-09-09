import sys
import re

SP_ADDRESS = 0
SP_START_VALUE = 256
LCL_ADDRESS = 1
ARG_ADDRESS = 2
THIS_ADDRESS = 3
THAT_ADDRESS = 4
TEMP_ADDRESS_START = 5
STATIC_ADDRESS_START = 16

class CodeWriter:
    label_count: int = 0
    def generate_label(self, prefix: str) -> int:
        self.label_count += 1
        return prefix + str(self.label_count)

    def write_init(self) -> None:
        print('''
    @{SP_START_VALUE}
    D=A
    @SP
    M=D
            '''.format(SP_START_VALUE=str(SP_START_VALUE)))

    def write_end_loop(self) -> None:
        print('''
    (END)
      @END
      0;JMP
            ''')

    def write_push_constant(self, value: int) -> None:
        print('  @' + str(abs(value)))
        print('  D=A')
        print('  @SP')
        print('  A=M')
        if int(value) >= 0:
            print('  M=D')
        else:
            print('  M=-D')
        self.write_increment_sp()

    def write_pop_to(self, base_address: int, index: int):
        # SP--
        # RAM[ RAM[base_address] + index ] <- RAM[SP]

        self.write_decrement_sp()

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


    def write_push_from(self, base_address: int, index: int):
        # RAM[SP] <- RAM[ RAM[base_address] + index ]
        # SP++
        print(' // push to address ' + str(base_address) + ', index ' + str(index))
        print('  @' + str(base_address))
        print('  D=M')
        print('  @' + str(index))
        print('  D=A+D')
        print('  A=D')
        print('  D=M')


        print('  @SP')
        print('  A=M')
        print('  M=D')
        self.write_increment_sp()

    def write_save(self, base_address: int ):
        # RAM[SP] <- base_address
        # SP++
        print(' // save ' + str(base_address))
        print('  @' + str(base_address))
        print('  D=M')
        print('  @SP')
        print('  A=M')
        print('  M=D')
        self.write_increment_sp()

    def write_init_zero(self, base_address: int, index: int):
        print('  @' + str(base_address))
        print('  D=M')
        print('  @' + str(index))
        print('  D=A+D')
        print('  A=D')
        print('  M=0')

    def write_pop_pointer(self, index: int):
        # SP--
        # RAM[ index ] <- RAM[SP]

        self.write_decrement_sp()

        print('  @SP')
        print('  A=M')
        print('  D=M')

        print('  @' + str(index))
        print('  M=D')


    def write_push_pointer(self, index: int):
        # RAM[SP] <- RAM[ index ]
        # SP++
        print('  @' + str(index))
        print('  D=M')

        print('  @SP')
        print('  A=M')
        print('  M=D')
        self.write_increment_sp()


    def write_not(self) -> None:
        self.write_operate_stack_top_value('!')
    def write_neg(self) -> None:
        self.write_operate_stack_top_value('-')

    def write_and(self) -> None:
        self.write_stack_operation('&')
    def write_add(self) -> None:
        self.write_stack_operation('+')
    def write_sub(self) -> None:
        self.write_stack_operation('-')
    def write_or(self) -> None:
        self.write_stack_operation('|')

    def write_eq(self) -> None:
        self.write_compare_stack_values('JEQ')
    def write_lt(self) -> None:
        self.write_compare_stack_values('JLT')
    def write_gt(self) -> None:
        self.write_compare_stack_values('JGT')

    def write_increment_sp(self) -> None:
        print('  @SP')
        print('  M=M+1')

    def write_decrement_sp(self) -> None:
        print('  @SP')
        print('  M=M-1')

    def write_stack_operation(self, op: str) -> None:
        # Pop first value from stack
        self.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')

        # Pop second value from stack
        self.write_decrement_sp()
        print('  @SP')
        print('  A=M')

        # Write operation for first and second values
        print('  D=M'+op+'D')

        # Save result to stack
        print('  @SP')
        print('  A=M')
        print('  M=D')

        self.write_increment_sp()

    def write_operate_stack_top_value(self, op: str) -> None:
        # Pop first value from stack
        self.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')

        # Write operation and save result to stack
        print('  @SP')
        print('  A=M')
        print('  M='+op +'D')
        self.write_increment_sp()

    def write_compare_stack_values(self, op: str):
        tmp_label = codeWriter.generate_label('_')

        # Pop first value from stack
        self.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')
        print('  @tmp')
        print('  M=D')

        # Pop second value from stack
        self.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')


        # Compare values
        print('  @tmp')
        print('  D=D-M')
        print('  @IS_TRUE' +str(tmp_label))
        print('  D;'+ op)

        print('  //false -> save 0 to stack')
        print('  @SP')
        print('  D=M')
        print('  A=D')
        print('  M=0')
        print('  @CONTINUE' + str(tmp_label))
        print('  0;JMP')

        print('  //true -> save -1 to stack')
        print('(IS_TRUE' + str(tmp_label) +')  ')
        print('  @SP')
        print('  D=M')
        print('  A=D')
        print('  M=-1')
        print('  @CONTINUE' + str(tmp_label))
        print('  0;JMP')


        print('(CONTINUE' + str(tmp_label) +')  ')

        self.write_increment_sp()

    def write_push_generate_label(self) -> str:
        label = self.generate_label('return_')

        print('  @' + label )
        print('  D=A')
        print('  @SP')
        print('  A=M')
        print('  M=D')
        self.write_increment_sp()
        return label

    def write_label(self, label: str) -> None:
        print('(' + label + ')')

    def write_if(self, label: str) -> None:
        self.write_decrement_sp()
        print('  @SP')
        print('  A=M')
        print('  D=M')
        print('  @' + label )
        print('  D;JNE')

    def write_goto(self, label: str) -> None:
        print('  @' + label )
        print('  0;JMP')

    def write_function(self, function_name: str, num_locals: int) -> None:
        self.write_label(function_name)
        for i in range(0, num_locals):
            print('  // initialize local ' + str(i))
            self.write_init_zero(LCL_ADDRESS, i)
            self.write_increment_sp()
        
    def write_call(self, function_name: str, num_args: int) -> None:
        # Generate label for return address and save it to stack
        return_address_label = self.write_push_generate_label()

        # Save LCL of the calling function
        self.write_save(LCL_ADDRESS)
        # Save ARG of the calling function
        self.write_save(ARG_ADDRESS)
        # Save THIS of the calling function
        self.write_save(THIS_ADDRESS)
        # Save THAT of the calling function
        self.write_save(THAT_ADDRESS)

        # Reposition ARG = SP-n-5 (n = number of args)
        print('  @5')
        print('  D=A')
        print('  @' + str(num_args))
        print('  D=A+D')
        print('  @SP')
        print('  D=M-D')
        print('  @' + str(ARG_ADDRESS))
        print('  M=D')

        # Reposition LCL = SP
        print('  @SP')
        print('  D=M')
        print('  @' + str(LCL_ADDRESS))
        print('  M=D')

        # Transfer control
        self.write_goto(function_name)
        # Declare a label for the return address
        self.write_label(return_address_label)

    def write_return(self) -> None:


        # FRAME = LCL
        print('  @' + str(LCL_ADDRESS))
        print('  D=M' )
        print('  @FRAME' )
        print('  M=D' )

        # RET = *(FRAME-5)
        print('  @FRAME' )
        print('  D=M' )
        print('  @5' )
        print('  D=D-A' )
        print('  A=D' )
        print('  D=M' )
        print('  @RET' )
        print('  M=D' )

        # *ARG = pop()
        self.write_decrement_sp()
        print('  @SP' )
        print('  A=M' )
        print('  D=M' )
        print('  @' + str(ARG_ADDRESS))
        print('  A=M' )
        print('  M=D' )

        # SP = ARG+1
        print('  @' + str(ARG_ADDRESS))
        print('  D=M+1' )
        print('  @SP' )
        print('  M=D' )

        # THAT = *(FRAME-1)
        print('  @FRAME' )
        print('  D=M' )
        print('  @1' )
        print('  D=D-A' )
        print('  A=D' )
        print('  D=M' )
        print('  @' + str(THAT_ADDRESS))
        print('  M=D' )

        # THIS = *(FRAME-2)
        print('  @FRAME' )
        print('  D=M' )
        print('  @2' )
        print('  D=D-A' )
        print('  A=D' )
        print('  D=M' )
        print('  @' + str(THIS_ADDRESS))
        print('  M=D' )

        # ARG = *(FRAME-3)
        print('  @FRAME' )
        print('  D=M' )
        print('  @3' )
        print('  D=D-A' )
        print('  A=D' )
        print('  D=M' )
        print('  @' + str(ARG_ADDRESS))
        print('  M=D' )

        # LCL = *(FRAME-4)
        print('  @FRAME' )
        print('  D=M' )
        print('  @4' )
        print('  D=D-A' )
        print('  A=D' )
        print('  D=M' )
        print('  @' + str(LCL_ADDRESS))
        print('  M=D' )
        
        #goto RET
        print('  @RET' )
        print('  A=M' )
        print('  0;JMP' )


def translate(instruction: str, codeWriter: CodeWriter):
    print('// ' + instruction)
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
        case _ if instruction.startswith('label'):
            parsed_value = re.search(r'^label (\w+)', instruction).group(1)
            codeWriter.write_label(parsed_value)
        case _ if instruction.startswith('if-goto'):
            parsed_value = re.search(r'^if-goto (\w+)', instruction).group(1)
            codeWriter.write_if(parsed_value)
        case _ if instruction.startswith('goto'):
            parsed_value = re.search(r'^goto (\w+)', instruction).group(1)
            codeWriter.write_goto(parsed_value)
        case _ if instruction.startswith('call'):
            parsed_label = re.search(r'^call (\w+.\w+.) ', instruction).group(1)
            parsed_num_locals = int(re.search(r'^call (\w+.\w+.) (\d+)', instruction).group(2))
            codeWriter.write_call(parsed_label, parsed_num_locals)
        case _ if instruction.startswith('return'):
            codeWriter.write_return()
        case _ if instruction.startswith('function'):
            parsed_function_name = re.search(r'^function (\w+.\w+.) ', instruction).group(1)
            parsed_num_locals = int(re.search(r'^function (\w+.\w+.) (\d+)', instruction).group(2))
            codeWriter.write_function(parsed_function_name, parsed_num_locals)
        case _ if instruction.startswith('push constant'):
            parsed_value = int(re.search(r'^push constant (\d+)', instruction).group(1))
            codeWriter.write_push_constant(parsed_value)
        case _ if instruction.startswith('push local'):
            parsed_value = int(re.search(r'^push local (\d+)', instruction).group(1))
            codeWriter.write_push_from(LCL_ADDRESS, parsed_value)
        case _ if instruction.startswith('push that'):
            parsed_value = int(re.search(r'^push that (\d+)', instruction).group(1))
            codeWriter.write_push_from(THAT_ADDRESS, parsed_value)
        case _ if instruction.startswith('push this'):
            parsed_value = int(re.search(r'^push this (\d+)', instruction).group(1))
            codeWriter.write_push_from(THIS_ADDRESS, parsed_value)
        case _ if instruction.startswith('push argument'):
            parsed_value = int(re.search(r'^push argument (\d+)', instruction).group(1))
            codeWriter.write_push_from(ARG_ADDRESS, parsed_value)
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

        # push/pop temp
        case _ if instruction.startswith('push temp'):
            parsed_value = int(re.search(r'^push temp (\d+)', instruction).group(1))
            codeWriter.write_push_pointer(TEMP_ADDRESS_START + parsed_value)
        case _ if  instruction.startswith('pop temp'):
            parsed_value = int(re.search(r'^pop temp (\d+)', instruction).group(1))
            codeWriter.write_pop_pointer(TEMP_ADDRESS_START + parsed_value)

        # push/pop pointer
        case _ if instruction.startswith('pop pointer 0'):
            codeWriter.write_pop_pointer(THIS_ADDRESS)
        case _ if instruction.startswith('pop pointer 1'):
            codeWriter.write_pop_pointer(THAT_ADDRESS)
        case _ if instruction.startswith('push pointer 0'):
            codeWriter.write_push_pointer(THIS_ADDRESS)
        case _ if instruction.startswith('push pointer 1'):
            codeWriter.write_push_pointer(THAT_ADDRESS)

        # push/pop static
        case _ if instruction.startswith('push static'):
            parsed_value = int(re.search(r'^push static (\d+)', instruction).group(1))
            codeWriter.write_push_pointer(STATIC_ADDRESS_START + parsed_value)
        case _ if  instruction.startswith('pop static'):
            parsed_value = int(re.search(r'^pop static (\d+)', instruction).group(1))
            codeWriter.write_pop_pointer(STATIC_ADDRESS_START + parsed_value)
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
#codeWriter.write_init()

for line in lines:
    line_number += 1
    if '//' in line:
        line = line.split('//')[0]
    if line == '':
        continue
    line = line.strip()
    translate(line, codeWriter)

codeWriter.write_end_loop()

