import numpy as np
import itertools
import copy

from classTestify import Testify
from classCapability import Capability

class Table(object):
    r"""
    INPUT:
    - ''demands_sender'' -- [K*J] matrix: which user's demand can be fulfilled
                             by which sender, it is the result form Class_Capability
                             a = Capability(demands, distribution, connection)
                             demands_sender = a.capability_matrix().tolist()
    - ''K'' -- number of users
    - ''t'' -- t=int(M*K/I)

    """

    def __init__(self, demands_sender, K, J, t):
        
        self.__demands_sender = demands_sender
        self.__K = K
        self.__J = J
        self.__t = t

        US = itertools.combinations(range(self.__K), self.__t +1)
        self.__user_subsets = [us for us in US] # pick up all the user-subsets, i.e., deilvery-tasks
    
    def table_list(self):
        
        subset_demands_sender = [None]*len(self.__user_subsets) # every delivery task and its potential capable senders
        sender_subset_demands = [None]*len(self.__user_subsets) # the transposion of matrices above
        capable_sender_subset_demands = [None]*len(self.__user_subsets) # the recorder to track capable-senders for each delivery task
        maximum_sender_union_size = self.__t +1 # the maximum size of possible sender-union
        
        for i, one_subset in enumerate(self.__user_subsets):
            subset_demands_sender[i] = []
            for one_user, j in enumerate(one_subset):
                subset_demands_sender[i].append(copy.deepcopy(self.__demands_sender[j]))
        # subset_demands_sender is a "list in List",
        # we should change every sub-list into np.array, for "transpose of a matrix" in a easier way 
        
        subset_demands_sender_array = np.array(subset_demands_sender)    
        # now every sub-list is a array/matrix 


        for sub in range(len(self.__user_subsets)):
            
            capable_sender_subset_demands[sub] = []
            sender_subset_demands[sub] = subset_demands_sender_array[sub].T # transposition
            
            multi_capable_sender = [None]* maximum_sender_union_size # the track list for different sized sender_union： single, double, triple...

            r"""
            below is to record every possible capable-senders for this delivery-task
            """
            for union_size in range(maximum_sender_union_size):
                
                multi_capable_sender[union_size] = []
                CS = itertools.combinations(range(self.__J), union_size +1)
                sender_unions = [cs for cs in CS]

                for one_sender_union in sender_unions:
                    min_help = np.zeros(self.__t +1, dtype=np.int)
                    for sender in one_sender_union:
                        min_help = min_help + sender_subset_demands[sub][sender]
                    if min(min_help)>0:
                        multi_capable_sender[union_size].append(set(one_sender_union))

            r"""
            However, the multi_capable_sender above is not exactly what we want.
            The content may be [[(1,), ...], [(1, 2), (1, 3), ...], ...],
            since (1,) already exists, then (1, 2)/(1, 3) is not alowed
            i.e., the capable-senders should not belongs to each other
            """

            for smaller_sender_union in range(maximum_sender_union_size):
                for bigger_sender_union in range(smaller_sender_union + 1, maximum_sender_union_size):
                    record_list = []
                    for i in multi_capable_sender[smaller_sender_union]:
                        for j in multi_capable_sender[bigger_sender_union]:
                            if i.issubset(j):
                                record_list.append(j)
                    # because record_list may contain repeated component
                    # e.g., i1 belongs to j1 while i2 also belongs to j1，then j1 is recorded twice
                    # belows the repeated component is eliminated (the extra ones)
                    record_list_c = []
                    [record_list_c.append(i) for i in record_list if not i in record_list_c]

                    for k in record_list_c:
                        multi_capable_sender[bigger_sender_union].remove(k)

            r"""
            now the multi_capable_sender contains all capable-senders for this delivery-task
            it looks like [[single_sender]，[double_sender]...],
            where none of the capable senders belongs to each other.
            Then, we take this multi_capable_sender back to the list of capable_sender_subset_demands
            """

            for i in multi_capable_sender:
                capable_sender_subset_demands[sub].append(i)


        return (capable_sender_subset_demands)



if __name__ == "__main__":

    demands = np.array([[1, 0, 0, 0, 0, 0],
                        [0, 1, 0, 0, 0, 0],
                        [0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1]])

    distribution = np.array([[1, 1, 1, 1],
                             [1, 1, 1, 1],
                             [1, 1, 1, 1],
                             [1, 1, 1, 1],
                             [1, 1, 1, 1],
                             [1, 1, 1, 1]])

    connection = np.array([[1, 1, 1, 0, 0, 0],
                           [1, 0, 0, 1, 1, 0],
                           [0, 1, 0, 1, 0, 1],
                           [0, 0, 1, 0, 1, 1]])

    a = Capability(demands, distribution, connection)
    demands_sender = a.capability_matrix().tolist()

    b = Table(demands_sender, 6, 4, 2)
    capability_table = b.table_list()
           
    i = 0
    for j in capability_table:
        print ('delivery task ', i, 'can be taken by: ', j)
        i = i+1


















