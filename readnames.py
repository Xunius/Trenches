'''Read in the name list file and return a list.
'''

import random

FILE_NAME='male-names2.txt'

def readNames(filename):
    name_list=[]
    file=open(filename,'r')
    while True:
        line=file.readline().strip()
        if len(line)==0:
            break
        if line[0]=='#':
            continue
        line=line.split()
        name_list.append(line[0].capitalize())
    file.close()
    return name_list

name_list=readNames(FILE_NAME)

def pickRandom():
    return name_list[random.randint(0,len(name_list)-1)]











