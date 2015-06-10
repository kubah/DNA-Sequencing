import sys
import random
import re

import networkx


p_cross = 100 * 0.9
p_mutate = 100 * 0.1
p_size = 1000
it = 30  # liczba iteracji algorytmu

length = 10


def read_data():
    """
    Wczytuje dane z pliku 'filename' do listy 'lines'. Każdy oligonukleotyd jest elementem tej listy.
    """
    global lines
    with open(filename) as file:
        lines = file.read().splitlines()
    file.close()


def get_length() -> int:
    """
    Liczy długość szukanego łańcucha DNA na podstawie nazwy pliku 'filename'.
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
                g.add_edge(lineA, lineB, l - rate)  # klucze to oceny łańcuchów, wartości są puste


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
        if rates_sum + min(g[instance[-1]][v].keys()) >= b:
            break
        rates_sum += min(g[instance[-1]][v].keys())
        instance.append(v)
    return instance


def draw_population(n) -> list:
    """
    Tworzy populację początkową.
    :param n: liczba osobników w populacji.
    :return: pierwsza populacja.
    """
    population = []
    while n > 0:
        n -= 1
        instance = draw_instance()
        instance_rate = percent_rate(instance)
        population.append((instance, instance_rate))
    return population


def new_population(old_population) -> list:
    """
    Na podstawie populacji 'old_population' tworzy nową populację o takiej samej liczności.
    :param old_population: stara populacja.
    :return: nowa populacja.
    """
    population = []
    sum_rates = sum([x[1] for x in old_population])
    sorted_population = sorted(population, key=lambda x: x[1])
    accumulated_population = list(accu(sorted_population))
    n = len(accumulated_population)
    for i in range(n):
        r = random.randint(0, sum_rates)
        index = next(y[0] for x, y in enumerate(accumulated_population) if y[1] > r)
        population.append(accumulated_population[index])
    return population


def cross_operator(parent_a, parent_b) -> tuple:
    """
    Operator krzyżowania dwóch osobników w wyniku czego powstają dwa nowe.
    :param parent_a: pierwszy osobnik.
    :param parent_b: drugi osobnik.
    :return: para nowych osobników.
    """
    x, y = sorted(random.sample(range(1, length - 1), 2))
    others_a = parent_a[:x] + parent_a[y:]
    others_b = parent_b[:x] + parent_b[y:]
    child_a = parent_a[x:y]
    child_b = parent_b[x:y]
    rate_a = weight_sum(child_a)
    rate_b = weight_sum(child_b)
    while True:  # pętla dla childA
        a = random.choice(others_b)
        if a in g.successors(child_a[-1]):
            if rate_a + min(g[child_a[-1]][a].keys()) >= b:
                break
            child_a.append(a)
            rate_a += min(g[child_a[-1]][a].keys())
        if a in g.predecessors(child_a[0]):
            if rate_a + min(g[a][child_a[0]].keys()) >= b:
                break
            child_a.insert(0, a)
            rate_a += min(g[a][child_a[0]].keys())

    while True:  # pętla dla childB
        a = random.choice(others_a)
        if a in g.successors(child_b[-1]):
            if rate_b + min(g[child_b[-1]][a].keys()) >= b:
                break
            child_a.append(a)
            rate_b += min(g[child_b[-1]][a].keys())
        if a in g.predecessors(child_b[0]):
            if rate_b + min(g[a][child_b[0]].keys()) >= b:
                break
            child_a.insert(0, a)
            rate_b += min(g[a][child_b[0]].keys())
    return child_a, child_b


def crossover(old_population) -> list:
    """
    Ogólny operator krzyżowania dla całej populacji.
    :param old_population: populacja do przeprowadzenia krzyżowania.
    :return: nowa populacja wynikowa.
    """
    population = []
    for i in range(len(old_population)):
        x, y = random.sample(old_population, 2)
        p = random.randint(0, 100)
        if p < p_cross:
            z, f = cross_operator(x, y)
            population.append(z)
            population.append(f)
        else:
            population.append(x)
            population.append(y)
    return population


def percent_rate(instance) -> int:
    """
    Zwraca jakość rozwiązania wyrażoną w procentach.
    :param instance: oceniana instancja.
    :return: zwraca ocenę wyrażoną w procentach.
    """
    return 100 * rate_instance(instance) / get_length()


def weight_sum(instance) -> int:
    """
    Zwraca sumę wartości ze wszystkich łuków w drodze.
    :param instance: przetwarzana droga.
    :return: suma wartości wszystkich łuków w drodze.
    """
    w_sum = 0
    for i, j in zip(instance[:-1], instance[1:]):
        w_sum += min(g[i][j].keys())
        w_sum += length
    return w_sum


def rate_instance(instance) -> int:
    """
    Wylicza ocenę zadanej drogi w grafie.
    :param instance: lista etykiet oligonukleotydów tworzących drogę w grafie.
    :return: ocena drogi. Liczba wierzchołków należących do drogi
    lub 0 jeśli suma wag łuków jest większa niż wartość 'b'.
    """
    rates_sum = 0
    for i, j in zip(instance[:-1], instance[1:]):
        rates_sum += min(g[i][j].keys())
        rates_sum += length
    return len(instance) if rates_sum <= b else 0


def rate_population(population) -> tuple:
    """
    Zwraca ocenę populacji w formacie:
    (minimum, średnia, maksimum)
    wyrażoną w procentach.
    :param population: oceniana populacja.
    :return: (minimum, średnia, maksimum)
    """
    rates = []
    for p in population:
        rates.append(percent_rate(p))
    return min(rates), sum(rates) / len(rates), max(rates)


def accu(x):
    """
    Generuje listę par: populacja + skumulowana wartość oceny.
    :param x: populacja.
    :return: lista skumulowanych wartości.
    """
    total = 0
    for i, j in x:
        total += j
        yield i, total


def process():
    """
    Główny algorytm programu.
    """
    x = y = z = 0
    print("Start")
    for i in range(it):
        population = []
        x, y, z = rate_population(population)
        if z == 100:
            break
    print(x, y, z)
    print("Stop")


def main(arg):
    """
    Główna funkcja odpowiadająca za agregację funkcji przetwarzających.
    :param arg: nazwa pliku, z którego pobierane są dane.
    """
    global b, filename
    filename = arg
    read_data()
    b = get_length() - length
    make_graph()
    draw_instance()
    # printData()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: \"" + sys.argv[0] + " filename\"")
    else:
        main(sys.argv[1])