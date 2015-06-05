import sys
import random
import re

import networkx


length = 10
a = "rate"


def read_data(filename):
    """
    Wczytuje dane z pliku 'filename' do listy 'lines'. Każdy oligonukelotyd jest elementem tej listy.
    :param filename: nazwa pliku który ma zostać wczytany.
    """
    global lines
    with open(filename) as file:
        lines = file.read().splitlines()
    file.close()


def get_length(filename) -> int:
    """
    Liczy długość szukanego łańcucha DNA na podstawie nazwy pliku.
    :param filename: nazwa pliku, która zostaje sparsowana.
    :return: długość szukanego łańcucha DNA.
    """
    [n] = re.findall("[0-9]{3}", filename)
    return int(n) + 9


def print_data():
    """
    Wyświetla ponumerowaną listę oligonukleotydów wczytanych wcześniej z pliku.
    """
    for x, y in enumerate(lines):
        print(x, y)


def make_graph():
    """
    Na podstawie listy 'lines' tworzy MultiDiGraph (skierowany multigraf) 'g'.
    Każdy wierzchołek to jeden oligonukleotyd etykietowany jego nazwą.
    Każdy łuk etykietowany jest liczbą oznaczającą stopień 'pokrycia' się połączonych ze sobą oligonukleotydów.
    """
    global g
    l = len(lines[0])
    g = networkx.MultiDiGraph()
    for lineA in lines:
        for lineB in lines:
            rates = rate_strings(lineA, lineB)
            for rate in rates:
                g.add_edge(lineA, lineB)
                g[lineA][lineB][a] = l - rate


def rate_strings(string1, string2) -> list:
    """
    Wylicza stopień pokrycie się dwóch oligonukleotydów.
    :param string1: Etykieta początkowego oligonukleotydu.
    :param string2: Etykieta końcowego oligonukleotydu.
    :return: stopień pokrycia się oligonukleotydów 'string1' i 'string2'.
    """
    rates = []
    for i in range(1, len(string1)):
        if string1[-i:] == string2[:i]:
            rates.append(i)
    return rates


def draw_instance() -> list:
    """
    Losuje drogę w grafie.
    Suma ocen na jej łukach jest mniejsza bądź równa niż wartość 'b'.
    :return: wylosowana droga.
    """
    instance = []
    rates_sum = 0
    first = random.choice(g.nodes())
    instance.append(first)
    while True:
        v = random.choice(g.successors(instance[-1]))
        if rates_sum + g[instance[-1]][v][a] >= b:
            break
        rates_sum += g[instance[-1]][v][a]
        instance.append(v)
    return instance


def draw_population(n) -> list:
    """
    Tworzy populację początkową.
    :param n: liczba osobników w populacji.
    :return: zwraca populację.
    """
    population = []
    while n > 0:
        n -= 1
        instance = draw_instance()
        population.append(instance)
    return population


def rate_instance(instance) -> int:
    """
    Wylicza ocenę zadanej drogi w grafie.
    :param instance: lista etykiet oligonukleotydów tworzących drogę w grafie.
    :return: ocena drogi. Liczba wierzchołków należących do drogi
    lub -1 jeśli suma wag łuków jest większa niż wartość 'b'.
    """
    rates_sum = 0
    for i, j in zip(instance[:-1], instance[1:]):
        rates_sum += g[i][j][a]
    if rates_sum > b:
        return -1
    return len(instance)


def rate_population(population, n):
    rates = []
    for p in population:
        rates.append(rate_instance(p))


def process(filename):
    """
    Główna funkcja odpowiadająca za agregację funkcji przetwarzających.
    :param filename: nazwa pliku, z którego pobierane są dane.
    """
    global b
    read_data(filename)
    b = get_length(filename) - length
    make_graph()
    draw_instance()
    # printData()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: \"" + sys.argv[0] + " filename\"")
    else:
        process(sys.argv[1])