#TYPE 1*


def add(rs,rt):
    return rs+rt

def slt(rs,rt):
    if rs<rt :
        return 1
    else:
        return 0

def addu(rs,rt):
    return rs+rt

def AND(rs,rt):
    return rs&rt

def dadd(rs,rt):
    return rs+rt

def daddu(rs,rt):
    return rs+rt

def movz(rs,rt):
    if(rt == 0):
        return rs

#TYPE 2*
def sll(rt,sa):
    return rt<<sa

#TYPE 3

#TYPE 4

#TYPE 5*

#TYPE 6*

#TYPE 7

#TYPE 8

#TYPE 9

#TYPE 10*
def bgez(rs,offset):
    if(rs>=0):
        return 1;
    else:
        return 0;
#TYPE 11

#TYPE 20*
def lui(imm):
    return imm<<16

#TYPE 21

#TYPE 22
def lw(offset,base):
    return offset+base

def sw(offset,base):
    return offset+base
#TYPE 23

#TYPE 24*

#TYPE 25*

#TYPE 26*
def addiu(rs,imm):
    return rs+imm

def ori(rs,imm):
    return rs|imm

def addi(rs,imm):
    return rs+imm

def daddi(rs,imm):
    return rs+imm

def daddiu(rs,imm):
    return rs+imm

#TYPE 27*
def bne(rs,rt,offset):
    if(rs != rt):
        return offset<<2
    return 0

def beq(rs,rt,offset):
    if(rs == rt):
        return offset<<2
    return 0

#Fill the Library of calling programs 
l = []
for key, value in locals().copy().items():
    if callable(value) and value.__module__ == __name__:
        l.append(key)

def PopulateLibrary():
    return l

