import time
import csv
import configparser

routes = []

def read_file(file_name):
    dane_new = []
    my_dict = {}
    file = open(file_name,"r")
    dane = file.readlines()
    for i in dane:
        dane_new.append(i.strip().split())
    nums = [str(a) for a in range(len(dane))]
    for i in dane_new:
        i = [eval(j) for j in i]
        my_dict[str(i.index(0))] = dict(zip(nums, i))
    for i in my_dict:
        my_dict[i] = {key:val for key, val in my_dict[i].items() if val > 0}
    return my_dict

# funkcja rekurencyjnie sprawdzająca wszystkie permutacje połączeń wierzchołków
# w - obecnie rozważany wieszchołek, points - wszystkie drogi pomiędzy wierzchołkami, path - obecnie wyznaczana droga, dist - długość drogi
def find_paths(w, points, path, dist):

    # Dodaje wierzchołek do obecnie sprawdzanej drogi
    path.append(w)

    # Oblicza długość drogi od obecnego do ostatnio dodanego wierzchołka czyli przedostatniego w drodze
    if len(path) > 1:
        dist += points[path[-2]][w]

    # Jeżeli ścieżka zawiera wszystkie punkty oraz 
    # jest możliwość powrotu do punktu początkowego to
    # to zamyka ścieżkę łącząc ją z początkiem
    if (len(path) == len(points)) and (path[0] in points[path[-1]]):
        path.append(path[0])
        dist += points[path[-2]][path[0]]
        #print (path, dist)
        global routes
        routes.append([dist, path])
        return

    # Sprawdza wszystkie możliwe jeszcze nie sprawdzone permutacje
    for point in points:
        if (point not in path) and (w in points[point]):
            find_paths(point, dict(points), list(path), dist)

def messure_time(file_name):
    data = read_file(file_name)
    t0 = time.time()
    find_paths('0',data,[],0)
    t1 = time.time() - t0
    routes.sort()
    return [file_name,t1,routes[0][0],routes[0][1]]


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('bf.ini')
    files = [config.get('section_a','file' + str(i)).split() for i in range(6)]
    outputFile = config.get('section_a','outputFile')
    header = ['file', 'time', 'value', 'path']
    with open(outputFile, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range (2):
            for j in range(eval(files[i][1])):
                writer.writerow(messure_time(files[i][0]))
