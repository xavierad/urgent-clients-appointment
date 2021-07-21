# IASD Project 20/21
# Xavier Dias e Guilherme Atanásio

''' 

Goal: todos os pacientes com flag=False
Action:
Result:
Path Cost:

    A FAZER:

( ) - Documentação das classes, métodos e funções (objetivo(s), input, output)

    Dúvidas:
( ) - Documentação dos métodos, que formato? texto corrido (com objetivo, input e output) ou por pontos?
'''

import sys
import random
import math
from search import *
from itertools import permutations
from copy import deepcopy

class PMDAProblem(Problem):
    """ An implementation of the class Problem. PMDAProblem is a class
    that implements the actions, result, goal_test and path_cost methods."""
    #alterar goal
    def __init__(self, initial=None, goal=None):
        """ Define goal state and initializes a problem. """
        super().__init__(initial, goal)
        self.medics = []


    def actions(self, state):
        """ Return the actions that can be executed in the given state. """

        urgent = [] #list of patients that can't wait any longer
        n = 0 #number of waiting patients
        for f in state.flags:
            if f: 
                n = n + 1

        #calculating the combinations with the patients that are still wainting
        combinations = list(permutations([p.code for p in state.patients if state.flags[p.code - 1]], min(len(self.medics),n)))

        #urgent patients:
        for p in state.patients:
            if p.currWaitTime > p.maxWait - 5 and state.flags[p.code-1]:
                urgent.append(p.code)
        
        if len(urgent) > len(self.medics):
            return [] #not possible because the number of waiting patients exceeds the medics
 
    
        #Now we filter the possible combinations with the urgent patients
        if urgent != []:  
            if len(urgent) == len(self.medics):
                auxList = list(permutations(urgent, len(self.medics)))
            else:
                auxList = []
                for c in combinations:
                    i = 0 #number of urgent patients in the current c
                    for patient in c:
                        if patient in urgent:
                            i = i + 1

                    if i == len(urgent):
                        auxList.append(c)
                
            combinations = auxList

        # print(f'schedule: {state.schedule} | path_cost {state.path_cost} | flags: {state.flags} | combinations: {combinations}')
        possible_actions = combinations

        return possible_actions


    def result(self, state, action):
        """ Given state and action, return a new state that is the result of the action.
        Action is assumed to be a valid action in the state """

        # New state
        new_state = deepcopy(state)

        # Updating the current fields of each patients based on the current action
        for patient in new_state.patients:
            if patient.code in action:
                patient.currConsultTime = patient.currConsultTime + (5*self.medics[action.index(patient.code)].efficiency)
                if patient.consultTime <= patient.currConsultTime:
                    new_state.flags[patient.code - 1] = False
            else:
                patient.currWaitTime = patient.currWaitTime + 5

        new_state.schedule.append(action)
       
        return new_state
        

    def goal_test(self, state):
        """ Given a state, return True if state is a goal state or False, otherwise """
        if state.flags == self.goal.flags:
            return True

        return False

    
    def path_cost(self, c, state1, action, state2):
        # This list contains the current waiting time of each patient for the state2
        state2.path_cost = sum([patient.currWaitTime**2 for patient in state2.patients])
        
        if state2.flags == self.goal.flags:
            print(f'Result: {state2.schedule} {state2.flags} {state2.path_cost} --> Goal')
        else:
            print(f'Result: {state2.schedule} {state2.flags} {state2.path_cost}')

        return state2.path_cost

    def load(self, f):      
        """Loads a problem from a (opened) file object f.
        Input: A opened file object f.
        Output: Undefined"""
        
        schedule = []
        patients = []
        labels = {}
        info = f.readlines()
        for line in info:
            string = line.split()
            if string != []:
                if(string[0] == 'MD'):
                    code = string[1]
                    efficiency = float(string[2])
                    self.medics.append(Medic(int(code), efficiency))
                                    
                elif(string[0] == 'PL'):
                    labelCode = string[1]
                    maxWait = string[2]
                    consultTime = string[3]
                    labels[labelCode] = {'maxWait': maxWait, 'consultTime': consultTime} 
                                    
                elif (string[0] == 'P'):
                    code = string[1]
                    currTime = string[2]
                    label = string[3]
                    maxWait = labels[label]['maxWait']
                    consultTime = labels[label]['consultTime']
                    patients.append(Patient(int(code), int(maxWait), int(consultTime), int(currTime)))
    
        self.initial = State([True]*len(patients), schedule, patients, sum([patient.currWaitTime**2 for patient in patients]))
        self.goal = State([False]*len(patients), None, None, None)
      
    
    
    def save(self, f, s): 
        """ Saves a solution state S to a (opened) file object f"""
        
        for x in range(len(self.medics)):
            line = 'MD ' + str(x+1).zfill(4)
            for consult in s.schedule:
                if x < len(consult):
                    line = line + ' ' + str(consult[x]).zfill(3)
                else:
                    line = line + ' empty'
            
            line = line + '\n'
            f.write(line)
        
        pass
    
    def search(self):
        print('\nSearching ...')
        solution = uniform_cost_search(self, display=True)
        
        if solution:
            print(f'\nSolution found! --> {solution.state.schedule}, {solution.state.path_cost}')
            with open("solution.txt", "w") as f:
                self.save(f, solution.state)
            return True
        
        print('\nNo solution found!')
        return False
        

class Medic:
    """ A medic class that stores data regarding a medic."""
    def __init__(self, code, efficiency):
        """The constructor specifies the code and the efficiency of the medic."""
        self.code = code 
        self.efficiency = efficiency

class Patient:
    """ A patient class that stores data regarding a patient."""
    def __init__(self, code, maxWait, consultTime, currWaitTime, flag = True, currConsultTime = 0):
        """ The constructor specifies the code, the maximum waiting time, the consult time,
        the current waiting time and possibly a flag that tells if the patient has spent at
        least consultTime in consult(s)."""
        self.code = code
        self.maxWait = maxWait
        self.consultTime = consultTime
        self.currWaitTime = currWaitTime
        self.currConsultTime = currConsultTime        
        
class State:
    def __init__(self, flags, schedule, patients, path_cost):
        self.flags = flags
        self.schedule = schedule
        self.patients = patients
        self.path_cost = path_cost

    # def __repr__(self):
    #     return "<Node {}>".format(self.state)

    def __lt__(self, other):
        return self.path_cost < other.path_cost

    def __eq__(self, other):
        return self.schedule == other.schedule

    def __hash__(self):
        # We use the hash value of the state
        # stored in the node instead of the node
        # object itself to quickly search a node
        # with the same state in a Hash Table
        return hash(self.hash_code())

    def hash_code(self):
        number = [0]
        for x in self.schedule:
            for y in x:
                number.append(y)

        return int("".join(map(str, number))) 

if __name__ == "__main__":

    import time

    start_time = time.time()
    
    pmda = PMDAProblem()

    with open(sys.argv[1]) as f:
        pmda.load(f)

    solution = pmda.search()
    
    print(f'\nTime of searching: {time.time() - start_time}')