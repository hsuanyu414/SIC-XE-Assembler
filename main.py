import json

print("this is SIC/XE assembler")

fd = open("Fig2_5_TEST.txt", 'r', encoding='utf-8')
fd1 = open("Pass1Result.txt", 'w', encoding='utf-8')
fd2 = open("Pass2Result.txt", 'w', encoding='utf-8')

with open('./OPTAB.json', encoding="utf-8") as f :
	OPTAB = json.load(f)
	f.close()

# lines = fd.readlines()

SYMTAB = {}

def intToHexStr(number):
	hexStr = hex(number)
	hexStr = hexStr[2:]
	while(len(hexStr)<4):
		hexStr = '0'+hexStr
	return hexStr

def printline(LOCCTR, LABEL, OPCODE, OPERAND):
	loc = intToHexStr(LOCCTR)
	print(loc+'\t'+LABEL+'\t'+OPCODE+'\t'+OPERAND)

def printSYMTAB(symtab):
	print('========SYMTAB========')
	print('SYMBOL\tADDRESS\n')
	for i in symtab:
		loc = intToHexStr(symtab[i])
		print (i+'\t'+loc)
	print('======SYMTAB_END======')


def pass1(fd):
	LOCCTR = 0
	count = 0
	duplicate_symbol = 0
	label_found = 0
	EXTEND = 0
	starting_address = 0
	program_length = 0 

	print('LOC\tLABEL\tSTATEMENT\t\tOBJCODE')
	lines = fd.readlines()
	for line in lines:
		line = line.rstrip("\n")
		instruction = line.split("\t")
		if(instruction[1][0] == '.'):
			continue# If this is a comment
		if(len(instruction)==2):
			if(instruction[0] in OPTAB):
				instruction.insert(0, '')
			else:
				instruction.append('')
		instruction.insert(0, str(0))
		LABEL = instruction[1]
		OPCODE = instruction[2]
		OPERAND = instruction[3]
		if(count == 0):
			if(OPCODE == 'START'):
				LOCCTR = int(OPERAND)
				starting_address = LOCCTR
				printline(LOCCTR, LABEL, OPCODE, OPERAND)
				continue
		if(OPCODE == 'END'):
			printline(LOCCTR, LABEL, OPCODE, OPERAND)
			break
		else:#if this is not a comment line
			if(len(LABEL)!=0):#if there is a symbol in the LABEL field
				if(LABEL in SYMTAB):#if found
					print('duplicate symbol')
					return
				else:
					SYMTAB[LABEL] = LOCCTR
				#search OPTAB for OPCODE
			if(OPCODE[0] == '+'):
				OPCODE = OPCODE[1:]
				EXTEND = 1
			else:
				EXTEND = 0
			if(OPCODE in OPTAB):
				FORMAT = (OPTAB[OPCODE]['FORMAT'])
				LOCCTR += FORMAT+EXTEND
			elif(OPCODE == 'WORD'):
				LOCCTR += 3
			elif(OPCODE == 'RESW'):
				LOCCTR += 3*int(OPERAND)
			elif(OPCODE == 'RESB'):
				LOCCTR += 1*int(OPERAND)
			elif(OPCODE == 'BYTE'):
				if(OPERAND[0] == 'C'):
					LOCCTR += len(OPERAND[2:-1])
				elif(OPERAND[0] == 'X'):
					LOCCTR += len(OPERAND[2:-1])//2
			elif(OPCODE == 'BASE'):
				LOCCTR += 0
			else:
				print('invalid operation code')
				# return
		# print(SYMTAB)
		printline(LOCCTR, LABEL, OPCODE, OPERAND)
		count += 1
	printSYMTAB(SYMTAB)
	program_length = LOCCTR - starting_address
	print('program_length = '+ intToHexStr(program_length))
	return 

def pass2(lines):
	return

pass1(fd)
# print(SYMTAB)