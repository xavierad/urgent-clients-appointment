class node:
    def __init__(self, state):
        self.state = state

    def __eq__(self, other):        
        return isinstance(other, node) and self.state == other.state

    def __hash__(self):
        # We use the hash value of the state
        # stored in the node instead of the node
        # object itself to quickly search a node
        # with the same state in a Hash Table
        return hash(self.state)

class State:
    def __init__(self, schedule):
        self.schedule = schedule

    
    def __eq__(self, other):
        return tuple(self.schedule) == tuple(other.schedule) and isinstance(other, State)

    def __hash__(self):
        # We use the hash value of the state
        # stored in the node instead of the node
        # object itself to quickly search a node
        # with the same state in a Hash Table
        return hash(tuple(self.schedule))


if __name__ == "__main__":
    state1 = State([(1,2),(3,4)])
    state2 = State([(1,2),(3,4)])
    state3 = State([(3,4),(1,2)])

    node1 = node(state1)
    node2 = node(state2)
    node3 = node(state3)

    if state1.schedule==state2.schedule:
        print('states equal!')

    if node1==node2:
        print('nodes equal!')

    if state1.schedule==state3.schedule:
        print('states equal!')

    if node1==node3:
        print('nodes equal!')
    

    # print(node1.state)
    # print(node2.state)