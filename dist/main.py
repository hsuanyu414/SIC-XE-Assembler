import json
import sys
import os

'''
OS：Windows

Used language：python

how to compile：
1. use the python interpreter
=======================
$python main.py
=======================

2. use pyinstaller to pack main.py into 
=======================
$pyinstaller -F main.py
=======================
the packed exe file will be in the dist folder
'''


current_folder = os.getcwd()

with open(current_folder+'/'+'OPTAB.json', encoding="utf-8") as f :
	OPTAB = json.load(f)
	f.close()

# lines = fd.readlines()

SYMTAB = {}
starting_address = 0
program_length = 0 
EXTEND = 0
indirect = 0
immediate = 0
index = 0

ofd = None

def intToHexStr(number):
	hexStr = hex(number)
	hexStr = hexStr[2:]
	while(len(hexStr)<6):
		hexStr = '0'+hexStr
	return hexStr

def printline(LOCCTR, LABEL, OPCODE, OPERAND):
	loc = intToHexStr(LOCCTR)
	print(loc+'\t'+LABEL+'\t'+OPCODE+'\t'+OPERAND, file=ofd)

def printSYMTAB(symtab):
	print('========SYMTAB========')
	print('SYMBOL\tADDRESS\n')
	for i in symtab:
		loc = intToHexStr(symtab[i])
		print (i+'\t'+loc, file=ofd)
	print('======SYMTAB_END======')

def is_comment(instruction):
	for i in instruction:#================================= To find the first index with content
		if(len(i)!=0):
			if(i[0] == '.'):#============================== If this is a comment
				return True
	return False

def is_blankLine(instruction):
	for i in instruction:
		if(len(i)!=0):
			return False
	return True

def in_SYMTAB(element):
	global indirect
	global immediate
	global index
	indirect = 0
	immediate = 0
	index = 0
	if(element in SYMTAB):
		return True
	elif(len(element)>= 2 and element[0] == '@' and element[1:] in SYMTAB):
		indirect = 1
		return True
	elif(len(element)>= 2 and element[0] == '#' and element[1:] in SYMTAB):
		immediate = 1
		return True
	elif(element[:-2] in SYMTAB and element[-2:] == ",X"):
		index = 1
		return True
	else:
		return False

def in_OPTAB(element):
	global EXTEND
	EXTEND = 0
	if(element in OPTAB):
		return True
	elif(len(element)>= 2 and element[0] == '+' and element[1:] in OPTAB):
		EXTEND = 1
		return True
	else:
		return False

def pass1(inputFilePath, outputFilePath):
	fd = open(current_folder+'/'+inputFilePath, 'r', encoding='utf-8')
	if(outputFilePath):
		ofd = open(current_folder+'/'+outputFilePath, 'w', encoding='utf-8')
	else:
		ofd = sys.stdout
	# opening the input file and output file's fd
	LOCCTR = 0
	last = 0
	count = 0
	duplicate_symbol = 0
	label_found = 0
	print('LOC\tLABEL\tSTATEMENT\t\tOBJCODE')
	lines = fd.readlines()
	for line in lines:
		line = line.rstrip("\n")
		instruction = line.split("\t")
		if(is_comment(instruction)):
			continue
		if(is_blankLine(instruction)):
			continue
		if(len(instruction)==1):
			if(len(instruction[0])==0):
				continue
			if(in_OPTAB(instruction[0])):
				instruction.insert(0, '')
			else:
				print('label with no definition.')
				return -1
		if(len(instruction)==2):
			if(in_OPTAB(instruction[0])):#====== If the first element is in OPTAB, append ' ' at index 0
				instruction.insert(0, '')
			else: #============================ Else (view as a label)
				instruction.append('')
		instruction.insert(0, str(0))
		LABEL = instruction[1]
		OPCODE = instruction[2]
		OPERAND = instruction[3]
		if(count == 0):
			if(OPCODE == 'START'):
				LOCCTR = int(OPERAND, 16)
				starting_address = LOCCTR
				last = LOCCTR
				printline(LOCCTR, LABEL, OPCODE, OPERAND)
				continue
		if(OPCODE == 'END'):
			printline(LOCCTR, LABEL, OPCODE, OPERAND)
			break
		else:#if this is not a comment line
			if(len(LABEL)!=0):#if there is a symbol in the LABEL field
				if(LABEL in SYMTAB):#if found
					print('duplicate symbol')
					return -1
				elif(LABEL == 'WORD' or LABEL == 'RESW' or LABEL == 'RESB' or LABEL == 'BYTE' or LABEL == 'BASE'):
					print('assembler driective as symble')
					return -1
				elif(in_OPTAB(LABEL)):
					print('opcode as label')
					return -1
				else:
					SYMTAB[LABEL] = LOCCTR
				#search OPTAB for OPCODE
			if(in_OPTAB(OPCODE)):
				if(EXTEND):
					FORMAT = (OPTAB[OPCODE[1:]]['FORMAT'])
					if(FORMAT != 3):
						print('extend format without FORMAT 3')
						return -1 
					LOCCTR += (FORMAT+1)
				else:
					FORMAT = (OPTAB[OPCODE]['FORMAT'])
					LOCCTR += FORMAT	
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
				return -1
		# print(SYMTAB)
		printline(last, LABEL, OPCODE, OPERAND)
		last = LOCCTR
		count += 1
	printSYMTAB(SYMTAB)
	global program_length
	program_length = LOCCTR - starting_address
	print('program_length = '+ intToHexStr(program_length))
	return 1

def pass2(inputFilePath, outputFilePath):
	fd = open(current_folder+'/'+inputFilePath, 'r', encoding='utf-8')
	if(outputFilePath):
		ofd = open(current_folder+'/'+outputFilePath, 'w', encoding='utf-8')
	else:
		ofd = sys.stdout
	# opening the input file and output file's fd
	LOCCTR = 0
	count = 0
	duplicate_symbol = 0
	X = 0
	t_record = "T "
	t_record_len = 0
	global program_length
	label_found = 0
	# print('LOC\tLABEL\tSTATEMENT\t\tOBJCODE')
	lines = fd.readlines()
	for line in lines:
		line = line.rstrip("\n")
		instruction = line.split("\t")
		if(is_comment(instruction)):
			continue
		if(is_blankLine(instruction)):
			continue
		if(len(instruction)==1):
			if(len(instruction[0])==0):
				continue
			if(in_OPTAB(instruction[0])):
				instruction.insert(0, '')
			else:
				print('label with no definition.')
				return
		if(len(instruction)==2):
			if(in_OPTAB(instruction[0])):#====== If the first element is in OPTAB, append ' ' at index 0
				instruction.insert(0, '')
			else: #============================ Else (view as a label)
				instruction.append('')
		instruction.insert(0, str(0))
		LABEL = instruction[1]
		OPCODE = instruction[2]
		OPERAND = instruction[3]
		if(count == 0):
			if(OPCODE == 'START'):
				LOCCTR = int(OPERAND)
				starting_address = LOCCTR
				while(len(LABEL)<6):
					LABEL = LABEL+' '
				print("H " + LABEL + ' '+ intToHexStr(LOCCTR) + ' ' +intToHexStr(program_length))
				continue
		if(OPCODE == 'END'):
			print("E " + intToHexStr(starting_address))
			break
		else:#if this is not a comment line
			#29個 byte 換
			if(in_OPTAB(OPCODE)):
				if(in_SYMTAB(OPERAND)):
					if(indirect):# @m
						continue
					elif(immediate): # #c
						print(OPCODE + "\t" +  OPERAND +  "\t" + intToHexStr(SYMTAB[OPERAND]))
					elif(index):# m,x
						continue
					else:
						print(OPCODE + "\t" +  OPERAND +  "\t" + intToHexStr(SYMTAB[OPERAND]))

	return
# you should call pass1 first to get the SYMTAB

# print(SYMTAB)

fileName = input("Please input the file name : ")
pass1(fileName, None)
# if(pass1(fileName, None)):
# 	pass2(fileName, None)

input('Press any key to continue')
