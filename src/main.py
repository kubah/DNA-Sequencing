import sys
import random
import re
import time

import networkx

p_cross = 100 * 0.9
p_mutate = 100 * 0.1
p_size = 2000
it = 20  # liczba iteracji algorytmu


def read_data():
    """
    Wczytuje dane z pliku 'filename' do listy 'lines'. Każdy oligonukleotyd jest elementem tej listy.
    """
    global lines, length
    with open(filename) as file:
        lines = file.read().splitlines()
    length = len(lines[0])
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
    g = networkx.MultiDiGraph()
    for lineA in lines:
        for lineB in lines:
            rates = rate_strings(lineA, lineB)
            # wagi o wartości 10 odpowiadające przyleganiu kolejnych oligonukleotydów
            # if lineA != lineB:
            #     g.add_edge(lineA, lineB, length)
            for rate in rates:
                g.add_edge(lineA, lineB, length - rate)  # klucze to oceny łańcuchów, wartości są puste


def rate_strings(string1, string2) -> list:
    """
    Wylicza stopień pokrycia się dwóch oligonukleotydów.
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
    rates_sum = length
    first = random.choice(g.nodes())
    instance.append(first)
    while True:
        v = random.choice(g.successors(instance[-1]))
        rates_sum += min(g[instance[-1]][v].keys())
        if rates_sum >= b:
            break
        instance.append(v)
    return instance


def draw_population(n) -> list:
    """
    Tworzy populację początkową.
    :param n: liczba osobników w populacji.
    :return: pierwsza populacja.
    """
    population = []
    for _ in range(n):
        instance = draw_instance()
        population.append(instance)
    return population


def new_population(old_population) -> list:
    """
    Na podstawie populacji 'old_population' tworzy nową populację o takiej samej liczności.
    :param old_population: stara populacja.
    :return: nowa populacja.
    """
    population = []
    sum_rates = sum([len(x) for x in old_population])
    sorted_population = sorted(old_population, key=lambda x: len(x))
    accumulated_population = list(accu(sorted_population))

    for i in range(len(accumulated_population)):
        r = random.randint(0, sum_rates-1)
        index = next(x for x, (y, z) in enumerate(accumulated_population) if z > r)
        population.append(accumulated_population[index][0])

    return population


def process_successors(rate, child, other) -> tuple:
    """
    Dodaje na końcu łańcucha child oligonukleotyd z łańcucha other.
    :param rate: aktualna ocena łańcucha.
    :param child: aktualny łańcuch dziecka.
    :param other: aktualny łańcuch pozostałych oligonukleotydów.
    :return:
    """
    for a in other:
        if a in g.successors(child[-1]):
            rate += min(g[child[-1]][a].keys())
            if rate > b:
                return rate, False
            child.append(a)
            other.remove(a)
            return rate, True

    return rate, True


def process_predecessors(rate, child, other) -> tuple:
    """
    Dodaje na początku łańcucha child oligonukleotyd z łańcucha other.
    :param rate: aktualna ocena łańcucha.
    :param child: aktualny łańcuch dziecka.
    :param other: aktualny łańcuch pozostałych oligonukleotydów.
    :return:
    """
    for a in other:
        if a in g.predecessors(child[0]):
            rate += min(g[a][child[0]].keys())
            if rate > b:
                return rate, False
            child.insert(0, a)
            other.remove(a)
            return rate, True

    return rate, True


def cross_operator(parent_a, parent_b) -> tuple:
    """
    Operator krzyżowania dwóch osobników w wyniku którego powstają dwa nowe.
    :param parent_a: pierwszy osobnik.
    :param parent_b: drugi osobnik.
    :return: para nowych osobników.
    """
    go_a = go_b = True
    x, y = sorted(random.sample(range(1, length - 1), 2))
    others_a = parent_a[:x] + parent_a[y:]
    others_b = parent_b[:x] + parent_b[y:]
    child_a = parent_a[x:y]
    child_b = parent_b[x:y]
    rate_a = weight_sum(child_a)
    rate_b = weight_sum(child_b)
    random.shuffle(others_a)
    random.shuffle(others_b)

    others_a = [x for x in others_a if x not in child_b]
    lines_a = [y for y in lines if (y not in others_a and y not in child_b)]
    others_a = others_a + lines_a

    others_b = [x for x in others_b if x not in child_a]
    lines_b = [y for y in lines if (y not in others_b and y not in child_a)]
    others_b = others_b + lines_b

    while go_a:  # pętla dla childA
        c = random.randint(0, 1)
        if c == 0:
            rate_a, go_a = process_successors(rate_a, child_a, others_a)
            rate_a, go_a = process_predecessors(rate_a, child_a, others_a)
        else:
            rate_a, go_a = process_predecessors(rate_a, child_a, others_a)
            rate_a, go_a = process_successors(rate_a, child_a, others_a)

    while go_b:  # pętla dla childB
        c = random.randint(0, 1)
        if c == 0:
            rate_b, go_b = process_successors(rate_b, child_b, others_b)
            rate_b, go_b = process_predecessors(rate_b, child_b, others_b)
        else:
            rate_b, go_b = process_predecessors(rate_b, child_b, others_b)
            rate_b, go_b = process_successors(rate_b, child_b, others_b)

    return child_a, child_b


def crossover(old_population) -> list:
    """
    Ogólny operator krzyżowania dla całej populacji.
    :param old_population: populacja do przeprowadzenia krzyżowania.
    :return: nowa populacja wynikowa.
    """
    population = []
    n = int(len(old_population)/2)
    for i in range(n):
        x, y = random.sample(old_population, 2)
        p = random.randint(0, 99)
        if p < p_cross:
            z, f = cross_operator(x, y)
            population.append(z)
            population.append(f)
        else:
            population.append(x)
            population.append(y)
    return population


def weight_sum(instance) -> int:
    """
    Zwraca sumę wartości ze wszystkich łuków w drodze.
    :param instance: przetwarzana droga.
    :return: suma wartości wszystkich łuków w drodze.
    """
    w_sum = length
    for i, j in zip(instance[:-1], instance[1:]):
        w_sum += min(g[i][j].keys())
    return w_sum


def rate_instance(instance) -> int:
    """
    Wylicza ocenę zadanej drogi w grafie.
    :param instance: lista etykiet oligonukleotydów tworzących drogę w grafie.
    :return: ocena drogi. Liczba wierzchołków należących do drogi
    lub 0 jeśli suma wag łuków jest większa niż wartość 'b'.
    """
    rates_sum = length
    for i, j in zip(instance[:-1], instance[1:]):
        rates_sum += min(g[i][j].keys())

    # print(len(instance), rates_sum, b)
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
        rates.append(rate_instance(p))
    return min(rates), sum(rates) / len(rates), max(rates)


def accu(x):
    """
    Generuje listę par: populacja + skumulowana wartość oceny.
    :param x: populacja.
    :return: lista skumulowanych wartości.
    """
    total = 0
    for i in x:
        total += len(i)
        yield i, total


def process() -> tuple:
    """
    Główny algorytm programu.
    :return:
    """
    x = y = z = 0
    print("START")
    start_time = time.time()
    p1 = draw_population(p_size)
    x, y, z = rate_population(p1)
    print("LOOP")
    for i in range(it):
        p2 = new_population(p1)
        p1 = crossover(p2)
        x, y, z = rate_population(p1)
        print("Iteration:", i, "min:", x, "avg:", y, "max:", z)

    t = time.time() - start_time
    print(t)
    print("STOP")
    return x, y, z, t


def main(arg):
    """
    Główna funkcja odpowiadająca za agregację funkcji przetwarzających.
    :param arg: nazwa pliku, z którego pobierane są dane.
    :return data: (minimum, średnia, maksimum, czas)
    """
    global b, filename
    filename = arg
    read_data()
    b = get_length() - length
    make_graph()
    data = process()
    return data


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: \"" + sys.argv[0] + " filename\"")
    else:
        main(sys.argv[1])
