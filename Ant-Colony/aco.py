import numpy as np
import tsplib95
import networkx
import time
import tracemalloc
import configparser
import math
import csv



def read_file_matrix(file_name):
    file = open(file_name,"r")
    dane = file.readlines()
    dane_new = []
    for i in dane:
        dane_new.append(list(map(int,i.strip().split())))
    return dane_new

class AntColony():
    def __init__(self,graph,CC,strat):
        self.graph = graph
        self.CC = CC
        self.alpha = 1
        self.beta = 4
        self.rho = 0.5
        self.n = len(graph)
        self.m = self.n
        self.tau0 = self.m/self.initial_solution_greedy()
        self.Q = 1
        self.strat = strat #1 - DAS #2 - QAS
        self.pheromones = [[self.tau0 for i in range(len(self.graph))] for j in range(len(self.graph))]

    
    def initial_solution_greedy(self):
        cur_node = 0
        solution = [cur_node]
        free_nodes = set(range(self.n))
        free_nodes.remove(cur_node)


        while free_nodes:
            min = float('Inf')
            for i in range(self.n):
                if(self.graph[cur_node][i] < min and self.graph[cur_node][i] != 0 and i in free_nodes):
                    min = self.graph[cur_node][i]
                    next_node = i
            free_nodes.remove(next_node)
            solution.append(next_node)
            cur_node = next_node


        cur_val = self.get_val(solution)

        return cur_val



    def updatePheromon(self):
        for i in range(self.n):
            for j in range(self.n):
                self.pheromones[i][j] *= self.rho
                for ant in range(self.m):
                    if self.strat ==1:       #DAS
                        self.pheromones[i][j]+=self.Q
                    elif self.strat ==2:     #QAS
                        if self.graph[i][j] != 0:
                            self.pheromones[i][j] +=self.Q/self.graph[i][j]

    def get_val(self,solution):
        val = 0
        save = 0
        for i in range(len(solution)-1):
            val += self.graph[solution[i]][solution[i+1]]
            save = i+1
        val += self.graph[solution[save]][solution[0]]
        return val




    def aco(self):
        print(self.n)
        best_solution = []
        best_val = float("inf")
        for i in range(self.CC):
            solutions = []
            for j in range(self.m): #dla każdej mrówy
                current_city = np.random.randint(self.n)
                solution = [current_city]
                unvisited_cities = set(range(self.n)) - {current_city}
                while unvisited_cities:
                    prob = [0 for z in range(self.n)]
                    for k in unvisited_cities:
                        prob[k] = (self.pheromones[current_city][k] ** self.alpha) * ((1 / self.graph[current_city][k]) ** self.beta)
                    suma = sum(prob)
                    for p in range(len(prob)):
                        prob[p]/= suma
                    next_city = np.random.choice(list(set(range(self.n))),p=prob)
                    solution.append(next_city)
                    current_city = next_city
                    unvisited_cities -= {next_city}
                val = self.get_val(solution)
                if(val<best_val):
                    best_solution = solution
                    best_val = val
                solutions.append(solution)
            if len(set(tuple(i) for i in solutions)) == 1:
                break
            self.updatePheromon()
        return best_solution,best_val


def getError(actual,expected):
    return (int(actual)-int(expected))/int(expected)*100

def messure_all(file_name,expected_value,parameters):
    problem = tsplib95.load('dane/'+file_name)
    graph=problem.get_graph()
    matrix = networkx.to_numpy_array(graph).tolist()
    aco = AntColony(matrix,int(parameters[0]),int(parameters[1]))   #CC,strat 
    t0 = time.time()
    #tracemalloc.start()
    best_solution,best_val = aco.aco()
    #mem = tracemalloc.get_traced_memory()
    t1 = time.time() - t0
    #tracemalloc.stop()
    error = getError(best_val,expected_value)
    return file_name,best_solution,best_val,parameters[0],parameters[1],error,t1

def read_ini(file_name):
    config = configparser.ConfigParser()
    config.read(file_name)
    files = [config['section_a'][i].split() for i in config['section_a']]
    #files = [['gr17.tsp', '5', '2085', '1000', '2']]
    outputfile = config['section_b']['outputfile']
    #outputfile = 'outputACO.csv'
    parameters = [i[3:5] for i in files]
    return files,outputfile,parameters


if __name__ == "__main__":

    files,outputfile,parameters = read_ini('aco.ini')
    header = ['file','path','value','CC','strat','error','time']
    with open(outputfile,'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range (len(files)):
            for j in range(eval(files[i][1])):
                writer.writerow(messure_all(files[i][0],files[i][2],parameters[i]))

    #graph = read_file_matrix("tsp_10.txt")

    #AC =  AntColony(graph,1000,1)
    #print(AC.aco())
