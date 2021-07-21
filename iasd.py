# IASD Project 20/21
# Guilherme Atanásio (87013) e Xavier Dias (87136) 

import sys
import random
import math
import search
from itertools import permutations
from copy import deepcopy


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
        # A list of tuples (maybe empty) where each tuple contains indexes of efficiencies that are equal.
        self.equalEfficiencies = []
        # The solution to be assign to search method.
        self.solution = None
        

    def actions(self, state):
        """ Input: state
            Output: possible_actions, a list of tuples (each tuple represents an action)
            Description: returns all possible actions that can be executed in the given state.
            After retrieving all patients that are waiting for the current state, it's necessary to check
            first if the number of those patients is equal or lower than the number of medics. If so, 
            then it's just necessary to return only and only one action for those patients, since the order
            does not matter (no one will be harmed in waiting time) and, if needed, with some 'empty's to
            fill the possible gap. Otherwise, it's needed to divide the list of all patients that are 
            waiting in urgent and not urgent ones. There are four possibilities for the urgent list:  
            or the length of the list is higher, equal or lower than the than the number of medics. 
            If its empty, we just use all the patients to compute the permutations. For the second one, we 
            just return an empty list since there is no more possible ways to proceed in search. For the third 
            one, we compute all permutations between the patients for the medic assignment and return them. 
            In the forth, we return those actions that contain all the mandatory 
            the urgent patients. And for the last one we just return all possible permutations regarding the 
            number of patients related to the number of medics, i.e., some 'empty's must be added to keep 
            'busy' the medics in gaps when the number of patients that are waiting is lower than the number 
            of medics."""      

        # All patients that are still waiting
        all_patients_waiting = [code for code in state.patients.keys() if state.flags[code]]

        # If the number of patients that are waiting is not higher than the number of medics then the 
        # action is simple: it's only a list of the patients with possible 'empty's
        if len(all_patients_waiting) <= len(self.medics):
            pList = all_patients_waiting + ['empty']*(len(self.medics) - len(all_patients_waiting))
            return [tuple(pList)]

        # Getting all urgent and not urgent patients lists 
        urgent = [code for code, p in state.patients.items() if p.currWaitTime > p.maxWait - 5 and state.flags[code]]
        not_urgent = [code for code, p in state.patients.items() if p.currWaitTime <= p.maxWait - 5 and state.flags[code]]

        # When the number of waiting patients exceeds the medics: the path is not possible
        if len(urgent) > len(self.medics):
            return [] 
    
        # If the number of urgent patients is equal to the number of medics then the it's necessary
        # to compute the permutations  of those urgents.
        if len(urgent) == len(self.medics):
            permutationsList = list(permutations(urgent))
        # Otherwise, and if it's not empty, then it's necessary to compute all permutations for those 
        # mandatory urgent patients with not urgent ones. 
        elif len(urgent) > 0:
            # gap is the space left by the urgent patients and must be filled by not urgents (if any).
            gap = len(self.medics) - len(urgent)
            permutationsList = []
            # If the gap is higher than 1, then we compute permutations of size 'gap' between not urgents.
            # Otherwise, then the vacancies must be filled by only one not urgent patient and we compute 
            # possible permutations between urgents and one not urgent. 
            if gap > 1:  
                permutations_not_urgent = list(permutations(not_urgent, gap))
                for cn_urg in permutations_not_urgent:        
                    permutationsList = permutationsList + list(permutations(urgent + list(cn_urg)))
            else:
                for n_urg in not_urgent:
                    permutationsList = permutationsList + list(permutations(urgent + [n_urg]))
        # When the number of all patients that are waiting is higher than the number of medics, then 
        # we face the worse case: return all possible permutations.
        elif len(all_patients_waiting) > len(self.medics):
            permutationsList = list(permutations(all_patients_waiting, len(self.medics)))
        
        # If in the current problem there are some medics with some efficiencies, we can remove some
        # actions treating those medics as the same medic: done by removeActions method.
        if len(self.equalEfficiencies) > 0:
            possible_actions = self.removeActions(permutationsList)
        else:
            possible_actions = permutationsList
            
        # In order to filter deeper the possible actions if in the current state there are some
        # patients with same current waiting time and current consult time: done by removeActionsPatients method.
        possible_actions = self.removeActionsPatients(possible_actions, state)

        return possible_actions


    def removeActions(self, possible_actions):
        """ Input: Permutations list
            Output: filtered possible_actions
            Description: We filter the computed permutations based on the fact that
            changing the order of the patients of medics that have the same efficiency is useless
            and should be counted only once as a possible action."""  
        
        unique_hash_list_idx = []  #hashcodes of the chosen actions for the final list
        filtered_permutations = [] #final list of actions

        for idx, action in enumerate(possible_actions):
            equals = []
            not_equals = []
            for patient in action:   
                for ef in self.equalEfficiencies:
                    #in case the current patient belongs to a medic that has its efficiency equal to any another medics  
                    if action.index(patient) in ef:                        
                        equals.append(patient) #we append it to the "equals" list
                        break                        
                    else:
                        not_equals.append(patient) #otherwise we append it to the "not_equal" list
                        break
            
            #we sort the list of equals, so that we can compare it to other actions with the same patients on the medics with same efficiencies
            equals = sorted(equals) 
            hash_number = hash(tuple(equals+not_equals)) #the hashcode based on the list of tuples
            if hash_number not in unique_hash_list_idx: 
                #if the current hash number is not yet on the list of unique, then we append the action and the hashcode
                unique_hash_list_idx.append(hash_number) 
                filtered_permutations.append(possible_actions[idx])
        
        return filtered_permutations


    def removeActionsPatients(self, possible_actions, state):
        """ Input: Permutations
        Output: filtered possible_actions
        Description: We filter the computed actions based on the fact that
        patients with the same consult time left and current waiting time will result
        in equivalent actions and therefore should only be counted once."""  
        
        unique_hash_patients = [] #hash list of unique patients in the actions
        filtered_patients = []    #list of filtered actions
        for idx, slot in enumerate(possible_actions):
            s = tuple([(state.patients[patient].consultTime - state.patients[patient].currConsultTime, state.patients[patient].currWaitTime) for patient in slot])
            #the hashcode for each action is a tuple that contains tuples of the consult time left and current waiting time for each patient of the action
            #if for two actions, their hash is the same, that is, the consult time left and current waiting time is equal in every position, we count only one
            if hash(s) not in unique_hash_patients:
                unique_hash_patients.append((hash(s)))
                filtered_patients.append(possible_actions[idx])
        return filtered_patients


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

        # A list of tuples where each tuple contains the indexes of the list of medics that have the same efficiency
        # which will be used to filter actions 
        ef = []
        efEqual = []
        for x in self.efficiencies:
            if x not in ef:
                efEqual.append(tuple([idx for idx, efficiency in enumerate(self.efficiencies) if efficiency == x]))
            ef.append(x)
        
        # Take only the tuples that have more than one element
        for x in efEqual:
            if len(x) > 1:
                self.equalEfficiencies.append(x)

        # Assignment of the initial and goal states. Notice that goal is only a list, since we only
        # need to check the state with a list of flags.
        self.initial = State(flags, [], patients, 0)        
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
        """ Input: node
            Output: a value that is going to be added to the path_cost
            Description: To compute the heuristic we make a simplification of our algorithm where we 
            don't take in consideration the maximum waiting time for each pacient. Here, we attribute
            the patients with the higher current waiting time first and, of those patients, we
            attribute the ones with higher consult time needs for the most efficient medics. 
            We loop through this algorithm while making the updates for each patients's waiting time,
            consult time, etc... Until all the patients have their consults fulfilled. In the end,
            using the waiting times, we compute the path cost from the current state until the goal state.
        """  
        state = deepcopy(node.state) #copy the state to be able to make updates without changing the state outside this function

        all_patients_waiting = {code:patient for code,patient in state.patients.items() if state.flags[code]}        
        wait_times = {code:0 for code in all_patients_waiting.keys()}

        n = len(self.medics) #the number of medics

        efficiencies_ordered = sorted(self.efficiencies, reverse=True) #the ordered efficiencies

        if len(all_patients_waiting) <= n:
            return 0 #in case we have less patients than medics, the pathcost for the goal is 0
        
        while len(all_patients_waiting) > n: 
            #the patients ordered by their current waiting time
            sortedCurrWait = sorted(all_patients_waiting.items(), key = lambda p : p[1].currWaitTime, reverse=True)
            
            #the first n patients of the list ordered by waiting time, ordered by their consult time needs
            sortedCurrConsult = sorted(sortedCurrWait[:n], key = lambda p : p[1].consultTime - p[1].currConsultTime, reverse = True)
            
            #update the values of the choosen patients for the schedule slot
            for idx, patient in enumerate(sortedCurrConsult):
                patient[1].currConsultTime += 5 * efficiencies_ordered[idx]

            #update the values for the patients that are not on the current slot of the schedule
            for code, patient in sortedCurrWait[n:]:
                patient.currWaitTime += 5
                wait_times[code] += 5

            #update the list of the patients that are still waiting (without their consult times fulfilled)
            all_patients_waiting = {code:patient for code,patient in all_patients_waiting.items() if patient.consultTime > patient.currConsultTime}
    
        return sum([wait**2 for wait in wait_times.values()]) #path cost from the current state to the goal state

        
    def search(self):
        """ Input: None
            Output: True if the problem has a solution | False if it doesn't
            Description: The function that implements the search problem using the
            chosen algorithm. We are using Astar with an heuristic to solve our problem."""  

        # N = b* + b*^2 + ... + b*^d = somatorio( b* ^ k     ) k=1:d

        # sum ( a * r^k ) = a * (r^m - r^(n-1)) / (1 - r), k=m:n
        # N = sum ( 1 * b^k ) = (b - b^(d-1)) / (1 - b), k=1:d
        
        # b = 1
        # N = 52
        # d = 5
        
        # while (abs(b - N) <= 0.1):
        #     sum = 0
        #     for x in range(1,d):
        #         sum += b**x

        #     b += 0.05
        

        self.solution = search.astar_search(self, self.heuristic, display = True)
        if self.solution:  #in case there is solution, return True
            print('Depth of the solution:',len(self.solution.state.schedule))
            return True
        
        return False       #if there is no solution, returns False
        

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

    def __lt__(self, other):
        return self.path_cost < other.path_cost

    def __eq__(self, other):
        consult_remaining_times = [(p.consultTime-p.currConsultTime) for p in self.patients.values()]
        consult_remaining_times_other = [(p.consultTime-p.currConsultTime) for p in other.patients.values()]

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

    print(f'{sys.argv[1]}:')
    with open(sys.argv[1]) as f:
        pmda.load(f)

    solution = pmda.search()
    with open("solution.txt", "w") as f:
        pmda.save(f)
    
    print(f'\nTime of searching: {time.time() - start_time}')