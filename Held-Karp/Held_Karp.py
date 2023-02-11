import time
import csv
import configparser
import tracemalloc
from itertools import combinations
routes = []

def read_file_matrix(file_name):
    file = open(file_name,"r")
    dane = file.readlines()
    dane_new = []
    for i in dane:
        dane_new.append(list(map(int,i.strip().split())))
    return dane_new

def read_file_list(file_name):
    file = open(file_name,"r")
    dane = file.readlines()
    dane_new = [[0 for i in range(len(dane))] for j in range(len(dane))]
    dane_help = []
    for i in dane:
        dane_help.append(list(map(int,i.strip().split())))
    index1 = 0 
    for i in dane_help:
        index2 = 0
        for j in i:
            dane_new[index1][index2] = j
            dane_new[index2][index1] = j
            index2+=1
        index1+=1
    return dane_new

def clear_bit(value, bit):
    return value & ~(1<<bit)


def held_karp(paths):

    l = len(paths)

    C = {}

    # subset reprezentowany przez aktywowanie bitów w słowie, zwiedzany wierzchołek = dystans drogi, ostatni zwiedzony wierzchołek 
    for k in range(1, l):
        C[(1 << k, k)] = (paths[0][k], 0) #reprezentujemy odwiedzone wierzchołki poprzez aktywowanie odpowiedniego bitu w incie

    # Iteruje po coraz większych subsetach
    for subset_size in range(2, l):
        for subset in combinations(range(1, l), subset_size):  #tworzy subsety o odpowiedniej wielkości
            bits = 0
            for bit in subset:
                bits |= 1 << bit #zapisuje subset w postaci bitowej

            # Znajduje najkrótszą droge do rozpatrywanego podsetu
            for k in subset:
                prev = clear_bit(bits,k)#wyczyszczenie k bitu

                res = []
                for m in subset:
                    if m == 0 or m == k:  #jeżeli sprawdzany wierzchołek jest wierzchołkiem początkowym lub tym do którego drogę próbujemy ustalić to jest pominięty
                        continue
                    res.append((C[(prev, m)][0] + paths[m][k], m))  #generuje drogę do wierzchołka k 
                C[(bits, k)] = min(res) #znajduje najkrótszą ścieżkę do tego podsetu i ją zapisuje

    bits = 2**l - 2

    res = []
    for k in range(1, l):
        res.append((C[(bits, k)][0] + paths[k][0], k))
    min_path = min(res)
    optimal = min_path[0]
    last = min_path[1]

    path = []
    for i in range(l-1):
        path.append(last)
        new_bits = clear_bit(bits,last)
        last = C[(bits, last)][1]
        bits = new_bits

    path.append(0)
    path = list(reversed(path))
    return optimal, path

def messure_time(file_name):
    data = read_file_matrix(file_name)
    t0 = time.time()
    route = held_karp(data)
    t1 = time.time() - t0
    return [route,t1]

def messure_memory(file_name):
    data = read_file_matrix(file_name)
    tracemalloc.start()
    route = held_karp(data)
    mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return mem[1]

def messure_both(file_name):
    data = read_file_matrix(file_name)
    t0 = time.time()
    tracemalloc.start()
    route = held_karp(data)
    mem = tracemalloc.get_traced_memory()
    t1 = time.time() - t0
    tracemalloc.stop()
    return [file_name,route,t1,mem[1]/(1024*1024)]

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('hp.ini')
    files = [config.get('section_a','file' + str(i)).split() for i in range(6)]
    outputFile = config.get('section_a','outputFile')
    header = ['file','value and path','time','memory']
    with open(outputFile, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range (2):
            for j in range(eval(files[i][1])):
                writer.writerow(messure_both(files[i][0]))