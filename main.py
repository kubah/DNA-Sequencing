import sys
import random
import re

import networkx


olength = 10
a = "rate"


def readData(filename):
    global lines
    with open(filename) as file:
        lines = file.read().splitlines()
    file.close()


def getLength(filename) -> int:
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
    g = networkx.DiGraph()
    for lineA in lines:
        for lineB in lines:
            rates = rateStrings(lineA, lineB)
            for rate in rates:
                g.add_edge(lineA, lineB)
                g[lineA][lineB][a] = l - rate


def rateStrings(str, strx) -> list:
    rates = []
    for i in range(1, len(str)):
        if str[-i:] == strx[:i]:
            rates.append(i)
    return rates


def drawInstance() -> list:
    instance = []
    sum = 0
    first = random.choice(g.nodes())
    instance.append(first)
    while True:
        v = random.choice(g.successors(instance[-1]))
        if sum + g[instance[-1]][v][a] >= b:
            break
        sum += g[instance[-1]][v][a]
        instance.append(v)
    return instance


def drawPopulation(n) -> list:
    population = []
    while n > 0:
        n -= 1
        instance = drawInstance()
        population.append(instance)
    return population


def rateInstance(instance) -> int:
    sum = 0
    for i, j in zip(instance[:-1], instance[1:]):
        sum += g[i][j][a]
    if sum > b:
        return -1
    return len(instance)


def ratePopulation(population, n):
    rates = []
    for p in population:
        rates.append(rateInstance(p))


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