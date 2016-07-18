import numpy as np
import itertools
import copy

r"""

This script implements 1st method and outputs the required transmission rate
"""

class FirstRate(object):
    r"""
    INPUT:
    - ''demands_sender'' -- the [K*J] matrix: which user's requirement can be
                            fulfilled by which sender
    - '' t '' -- int(M*K/ I)
    
    OUTPUT:
    - ''.R_max'' -- the maximum required transmission rate of senders (by 2nd method)
    - ''.R_min'' -- the minimum required transmission rate of senders
    - ''.r_max'' -- the maximum required transmission rate through links (by 2nd method)
    - ''.r_min'' -- the minimum required transmission rate through links (except for 0)
    - ''.user_sender_packets'' -- this matrix tells each user gets how many packets
                                  from each sender, i.e., the required transmission
                                  rate through each link
    - ''.real_user_subset_demands_sender'' -- this dictionary tells each user
                                                   gets file from which sender during
                                                   different delivery_task
    - ''.sender_packet'' -- the vector tells the required transmission rate of senders
    """

    def __init__(self, demands_sender, t):

        self.__demands_sender = np.array(demands_sender)
        self.__t = t
        
        self.R_max = 0
        self.R_min = 0
        self.r_max = 0
        self.r_min = 0
        

    def required_rate(self):

        K = self.__demands_sender.shape[0]
        J = self.__demands_sender.shape[1]

        user_subset_demands_sender = []
        #to track every delivery task and its relevant capable senders

        cut_value = []
        #to track every delivery task will be split into how many smaller pieces

        S = itertools.combinations(range(K), self.__t+1)
        user_subsets = [f for f in S]


        for one_user_subset in user_subsets:
            one_user_subset_demands_sender = np.ones(np.shape(self.__demands_sender), dtype = np.int)*2
            for one_user in one_user_subset:
                one_user_subset_demands_sender[one_user] = copy.deepcopy(self.__demands_sender[one_user])
    
            user_subset_demands_sender.append(one_user_subset_demands_sender)
            cut_value.append(np.min(np.sum(one_user_subset_demands_sender, axis=1)))


        for delivery_task in range(len(user_subset_demands_sender)):
            for one_user in user_subsets[delivery_task]:
                cut_recorder = 0
                for one_sender in range(len(user_subset_demands_sender[delivery_task][one_user])):
                    cut_recorder = cut_recorder + user_subset_demands_sender[delivery_task][one_user][one_sender]
                    if cut_recorder > cut_value[delivery_task]:
                        user_subset_demands_sender[delivery_task][one_user][one_sender] = 0
            

        self.real_user_subset_demands_sender = []

        for delivery_task in range(len(user_subsets)):
            one_user_subset_demands_sender = np.zeros(np.shape(self.__demands_sender), dtype = np.int)

            for one_user in user_subsets[delivery_task]:
                one_user_subset_demands_sender[one_user] = copy.deepcopy(user_subset_demands_sender[delivery_task][one_user])

            self.real_user_subset_demands_sender.append(one_user_subset_demands_sender)


        assignment_result = [] # to track which sender participates in each delivery_task

        for delivery_task in range(len(self.real_user_subset_demands_sender)):
            assignment_result_lang = np.zeros(J)
            
            for one_user in range(len(self.real_user_subset_demands_sender[delivery_task])):
                for one_sender in range(len(self.real_user_subset_demands_sender[delivery_task][one_user])):
                    if self.real_user_subset_demands_sender[delivery_task][one_user][one_sender] == 1:
                        assignment_result_lang[one_sender] = 1/(cut_value[delivery_task])

            assignment_result.append(assignment_result_lang)

        self.sender_packet = np.zeros(J) # to calculate R
        for rate_single_delivery_task in assignment_result:
            self.sender_packet = self.sender_packet + rate_single_delivery_task

        #################################################################
        self.R_max = self.sender_packet.max()
        self.R_min = self.sender_packet.min()
        #################################################################

        self.user_sender_packets = np.zeros(np.shape(self.__demands_sender), dtype = np.int) # to calculate r

        for delivery_task in range(len(self.real_user_subset_demands_sender)):
            
            self.real_user_subset_demands_sender[delivery_task] = self.real_user_subset_demands_sender[delivery_task]/cut_value[delivery_task]
            self.user_sender_packets = self.user_sender_packets + self.real_user_subset_demands_sender[delivery_task]
            
        ######################################################################
        self.r_max = self.user_sender_packets.max()

        min_recorder = 10000
        for i in self.user_sender_packets:
            for j in i:
                if j != 0:
                    min_recorder = min(min_recorder, j)
        self.r_min = min_recorder
        ######################################################################

        return([self.R_max, self.r_max])

if __name__ == "__main__":

##    demands_sender = [[1, 1, 1, 0],
##                               [1, 1, 1, 0],
##                               [1, 1, 1, 1],
##                               [0, 1, 1, 0],
##                               [0, 1, 0, 1],
##                               [0, 0, 1, 1]]
    
##    demands_sender =  [[1, 1, 0, 0],
##                       [1, 0, 1, 0],
##                       [1, 0, 0, 1],
##                       [0, 1, 1, 0],
##                       [0, 1, 0, 1],
##                       [0, 0, 1, 1]]
##
##    t = 2
    
    demands_sender = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    t = 1

    a = FirstRate(demands_sender, t)
    b = a.required_rate()
