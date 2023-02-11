import time
import tracemalloc
import random
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

class Wyzarzanie():
    def __init__(self,graph,T,maxIter):
        self.graph = graph
        self.T = T
        self.maxIter = maxIter
        self.iteration = 1

        self.n = len(graph)
        self.nodes = [i for i in range(self.n)]
        self.best_solution = None
        self.best_val = float("Inf")

    def initial_solution_greedy(self):

        #cur_node = random.choice(self.nodes)  # start from a random node
        cur_node = 0
        solution = [cur_node]
        free_nodes = set(self.nodes)
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
        if cur_val < self.best_val:
            self.best_val,self.best_solution = cur_val,solution

        return solution,cur_val


    def prob_accept(self,new_val):
        if self.T >0:
            return math.exp(-abs(new_val-self.best_val)/self.T)
        else:
            return 1e-8
    
    #sposob = 1 - schemat geometryczny | sposob = 2 - schemat boltzmana
    def get_alfa(self,sposob):
        a = 0.99
        b  = 0.5
        if sposob == '1':
            return a**self.iteration
        elif sposob == '2':
            return 1/(a + b*math.log(self.iteration))
        else:
            return 0.995

    def get_val(self,solution):
        val = 0
        save = 0
        for i in range(len(solution)-1):
            val += self.graph[solution[i]][solution[i+1]]
            save = i+1
        val += self.graph[solution[save]][solution[0]]
        return val

    def accept(self,new_solution):
        val = self.get_val(new_solution)
        
        if val < self.cur_val:
            self.cur_val,self.cur_solution = val,new_solution
            if val < self.best_val:
                self.best_val,self.best_solution = val,new_solution
        else:
            if random.random() <= self.prob_accept(val):
                self.cur_val,self.cur_solution = val,new_solution
        

    def sa(self,schemat,change):
        self.cur_solution,self.cur_val = self.initial_solution_greedy()

        while self.iteration < self.maxIter:
            new_sol = list(self.cur_solution)
            if change == '1':
                i = random.randint(0,self.n-1)
                l = i
                while l == i:
                    l = random.randint(0,self.n-1)
                new_sol[i],new_sol[l] = new_sol[l],new_sol[i]
            elif change == '2':
                l = random.randint(2,self.n-1)
                i = random.randint(0,self.n-1)
                new_sol[i:(i+l)] = reversed(new_sol[i:(i+l)])
            self.accept(new_sol)
            self.T*=self.get_alfa(schemat)
            self.iteration +=1

def read_ini(file_name):
    config = configparser.ConfigParser()
    config.read(file_name)
    files = [config['section_a'][i].split() for i in config['section_a']]
    outputfile = config['section_b']['outputfile']
    parameters = [i[3:7] for i in files]
    return files,outputfile,parameters

def getError(actual,expected):
    return (int(actual)-int(expected))/int(expected)*100

def messure_all(file_name,expected_value,parameters):
    matrix = read_file_matrix(file_name)
    SA = Wyzarzanie(matrix,int(parameters[0]),int(parameters[1]))
    t0 = time.time()
    tracemalloc.start()
    SA.sa(parameters[2],parameters[3])
    mem = tracemalloc.get_traced_memory()
    t1 = time.time() - t0
    tracemalloc.stop()
    error = getError(SA.best_val,expected_value)
    return file_name,SA.best_solution,SA.best_val,parameters[0],parameters[1],parameters[2],parameters[3],error,t1,mem[1]/(1024*1024)


if __name__ == "__main__":
    files,outputfile,parameters = read_ini('sa.ini')
    header = ['file','path','value','T','maxIter','schemat','wybor','error','time','memory']
    with open(outputfile,'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range (len(files)):
            for j in range(eval(files[i][1])):
                writer.writerow(messure_all(files[i][0],files[i][2],parameters[i]))
