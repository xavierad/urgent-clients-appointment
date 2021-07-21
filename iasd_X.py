# IASD Project 20/21
# Xavier Dias e Guilherme Atanásio

import sys
import random
import math
import search
from itertools import permutations
from copy import deepcopy

'''A fazer:
() melhorar heurística
(X) xavier - comentar pmda init
(X) xavier - comentar pmda actions
(X) xavier - comentar pmda result
(X) xavier - comentar pmda goal test
(X) xavier - comentar pmda path cost
(X) xavier - comentar pmda load
() guilherme - comentar pmda save
() guilherme - comentar pmda heuristic
() guilherme - comentar pmda search
() guilherme - comentar patient init 
() guilherme - comentar state init
() comentar state hash, eq


Dúvidas:
 - ajuda na heurística
 - confirmar hash e eq
 -
'''

class PDMAProblem(search.Problem):
    """ An implementation of the class Problem. PMDAProblem is a class
    that implements the actions, result, goal_test and path_cost methods.
    As extra methods, heuristic, save, load and search are implemented for
    this problem."""    
    def __init__(self):
        """ Defines initially the initial goal state as None.
        Initial and goal states inherited are defined when load
        method is called."""
        super().__init__(None, None)
        # A dictionary where each medic code will have an efficiency. 
        self.medics = {}
        # A list with medic efficiencies, contains those values in same order as the previous dictionary.
        self.efficiencies = []
        # The solution to be assign to search method.
        self.solution = None
        self.equalEfficiencies = []

    def actions(self, state):
        """ Input: state
            Output: possible_actions
            Description: returns the all possible actions that can be executed in the given state.
            After retrieving all patients that are waiting for the current state, it's needed to check
            for those if there is any that's urgent. After getting a list of urgent patients, there is 
            four possibilities: the length of the list is higher, equal or lower than the than the number
            of medics or it's empty (no urgents). For the first one, there is no possible way to proceed
            to search, no possible action is returned. The second, we compute all permutations between the
            patients for the medic assignment and return them. In the third we compute all permutations 
            regarding that we must return those actions that contain mandatory the urgent patients. And for
            the last one we just return all possible permutations regarding the number of patients related to
            the number of medics, i.e., some 'empty's must be added to keep 'busy' the medics in gaps when the
            number of patients that are waiting is lower than the number of medics."""        

        # All patients that are still waiting
        all_patients_waiting = [code for code in state.patients.keys() if state.flags[code]]

        #calculating the combinations with the patients that are still waiting
        if len(all_patients_waiting) <= len(self.medics):
            pList = all_patients_waiting + ['empty']*(len(self.medics) - len(all_patients_waiting))
            return [tuple(pList)]

        # Getting all urgent patients
        urgent = [code for code, p in state.patients.items() if p.currWaitTime > p.maxWait - 5 and state.flags[code]]
        not_urgent = [code for code, p in state.patients.items() if p.currWaitTime <= p.maxWait - 5 and state.flags[code]]

        # When the number of waiting patients exceeds the medics: the path is not possible
        if len(urgent) > len(self.medics):
            return [] 
    
        # Now we filter the possible combinations with the urgent patients if it's not empty        
        if len(urgent) == len(self.medics):
            combinations = list(permutations(urgent))
        elif len(urgent) > 0:
            gap = len(self.medics) - len(urgent)
            combinations = []
            if gap > 1:  
                combinations_not_urgent = list(permutations(not_urgent, gap))
                for cn_urg in combinations_not_urgent:           
                    # print(combinations)             
                    combinations = combinations + list(permutations(urgent + list(cn_urg)))
            else:
                for n_urg in not_urgent:
                    combinations = combinations + list(permutations(urgent + [n_urg]))

        elif len(all_patients_waiting) > len(self.medics):
            combinations = list(permutations(all_patients_waiting, len(self.medics)))
        
        # print(self.equalEfficiencies)
        # print('\ncombinatçoes:', len(combinations))
        # print(combinations)
        if len(self.equalEfficiencies)>0:
            # print('aqui')
            possible_actions = self.removeActions(combinations)
            # print('filtrado', len(possible_actions))
        else:
            possible_actions = combinations
            # print(len(possible_actions))
            
        possible_actions = self.removeActionsPatients(possible_actions, state)
        # print('\nfiltrado', (possible_actions))

        return possible_actions

    # m1 1      ((1,2),3,4),(1,2,4,3),(3,4,1,2),(3,4,2,1),(1,3,2,4),(1,3,4,2)(1,4,3,2)(1,4,2,3)(2,3,1,4)(2,3,4,1)
    # m2 1      (1,2,3)(1,3,2)(2,1,3)(2,3,1)(3,2,1)(3,1,2)
    # m3 0.5    (1,2,3)(1,3,2)(2,3,1)()   
    # m4 0.2    (1,2,3,4) (1,2,4,3) (2,1,3,4) (2,1,4,3) (3,1,2,4) (3,1,4,2)....
                # (1,2, , ): [(3,4), (4,3)]
                # (2,3, , ): [(1,4), (4,1)]

    def removeActions(self, combinations):

        hash_list_of_combinations = []
        
        for action in combinations:
            str_of_equals = []
            str_of_not_equals = []
            for patient in action:   

                for ef in self.equalEfficiencies:  
                    
                    if action.index(patient) in ef:                        
                        str_of_equals.append(patient)
                        break                        
                    else:
                        str_of_not_equals.append(patient)
                        break
            
            str_of_equals = sorted(str_of_equals)
            hash_list_of_combinations.append(hash(tuple(str_of_equals+str_of_not_equals)))

        unique_hash_list_idx = []
        filtered_combinations = [] 
        for idx,hash_number in enumerate(hash_list_of_combinations): 
            if hash_number not in unique_hash_list_idx: 
                unique_hash_list_idx.append(hash_number) 
                filtered_combinations.append(combinations[idx])
        
        return filtered_combinations

    def removeActionsPatients(self, combinations, state):
        unique_hash_patients = []
        filtered_patients = []
        for idx, slot in enumerate(combinations):
            s = tuple([(state.patients[patient].consultTime - state.patients[patient].currConsultTime, state.patients[patient].currWaitTime) for patient in slot])
            if hash(s) not in unique_hash_patients:
                unique_hash_patients.append((hash(s)))
                filtered_patients.append(combinations[idx])
        
        # print(len(hash_list_of_combinations)==len(unique_hash_list_idx))
        # print(len(list(set(hash_list_of_combinations)) ))
        return filtered_patients
        
        # final = [] # accepted actions, the values of the same medics
        # values = []
        # aux_comb = []
        # for action in combinations:
            # for indexes in self.equalEfficiencies:
            #     values.append(tuple([action[x] for x in indexes]))

            # for indexes in self.equalEfficiencies:             
            #     for compare in final:               
            #         flag = 0                        
            #         if set(values) - set(compare[1]) == set():
            #             for idx, v in enumerate(action):
            #                 if idx not in indexes:
            #                     if compare[idx] == action[idx]:
            #                         flag += 1

            #         if flag == len(action) - len(values):
            #             break
            #         else:
            #             final.append((action, values))
            #             aux_comb.append(action)
        
        # return aux_comb


    def result(self, state, action):
        """ Inputs: state, action
            Output: new action
            Description: given state and action, return a new state that is the result of the action.
            The modifications are based on the consult time spent for each patient in the action to be
            performed and on the waiting time of all other patients that are still waiting. Action is 
            assumed to be a valid action in the state """
        
        # New state: basically a copy of whole state and then it's performed the necessary modifications.
        new_state = deepcopy(state)

        # Updating the current fields of each patients based on the current action
        for code, patient in new_state.patients.items(): 
            # For the patients in the slot (action)
            if code in action:
                # Add the consult time with the correspondent medic efficiency to the patient.
                m = action.index(code)
                patient.currConsultTime = patient.currConsultTime + (5 * self.efficiencies[m])
                # When the patient is done with consults
                if patient.consultTime <= patient.currConsultTime:
                    new_state.flags[code] = False
            # Add 5 minutes for all other still waiting patients to their waiting time.
            elif state.flags[code]:
                patient.currWaitTime = patient.currWaitTime + 5

        # action is needed to be appended in the state's schedule as result.
        new_state.schedule.append(action)
        return new_state        

    def goal_test(self, state):
        """ Input: state
            Output: True (if goal is achieved) or False (if not)
            Description: Given a state, return True if state is a goal state or False, otherwise.
            This is checked with the flags, that corresponds to the which patient is still waiting. """
        return state.flags == self.goal
    
    def path_cost(self, c, state1, action, state2):
        """ Inputs: c, state1, action, state2
            Output: path cost of state2 from start
            Description: Only state2 given will be useful, since here we will compute the path cost
            from the beggining of the search and return it. The path cost is based on the sum of the
            square of current waiting time of each patient.
            """
        # This will compute the sum of the current waiting time squared of each patient for the state2
        state2.path_cost = sum([patient.currWaitTime**2 for patient in state2.patients.values()])
        return state2.path_cost

    def load(self, f):      
        """ Input: file object f (opened)
            Ouput: None
            Description: Loads a problem from a (opened) file object f. Here we assign the initial 
            and goal states as such we retrieve all useful values from f to solve the problem."""
        
        # Some auxiliar list and dictionaries
        schedule = []
        patients = {}
        labels = {}
        flags = {}
        goal = {}

        # Beginnig of reading the file
        info = f.readlines()
        for line in info:
            string = line.split()
            if string != []:
                # Retrievement of all values correspondent to medics
                if(string[0] == 'MD'):
                    code = string[1]
                    efficiency = float(string[2])
                    self.medics[code] = efficiency
                    self.efficiencies.append(efficiency)

                # Retrievement of all values correspondent to labels   
                elif(string[0] == 'PL'):
                    labelCode = string[1]
                    maxWait = string[2]
                    consultTime = string[3]
                    labels[labelCode] = {'maxWait': maxWait, 'consultTime': consultTime} 
                                    
                # Retrievement of all values correspondent to patients
                elif (string[0] == 'P'):
                    code = string[1]
                    currTime = string[2]
                    label = string[3]
                    maxWait = labels[label]['maxWait']
                    consultTime = labels[label]['consultTime']
                    patients[code] = Patient(int(maxWait), int(consultTime), int(currTime))
                    flags[code] = True
                    goal[code] = False

        aux = []
        auxiliarEqual = []
        for x in self.efficiencies:
            if x not in aux:
                auxiliarEqual.append(tuple([i for i, ef in enumerate(self.efficiencies) if ef == x]))
            aux.append(x)
        
        for x in auxiliarEqual:
            if len(x) > 1:
                self.equalEfficiencies.append(x)

        # Assingment of the initial and goal states. Notice that goal is only a list, since we only
        # need to check the state with a list of flags.
        self.initial = State(flags, schedule, patients, 0)        
        self.goal = goal
    
    def save(self, f): 
        """ Input: f, the opened file where we are going to save the solution
            Output: None
            Description: The function that saves the solution to a file, f.
            It uses the variable 'schedule' from the self.solution state and
            writes to the file each line corresponding to each medic. """  
        
        if self.solution: #if there is a solution for the problem
            for idx, x in enumerate(self.medics):
                line = 'MD ' + x
                #go through each slot on the schedule and take the consult regarding each medic
                for consult in self.solution.state.schedule:
                    line = line + ' ' + consult[idx]
                
                line = line + '\n'
                f.write(line)

        else: #if the problem has no solution
            f.write('Infeasible!')


    def heuristic(self, node):
        """ Input: n, a node
            Output: a value that is going to be added to the path_cost
            Description: The function that helps to reduce the complexity of
            the search function. It takes in consideration an estimation of
            the number of slots that are left to fill and makes another
            estimation of the necessary waiting time for the pacients that are
            still waiting. This value will be added to the path_cost on the search algorithm.
        """  
        state = deepcopy(node.state)

        all_patients_waiting = {code:patient for code,patient in state.patients.items() if state.flags[code]}        
        wait_times = {code:0 for code in all_patients_waiting.keys()}

        n = len(self.medics)

        efficiencies_ordered = sorted(self.efficiencies, reverse=True)
        # print(efficiencies_ordered)

        if len(all_patients_waiting) <= n:
            return 0
        
        while len(all_patients_waiting) > n: 
            sortedCurrWait = sorted(all_patients_waiting.items(), key = lambda p : p[1].currWaitTime, reverse=True)
            sortedCurrConsult = sorted(sortedCurrWait[:n], key = lambda p : p[1].consultTime - p[1].currConsultTime, reverse = True)
            
            for idx, patient in enumerate(sortedCurrConsult):
                patient[1].currConsultTime += 5 * efficiencies_ordered[idx]
                # print(efficiencies_ordered[idx])

            for code, patient in sortedCurrWait[n:]:
                patient.currWaitTime += 5
                wait_times[code] += 5

            all_patients_waiting = {code:patient for code,patient in all_patients_waiting.items() if patient.consultTime > patient.currConsultTime}
        
        # print(f'{state.path_cost} + {sum([wait**2 for wait in wait_times.values()])}')
        return sum([wait**2 for wait in wait_times.values()])

        
    
    def search(self):
        """ Input: None
            Output: True if the problem has a solution | False if it doesn't
            Description: The function that implements the search problem using the
            chosen algorithm. ******************************************************COMMENT IN THE END WITH THE ALGORITHM NAME"""  
        # print('\nSearching ...')
        # self.solution = search.uniform_cost_search(self, display=True)
        # self.solution = search.greedy_best_first_graph_search(self, self.heuristic, display=True)
        self.solution = search.astar_search(self, self.heuristic, display=True)
        # self.solution = search.recursive_best_first_search(self, self.heuristic)

        #in case there is solution, return True
        if self.solution:
            print(f'\nSolution found! --> {self.solution.state.schedule}, {self.solution.state.path_cost}')
            # for code, p in self.solution.state.patients.items():
            #     print(f'PACIENTES: {code} | currWaitingTime: {p.currWaitTime}')
            return True
        
        print('\nNo solution found!')
        #if there is no solution, returns False
        return False
        


class Patient:
    """ Description: The class that saves the information of a patient.
        - 'maxWait' for the maximum waiting time for the patient.
        - 'consultTime' for the time of consult that the patient needs to have.
        - 'currWaitTime' for the time the patient already waited.
        - 'currConsultTime' for the time of consult that the patients already had. """

    def __init__(self, maxWait, consultTime, currWaitTime, currConsultTime = 0):
        """ The constructor specifies the maximum waiting time, the consult time,
        the current waiting time and the current consult time ASKKKKK XAVIER""" 
        self.maxWait = maxWait
        self.consultTime = consultTime
        self.currWaitTime = currWaitTime
        self.currConsultTime = currConsultTime        
        
class State:
    """ Description: The class that saves a state for the resolution of our problem.
        - The 'flags' is a dictionary that indicates, for each patient, their current state - 
        True if they are still waiting and False if they already had all their consult time.
        - The 'schedule' is an array of tuples that saves the schedule of the current state.
        - The 'patients' is a dictionary that saves the information regarding each patient on the 
        current state - for example, their current waiting time, etc - using the class Patient.
        - The 'path_cost' is the cost from the first state until the current state. """
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
        
        # consult_remaining_times = [p.currWaitTime for p in self.patients.values()]
        # consult_remaining_times_other = [p.currWaitTime for p in other.patients.values()]


        # if  tuple(consult_remaining_times) == tuple(consult_remaining_times_other) and isinstance(other, State):
        #     print('state equal!')
        return tuple(consult_remaining_times) == tuple(consult_remaining_times_other) and isinstance(other, State)

    def __hash__(self):
        # We use the hash value of the state
        # stored in the node instead of the node
        # object itself to quickly search a node
        # with the same state in a Hash Table
        consult_remaining_times = [(p.consultTime-p.currConsultTime) for p in self.patients.values()]
       

        return hash(tuple(consult_remaining_times))


if __name__ == "__main__":

    import time

    start_time = time.time()
    
    pmda = PDMAProblem()

    with open(sys.argv[1]) as f:
        pmda.load(f)

    solution = pmda.search()
    with open("solution.txt", "w") as f:
        pmda.save(f)
    
    print(f'\nTime of searching: {time.time() - start_time}')