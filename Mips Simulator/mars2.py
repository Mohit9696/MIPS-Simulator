"""
Author : Mohit Krishnamurthy
Simulation of Mars assembly code in MIPS
"""
from MIPSinstructions import *
#Loading Files 
FILE1 = open(input("Enter the File Name(eg. - binary1.txt)\n"))
FILE2 = open('instructions.txt')
INSTRUCT = []
DECODED = []
MEMORY = {}
PC = 0

#This function decodes the instruction. For example ['26', 'addiu', '001001', 'rs', 'rt', 'immediate']  is decoded to get ['26', 'addiu',  '01001', '29', '29',  '-48']
def DecodedInstruction(temp, binary):
    print("Instruction Type :", temp, "    ")
    line = temp.copy()
    global PC
    MEMORY[PC] = line.copy()
    PC= PC+4
    if 'rs' in line:
        line[line.index('rs')] = BinaryToDecimal(binary[6:11])
    if 'rt' in line:
        line[line.index('rt')] = BinaryToDecimal(binary[11:16])
    if 'rd' in line:
        line[line.index('rd')] = BinaryToDecimal(binary[16:21])
    if 'immediate' in line:
        line[line.index('immediate')] = twos_comp(int(binary[16:32],2), len(binary[16:32]))
    if 'offset' in line:
        line[line.index('offset')] =  twos_comp(int(binary[16:32],2), len(binary[16:32]))  
    if 'code' in line:
        line[line.index('code')] = BinaryToDecimal(binary[16:32])
    if 'sa' in line:
        line[line.index('sa')] = BinaryToDecimal(binary[21:26])
    if 'base' in line:
        line[line.index('base')] = BinaryToDecimal(binary[6:11])
    if 'hint' in line:
        line[line.index('hint')] = BinaryToDecimal(binary[11:16])
    if 'copfun' in line:
        line[line.index('copfun')] = BinaryToDecimal(binary[6:32])
    if 'instrindex' in line:
        line[line.index('instrindex')] = BinaryToDecimal(binary[6:32])
    if 'stype' in line:
        line[line.index('stype')] = BinaryToDecimal(binary[21:26])
    for i in range(3, len(line)):
        if not isinstance(line[i], int):
            line[i] = BinaryToDecimal(line[i])
    DECODED.append(line)
    del line

#This function is used to obtain 2's compliment
def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)        
    return val 

#This function detects which instruction is being used by decoding the mars binary file
def DetectInstruction(firstbits, lastbits, binary):
    temp = INSTRUCT.copy()
    for line in temp:
        if firstbits == line[2] and (firstbits != "000000" and firstbits != "000001"):
            DecodedInstruction(line, binary)
            break
        elif firstbits == "000000" and lastbits == line[-1]:
            DecodedInstruction(line, binary)
            break
        elif firstbits == "000001" and binary[11:16] == line[-2]:
            DecodedInstruction(line, binary)
            break
    del temp

#Converts Binary values to Decimal
def BinaryToDecimal(line):
    return int('0b' + line, 2)

#Load all the instructions from intructions.txt
for line in FILE2:
    #print(line)
    arr = list(filter(None, line.split(" ")))[:-1]
    if(arr[0] == "24"):
        arr.append("instrindex")
    INSTRUCT.append(arr)
    del arr

#Loads all the binary codes and then detects and decodes the binary to get corresponding instructions
for line in FILE1:
    print("Instruction : ", line.strip())
    firstbits = line[:6].strip()
    lastbits = line[26:].strip()
    DetectInstruction(firstbits, lastbits, line.strip())
    print("*"*70)

#Close the files
FILE1.close()
FILE2.close()

#Display the decoded instructions
print("*"*110)
for line in DECODED:
    str1 = ""
    for word in line:
        str1 = str1 + "\t" + str(word)
    print(str1)
    del str1
print("*"*110)

PREPROCESSING = {}
PC=0
for line in DECODED:
    PREPROCESSING[PC]=line
    PC=PC+4

REGS ={i:900+i for i in range(32)}
REGS[0] = 0

print("Initially")
print("Actual Memory : ",MEMORY)
#print("\nPre-processing the instructions : ",PREPROCESSING)
print("\nRegisters : ",REGS)

print("*"*110)


PC = 0
NPC = 0
A = None
B = None
IMM = None
ALUOP = None
LMD = None
IR = []

IF = []
ID = []
EX = []
MEM = []
WB = []
NCLOCK=0

BUSYREGS = [(-1,-1)]


PRINTINGIF = {}
PRINTINGID = {}
PRINTINGEX = {}
PRINTINGMEM = {}
PRINTINGWB = {}
NSTATE = None

#Populate the library with all the MIPS opcodes
library = {}
TEMPLIB = PopulateLibrary()
for val in TEMPLIB:
    library.update({val:locals()[val]})
library['and']= library.pop('AND')
print("Library :\n",library)
print("*"*110)

#The following piece of code passes the instructions through pipeline and simulates the instructions
while PC in MEMORY.keys():
    CLOCK = 0
    i=1
    STATES = []
    #Instruction Fetch Phase
    if i == 1:
        #print("\nFETCH PHASE : ")
        while True:
            if CLOCK in IF :
                CLOCK += 1
            else:
                IF.append(CLOCK)
                STATES.append(CLOCK)
                i=2
                try:
                    IR = MEMORY[PC]
                except:
                    print("Memory reference does not exist")
                    quit 
                NPC = PC + 4
                #print("PC : ",PC)
                #print("NPC : ",NPC)
                #print("Fetched Instruction : ",IR)
                STOREIR =IR
                PRINTINGIF.update({CLOCK: [PC,NPC,IR]})
                CLOCK += 1
                break
    #Instruction Decode Phase
    if i == 2:
        #print("\nDECODE PHASE")
        temp = PREPROCESSING[PC].copy()
        tempA = None
        tempB = None
        tempRD = None
        immflag=0
        bflag=0
        IMM = None
        offsetflag=0
        saflag=0
        if 'rs' in IR:
            A=REGS[temp[3]]
            tempA = temp[3]
        if 'rt' in IR:
            B=REGS[temp[4]]
            tempB = temp[4]
        if 'rd' in IR:
            #print("Destination register(rd) : ", temp[5])
            tempRD = temp[5]
        #print("A : ",A)
        #print("B : ",B)
        while True:
            if CLOCK in ID or (CLOCK,tempA) in BUSYREGS or (CLOCK,tempB) in BUSYREGS or (CLOCK,tempRD) in BUSYREGS :
                CLOCK += 1
            else:
                ID.append(CLOCK)
                STATES.append(CLOCK)
                #Block out of order instructions
                for j in range(CLOCK):
                    if j not in ID:
                        ID.append(j)
                if 'immediate' in IR:
                    IMM=temp[5]
                    immflag=1
                    #print ("IMM : ",IMM)
                #print("Decoded instruction : ",temp)
                i=3
                IR = temp
                PRINTINGID.update({CLOCK: [A,B,IMM,STOREIR,PREPROCESSING[PC].copy()]})
                CLOCK += 1
                break
    #Execute Instruction
    if i == 3:
        #print("\nEXECUTE PHASE")
        while True:
            if CLOCK in EX:
                CLOCK += 1
            else:
                EX.append(CLOCK)
                STATES.append(CLOCK)
                if tempRD != None :
                    BUSYREGS.append((CLOCK,tempRD))
                    BUSYREGS.append((CLOCK+1,tempRD))
                if immflag == 1 and tempB != None:
                    BUSYREGS.append((CLOCK,tempB))
                    BUSYREGS.append((CLOCK+1,tempB))
                if IR[1] in library:
                    if IR[0] == "01":
                        ALUOP = library[IR[1]](A,B)
                        #print("ALUOutput : ",ALUOP)
                    elif IR[0] == "02":
                        ALUOP = library[IR[1]](B,IR[6])
                        #print("ALUOutput : ",ALUOP)
                    elif IR[0] == "03":
                        pass
                    elif IR[0] == "04":
                        pass
                    elif IR[0] == "05":
                        pass
                    elif IR[0] == "06":
                        pass
                    elif IR[0] == "07":
                        pass
                    elif IR[0] == "08":
                        pass
                    elif IR[0] == "09":
                        pass
                    elif IR[0] == "10":
                        if library[IR[1]](A,IR[5]) == 1:
                            bflag = 1
                            ALUOP = NPC + (IR[5]<<2) 
                            #print("ALUOutput : ",ALUOP)
                    elif IR[0] == "11":
                        pass
                    elif IR[0] == "20":
                        ALUOP = library[IR[1]](IMM)
                        #print("ALUOutput : ",ALUOP)
                    elif IR[0] == "21":
                        pass
                    elif IR[0] == "22":
                        ALUOP = library[IR[1]](IR[5],REGS[IR[3]])
                        #print("ALUOutput : ",ALUOP)
                    elif IR[0] == "23":
                        pass
                    elif IR[0] == "24":
                        pass
                    elif IR[0] == "25":
                        pass
                    elif IR[0] == "26":
                        ALUOP = library[IR[1]](A,IMM)
                        #print("ALUOutput : ",ALUOP)
                    elif IR[0] == "27":
                        ALUOP = NPC + library[IR[1]](A,B,IR[5])
                        bflag=1
                        #print("ALUOutput : ",ALUOP)

                PRINTINGEX.update({CLOCK : [ALUOP,IR.copy()]})
                i=4
                CLOCK += 1
                break
    #Memory Phase
    if i == 4:
        #print("\nMEMORY PHASE")
        while True:
            if CLOCK in MEM:
                CLOCK += 1
            else:
                MEM.append(CLOCK)
                STATES.append(CLOCK)
                if IR[0] in ["05","10","24","25","27"] and bflag == 1:
                    NPC = ALUOP
                    #print("PC : ",NPC)
                if IR[0] in ["22"]:
                    if IR[1] == "lw":
                        LMD = MEMORY[ALUOP]
                        #print("LMD : ", LMD)
                    if IR[1] == "sw":
                        MEMORY[ALUOP] = B
                        #print("B : ",B)
                    #print("Memory : ", MEMORY)
                PRINTINGMEM.update({CLOCK : [NPC,IR.copy(),LMD,B]})
                i=5
                CLOCK += 1
                break
    #WriteBack Stage
    if i == 5:
        #print("\nWRITEBACK PHASE")
        while True:
            if CLOCK in WB:
                CLOCK += 1
            else:
                WB.append(CLOCK)
                STATES.append(CLOCK)
                if IR[1] in library:
                    if IR[0] == "01":
                        REGS[tempRD] = ALUOP
                        #print("\n Registers : ",REGS)
                    elif IR[0] == "02":
                        REGS[tempRD] = ALUOP
                        #print("\n Registers : ",REGS)
                    elif IR[0] == "03":
                        pass
                    elif IR[0] == "04":
                        pass
                    elif IR[0] == "05":
                        pass
                    elif IR[0] == "06":
                        pass
                    elif IR[0] == "07":
                        pass
                    elif IR[0] == "08":
                        pass
                    elif IR[0] == "09":
                        pass
                    elif IR[0] == "10":
                        pass
                    elif IR[0] == "11":
                        pass
                    elif IR[0] == "20":
                        REGS[tempB] = ALUOP
                        #print("\n Registers : ",REGS)
                    elif IR[0] == "21":
                        print("operation performed")
                    elif IR[0] == "22":
                        if IR[1] == "lw":
                            REGS[tempB] = LMD
                            #print("Registers : ", REGS)
                    elif IR[0] == "23":
                        pass
                    elif IR[0] == "24":
                        pass
                    elif IR[0] == "25":
                        pass
                    elif IR[0] == "26":
                        REGS[tempB] = ALUOP
                        #print("\n Registers : ",REGS)
                    elif IR[0] == "27":
                        #print("Branch")
                        pass
                PRINTINGWB.update({CLOCK : [REGS.copy(),IR.copy()]})
                i=0
                CLOCK += 1
                #print()
                #print("*"*110)
                #print("IF : {0}, ID : {1}, EX : {2}, MEM : {3}, WB : {4}".format(STATES[0],STATES[1],STATES[2],STATES[3],STATES[4]))
                #print("*"*110) 
                break
    CLOCK+=1
    NCLOCK = STATES[-1]
    NSTATE = STATES
    del STATES          
    IR.clear()
    PC=NPC
print("*"*110)
print(BUSYREGS)
print("*"*110)

PREG = None

#Displaying the values
for i in range(NCLOCK+1):
    print("In Clock ",i)
    print("Instruction Fetch ")
    if i in PRINTINGIF.keys():
        print("PC :",PRINTINGIF[i][0])
        print("NPC :",PRINTINGIF[i][1])
        print("Instruction Register :",PRINTINGIF[i][2])
    else:
        if i >= 1 and i <= NSTATE[0]:
            print("STALL")
    print("\n\nInstruction Decode :")
    if i in PRINTINGID.keys():
        print("Instruction :",PRINTINGID[i][3])
        print("Temporary Register A :",PRINTINGID[i][0])
        print("Temporary Register B :",PRINTINGID[i][1])
        print("Immediate :",PRINTINGID[i][2])
        print("Decoded Instruction :",PRINTINGID[i][4])
    else:
        if i >= 2 and i <= NSTATE[1]:
            print("STALL")
    print("\n\nExecute Stage :")
    if i in PRINTINGEX.keys():
        print("Instruction :",PRINTINGEX[i][1])
        print("ALUOutput :",PRINTINGEX[i][0])
    else:
        if i >=3 and i <= NSTATE[2]:
            print("STALL")
    print("\n\nMemory Stage :")
    if i in PRINTINGMEM.keys():
        print("Instruction :",PRINTINGMEM[i][1])
        print("NPC :",PRINTINGMEM[i][0])
        if PRINTINGMEM[i][1][1] == "lw":
            print("LMD :",PRINTINGMEM[i][2])
        if PRINTINGMEM[i][1][1] == "sw":
            print("Storing ",PRINTINGMEM[i][3]," into memory")
    else:
        if i >= 4 and i <= NSTATE[3]:
            print("STALL")
    print("\n\nWrite Back Stage :")
    if i in PRINTINGWB.keys():
        PREG = PRINTINGWB[i][0]
        print("Instruction :",PRINTINGWB[i][1])
        print("Registers :",PRINTINGWB[i][0])
    else:
        if i >= 5 and i <= NSTATE[-1] :
            print("STALL")
            print(" Registers : ",PREG)
    print("*"*110)
        

