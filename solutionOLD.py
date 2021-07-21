# IASD Project 20/21
# Xavier Dias e Guilherme Atanásio

import sys
import random
import math
import search
from itertools import permutations
from copy import deepcopy

'''
Dúvidas:
 - tipo de heurísticas?
 - 
'''

class PDMAProblem(search.Problem):
    """ An implementation of the class Problem. PMDAProblem is a class
    that implements the actions, result, goal_test and path_cost methods."""
    
    def __init__(self, initial=None, goal=None):
        """ Define goal state and initializes a problem. """
        super().__init__(initial, goal)
        self.medics = {}
        self.efficiencies = []
        self.solution = None


    def actions(self, state):
        """ Return the actions that can be executed in the given state. """        
        possible_actions = []

        # start_time = time.time()
        # All patients that are still waiting
        all_patients_waiting = [code for code in state.patients.keys() if state.flags[code]]

        # Retrieving urgent patients
        urgent = [code for code, p in state.patients.items() if ((p.currWaitTime > p.maxWait-5) and (state.flags[code]))]

        # print('\nschedule', state.schedule)
        # When the number of waiting patients exceeds the medics: the path is not possible
        if len(urgent) > len(self.medics):
            # print('not possible')
            return [] 
        
        elif urgent != []:  
            # Gap to be filled by not urgent patients
            gap = len(self.medics) - len(urgent)

            # When the number of urgent patients is equal to the number of medics (i.e. gap=0),
            # then return the combinations between urgent patients
            # print('urgent', urgent)
            if not gap:                
                possible_actions = list(permutations(urgent, len(self.medics)))
                # print('no gap, urg combs:',possible_actions)
            else:
                # We make the difference between all waiting patients and the urgent ones, that is we get not urgent patients
                # regarding the number of waiting patients
                if len(all_patients_waiting) >= len(self.medics):
                    not_urgent = list(set(all_patients_waiting) - set(urgent))                    
                else:
                    pList = all_patients_waiting + ['empty']*(len(self.medics) - len(all_patients_waiting))
                    not_urgent = list(set(pList) - set(urgent))

                # print('not urgent', not_urgent)

                # The difference computed is then to get all possible combinations with not urgent (in difference) 
                # and urgent patients regarding that an action must have the urgents 
                combinations = []
                if gap > 1:  
                    combinations_not_urgent = list(permutations(not_urgent, gap))
                    for cn_urg in combinations_not_urgent:                        
                        combinations = combinations + list(permutations(urgent + list(cn_urg), len(self.medics)))
                else:
                    for n_urg in not_urgent:
                        combinations = combinations + list(permutations(urgent + [n_urg], len(self.medics)))
                possible_actions =  combinations
                # print('gap, not urg and urg combs', possible_actions)

        else:
            # Since there is no urgent patients, just return all possible combinations regarding the number of waiting patients
            if len(all_patients_waiting) >= len(self.medics):
                possible_actions = list(permutations(all_patients_waiting, len(self.medics)))
            else:
                pList = all_patients_waiting + ['empty']*(len(self.medics) - len(all_patients_waiting))
                possible_actions = list(permutations(pList, len(self.medics)))

            # print('no urg', possible_actions)
        
        # with open("Xcombinations.txt", "a") as f:
        #     line = 'X - combinations ' + str(len(possible_actions)) + ' ' +  str(time.time() - start_time) + '\n'
        #     f.write(line)
        # print(len(possible_actions))
        return possible_actions
        # #------------------------------------------------------------------------------------------
        # start_time = time.time()
        # # All patients that are still waiting
        # all_patients_waiting = [code for code in state.patients.keys() if state.flags[code]]

        # #calculating the combinations with the patients that are still wainting
        # if len(all_patients_waiting) >= len(self.medics):
        #     combinations = list(permutations(all_patients_waiting, len(self.medics)))
        # else:
        #     pList = all_patients_waiting + ['empty']*(len(self.medics) - len(all_patients_waiting))
        #     combinations = list(permutations(pList, len(self.medics)))

        # # Getting all urgent patients
        # urgent = [code for code, p in state.patients.items() if p.currWaitTime > p.maxWait - 5 and state.flags[code]]
        
        # # When the number of waiting patients exceeds the medics: the path is not possible
        # if len(urgent) > len(self.medics):
        #     return [] 
    
        # # Now we filter the possible combinations with the urgent patients if it's not empty
        # if urgent != []:  
        #     if len(urgent) == len(self.medics):
        #         combinations = list(permutations(urgent, len(self.medics)))
        #     else:
        #         auxList = []
        #         for c in combinations:
        #             i = 0 #number of urgent patients in the current c
        #             for patient in c:
        #                 if patient in urgent:
        #                     i = i + 1

        #             if i == len(urgent):
        #                 auxList.append(c)

        #         combinations = auxList

        # # print(f'schedule: {state.schedule} | flags: {state.flags} | combinations: {combinations}')
        # # for code, p in state.patients.items():
        # #     print(f'PACIENTES: {code} | currWaitingTime: {p.currWaitTime}')
            
        
        # possible_actions = combinations
        # # with open("Gcombinations.txt", "a") as f:
        # #    line = 'G - combinations ' + str(len(possible_actions)) + ' ' + str(time.time() - start_time) + '\n'
        # #    f.write(line)
        
        # return possible_actions


    def result(self, state, action):
        """ Given state and action, return a new state that is the result of the action.
        Action is assumed to be a valid action in the state """
        
        # New state        
        new_state = deepcopy(state)
        # new_patients = {}
        # for code, p in state.patients.items():
        #     new_patients[code] = Patient(p.maxWait, p.consultTime, p.currWaitTime, p.currConsultTime)
        # new_schedule = state.schedule.copy()
        # new_flags = state.flags.copy()

        # new_state = State(new_flags, new_schedule, new_patients, state.path_cost)



        # Updating the current fields of each patients based on the current action
        for code, patient in new_state.patients.items(): 
            if code in action:
                m = action.index(code)
                patient.currConsultTime = patient.currConsultTime + (5 * self.efficiencies[m])
                if patient.consultTime <= patient.currConsultTime:
                    new_state.flags[code] = False
            elif state.flags[code]:
                patient.currWaitTime = patient.currWaitTime + 5

        new_state.schedule.append(action)
        return new_state
        

    def goal_test(self, state):
        """ Given a state, return True if state is a goal state or False, otherwise """
        return state.flags == self.goal

    
    def path_cost(self, c, state1, action, state2):
        # This will compute the sum of the current waiting time squared of each patient for the state2
        state2.path_cost = sum([patient.currWaitTime**2 for patient in state2.patients.values()])
        
        # if state2.flags == self.goal:
        #     print(f'Result: {state2.schedule} {state2.flags.values()} f=({state2.path_cost}) --> Goal')
        # else:
        #     print(f'Result: {state2.schedule} {state2.flags.values()} f=({state2.path_cost})')

        return state2.path_cost

    def load(self, f):      
        """Loads a problem from a (opened) file object f.
        Input: A opened file object f.
        Output: Undefined"""
        
        schedule = []
        patients = {}
        labels = {}
        flags = {}
        goal = {}
        info = f.readlines()
        for line in info:
            string = line.split()
            if string != []:
                if(string[0] == 'MD'):
                    code = string[1]
                    efficiency = float(string[2])
                    self.medics[code] = efficiency
                    self.efficiencies.append(efficiency)
                                    
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
                    patients[code] = Patient(int(maxWait), int(consultTime), int(currTime))
                    flags[code] = True
                    goal[code] = False
    
        self.initial = State(flags, schedule, patients, 0)        
        self.goal = goal
      
    
    
    def save(self, f): 
        """ Saves a solution state S to a (opened) file object f"""
        
        if self.solution:
            for idx, x in enumerate(self.medics):
                line = 'MD ' + x
                for consult in self.solution.state.schedule:
                    line = line + ' ' + consult[idx]
                
                line = line + '\n'
                f.write(line)
        else:
            f.write('Infeasible!')


    def heuristic(self, node):

        nflags = list(n.state.flags.values()).count(True)





        # nmedics = len(self.medics)
        # nflags = list(n.state.flags.values()).count(True)
        
        # slots = 0
        # for code, p in n.state.patients.items():
        #     if n.state.flags[code]:
        #         slots += p.consultTime - p.currConsultTime
            

        # h = 0
        # for slot in range(round(slots/5)):
        #     if nflags - nmedics >= 0:
        #         h += sum([(5*(slot+1)) ** 2] * nmedics)
        #     else: 
        #         h += sum([(5*(slot+1)) ** 2] * nflags) 

        #     nflags -= nmedics
            

        # print(f'nflags: {nflags_for_print} h: {h} ')
        return h

        # return sum([5**2] * list(n.state.flags.values()).count(True))
        # return list(n.state.flags.values()).count(True)

    
    def search(self):
        # print('\nSearching ...')
        # self.solution = search.uniform_cost_search(self, display=True)
        # self.solution = search.greedy_best_first_graph_search(self, self.heuristic, display=True)
        self.solution = search.astar_search(self, self.heuristic)
        # self.solution = search.recursive_best_first_search(self, self.heuristic)

        if self.solution:
            # print(f'\nSolution found! --> {self.solution.state.schedule}, {self.solution.state.path_cost}')
            # for code, p in self.solution.state.patients.items():
            #     print(f'PACIENTES: {code} | currWaitingTime: {p.currWaitTime}')
            return True
        
        # print('\nNo solution found!')
        return False
        


class Patient:
    """ A patient class that stores data regarding a patient."""
    def __init__(self, maxWait, consultTime, currWaitTime, currConsultTime = 0):
        """ The constructor specifies the code, the maximum waiting time, the consult time,
        the current waiting time and possibly a flag that tells if the patient has spent at
        least consultTime in consult(s)."""
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
        
        consult_remaining_times = [(p.consultTime-p.currConsultTime) for p in self.patients.values()]
        
        consult_remaining_times_other = [(p.consultTime-p.currConsultTime) for p in other.patients.values()]
        
        # if  tuple(consult_remaining_times) == tuple(consult_remaining_times_other) and isinstance(other, State):
        #     print('state equal!')
        return tuple(consult_remaining_times) == tuple(consult_remaining_times_other) and self.path_cost == other.path_cost and isinstance(other, State)

    def __hash__(self):
        # We use the hash value of the state
        # stored in the node instead of the node
        # object itself to quickly search a node
        # with the same state in a Hash Table
        consult_remaining_times = [(p.consultTime-p.currConsultTime) for p in self.patients.values()]
        return hash(tuple(consult_remaining_times))

    def hash_code(self):
        number = [0]
        for x in self.schedule:
            for y in x:
                number.append(y)
        return "".join(map(str, number)) 

