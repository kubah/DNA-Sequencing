import sys
import random
import re

import networkx


olength = 10

def readData(filename):
    global lines
    with open(filename) as file:
        lines = file.read().splitlines()
    file.close()

def getLength(filename):
    [n] = re.findall("[0-9]{3}", filename)
    n = int(n)
    n += 9
    return n

def printData():
    for x, y in enumerate(lines):
        print(x, y)

def makeGraph():
    global g
    l = len(lines[0])
    g = networkx.MultiDiGraph()
    for lineA in lines:
        for lineB in lines:
            rates = rateStrings(lineA, lineB)
            for rate in rates:
                g.add_edge(lineA, lineB, l - rate)

def rateStrings(str, strx):
    rates = []
    for i in range(1, len(str)):
        if str[-i:] == strx[:i]:
            rates.append(i)
    return rates

def drawInstance():
    instance = []
    first = random.choice(g.nodes())
    instance.append(first)
    while True:
        v = random.choice(g.successors(instance[-1]))
        if v in instance:
            continue
        if b >= len(v): # Głupoty do zmiany!!!
            break

def process(filename):
    global b
    readData(filename)
    b = getLength(filename) - olength
    makeGraph()
    drawInstance()
    # printData()

if __name__=="__main__":
    if len(sys.argv) <= 1:
        print("Usage: \"" + sys.argv[0] + " filename\"")
    else:
        process(sys.argv[1])