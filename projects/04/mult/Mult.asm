// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.
	@2
	M=0
	@0
	D=M
	@END
	D;JLE //Goto END
(LOOP)
	@R0
	MD=M-1
	@1
	D=M
	@2
	M=D+M
	@0
	D=M
	@END
	D;JLE //Goto END
	@LOOP
	0;JMP // Goto LOOP
(END)
	@END
	0;JMP // Infinite loop
