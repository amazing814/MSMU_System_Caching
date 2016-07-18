import numpy as np

import matplotlib.pyplot as plt

import copy

import itertools

from classTestify import Testify
# this class is to testify if the input matrices suitable, i.e., every user can
# get every file from senders (min(user_demands_file) > 0)

from classCapability import Capability
# this class is to output the [K*J] matrix named as 'demands_sender', where
# demands_sender[k][j] == 1 indicates that the demand of user_k can be fulfilled
# by sender_j. (otherwise, demands_sender[k][j] == 0)

from classTable import Table
# this class is to ouput the matrix named as 'capablility_table', where
# capability_table[0] = [[set of capable single_sender],[set of capable double_senders],.....]
# collected the capable senders of different union size for the first delivery task

from class2ndMethod import SecondMethod
# this class is to output the dictionary as 'track', where track['DS_1'] == 34
# indicates that the first delivery task is assigned to the double_sender_union
# ---{sender_3, sender_4}. (assignment_phase by 2nd method)

from class2Randr import SecondRate
# this class is to output the R and r by 2nd method (delivery_phase).
# use xxx.[key-Tab] to find more outputs!

from class1stRandr import FirstRate
# this class is to output the R and r by 1st method. Since no maximum matching
# is used in 1st method, so we combine the assignment_phase and delivery_phase
# together in this class. use xxx.[key-Tab] to find more outputs!

from classFenpei import HopcroftKarp



class GeneralizedCodedCaching(object):
    
    r"""
    In the multi-sender mulit-user system, we have
    - I files, J senders and K users, the cache size of user is M

    INPUT:
    - ''demands'' -- [K*I] matrix: which user is asking for which file
    - ''distribution'' -- [I*J] matrix: which file is stored by which sender
    - ''connection'' -- [J*K] matrix: which sender is connected to which user
    """
    
    def __init__(self, demands, distribution, connection):
        
        self.__demands = demands
        self.__distribution = distribution
        self.__connection = connection


    def calculater(self):

        K = self.__demands.shape[0]
        I = self.__demands.shape[1]
        J = self.__distribution.shape[1]

        a = Testify(self.__distribution, self.__connection)
        user_demands_file = a.testify_phase()

        b = Capability(self.__demands, self.__distribution, self.__connection)
        demands_sender = b.capability_matrix().tolist()

        self.R_1 = []
        self.R_2 = []
        self.r_1 = []
        self.r_2 = []


        for M in range(I+1): # M belongs to [0,1,2,...,I]

            t = int(M*K/I)

            T = itertools.combinations(range(K), t)
            files = [f for f in T]
            file_part = len(files)
            packet_size = 1/file_part
    
            if M == 0: # we do maximum matching for the assignment if M=0
                assignment_M_0 = dict()
                
                for user in range(len(demands_sender)):
                    sender_recorder = []
                    for sender in range(len(demands_sender[user])):
                        if demands_sender[user][sender] == 1:
                            sender_recorder.append(sender+1)
                    #print(sender_recorder)
                    assignment_M_0['DS_'+str(user+1)] = set(sender_recorder)

                R = 0 
                r = 1 # every user get his required file from one of its capable senders,
                      # i.e., r_max = 1, r_min = 0.
                while assignment_M_0 != {}:

                    assignment_result_M_0 = HopcroftKarp(copy.deepcopy(assignment_M_0)).maximum_matching()
                    for keys in assignment_result_M_0:
                        if type(keys) != int:
                            assignment_M_0.pop(keys)
                    R = R + 1
                    
                self.R_1.append(R)
                self.R_2.append(R)
                self.r_1.append(r)
                self.r_2.append(r)
            

            elif M == I:

                R = 0
                r = 0
                self.R_1.append(R)
                self.R_2.append(R)
                self.r_1.append(r)
                self.r_2.append(r)
        
            else:

                # for the 1st method
                method_1 = FirstRate(demands_sender, t)
                rate_pair_1 = method_1.required_rate() #[R, r] for the first method

                self.R_1.append(rate_pair_1[0]*packet_size)
                self.r_1.append(rate_pair_1[1]*packet_size)

                #*****************************************************

                # for the 2nd method
                method_2_step_1 = Table(demands_sender, K, J, M) 
                capability_table = method_2_step_1.table_list() # capablitiy_table is a list [[[{},{},...],...],...]

                method_2_step_2 = SecondMethod(capability_table)
                track = method_2_step_2.assignment_phase() # track is a list of dict.

                method_2_step_3 = SecondRate(demands_sender, track, t)
                rate_pair_2 = method_2_step_3.required_rate() # [R, r] for the second method

                self.R_2.append(rate_pair_2[0]*packet_size)
                self.r_2.append(rate_pair_2[1]*packet_size)


    def draw_picture(self):
        
        # At first, set the axis for M
        cach_size = []
        for m in range(self.__demands.shape[1] + 1): # I+1
            cach_size.append(m)
    
        # Then, draw the system performance facing different cache size(M)
        plt.subplot(121)
        plt.plot(cach_size, self.R_1, "go-", label="$R_1$", linewidth=2)
        plt.plot(cach_size, self.R_2, "rv-", label="$R_2$")
        plt.axis([0, self.__demands.shape[1]+0.2 , 0, self.__demands.shape[1]+0.2])
        plt.legend()
        plt.xlabel("Cache size M (F-bits)")
        plt.ylabel("Performance Analysis (F-bits)")
        plt.title("Maximum required transmission rate of senders")

        plt.subplot(122)
        plt.plot(cach_size, self.r_1, 'go-', label='$r_1$', linewidth=2)
        plt.plot(cach_size, self.r_2, 'rv-', label='$r_2$')
        plt.axis([0, self.__demands.shape[1]+0.2 , 0, self.__demands.shape[1]+0.2])
        plt.legend()
        plt.xlabel("Cache size M (F-bits)")
        plt.ylabel("Performance Analysis (F-bits)")
        plt.title("Maximum required transmission rate through links")
  
        plt.show()


#********************************************************************

if __name__ == "__main__":
    

    # this is the network structure in Fig. 4.6 and Fig. 4.7
    demands = np.array([[0, 1, 0],   # user_1 needs file_2
                        [1, 0, 0],   # user_2 needs file_1
                        [0, 0, 1]])  # user_3 needs file_3

    distribution = np.array([[1,1,1], # file_1 is stored in sender_1, sender_2 and sender_3
                             [1,1,1],
                             [1,1,1]])

    connection = np.array([[0,1,1], # sender_1 is connected to user_2 and user_3
                           [1,0,1], # sender_2 is connected to user_1 and user_3
                           [1,1,0]])# sender_3 is connected to user_1 and user_2
    
    r"""
    Of course, you can type in any matrices if you like
    """
##    # this is the network structure in Fig. 4.2
##    demands = np.array([[1, 0, 0, 0],
##                        [0, 1, 0, 0],
##                        [0, 0, 1, 0],
##                        [0, 0, 0, 1]])
##
##    distribution = np.array([[1,0,0],
##                             [1,0,1],
##                             [0,1,1],
##                             [0,1,0]])
##
##    connection = np.array([[1,0,0,1],
##                           [0,1,1,1],
##                           [1,1,1,1]])
##

##    # this is the network structure in Fig. 4.3 and Fig. 4.4
##    demands = np.array([[1, 0, 0],
##                        [0, 1, 0],
##                        [0, 0, 1]])
##
##    distribution = np.array([[1,1,1],
##                             [1,1,1],
##                             [1,1,1]])
##
##    connection = np.array([[1,1,1],
##                           [1,1,1],
##                           [1,1,1]])

##    # this is the network stucture in Fig. 4.10
##    demands = np.array([[1, 0, 0, 0, 0, 0],
##                        [0, 1, 0, 0, 0, 0],
##                        [0, 0, 1, 0, 0, 0],
##                        [0, 0, 0, 1, 0, 0],
##                        [0, 0, 0, 0, 1, 0],
##                        [0, 0, 0, 0, 0, 1]])
##
##    distribution = np.array([[1, 1, 1, 1],
##                             [1, 1, 1, 1],
##                             [1, 1, 1, 1],
##                             [1, 1, 1, 1],
##                             [1, 1, 1, 1],
##                             [1, 1, 1, 1]])
##
##    connection = np.array([[1, 1, 1, 0, 0, 0],
##                           [1, 0, 0, 1, 1, 0],
##                           [0, 1, 0, 1, 0, 1],
##                           [0, 0, 1, 0, 1, 1]])

    a = GeneralizedCodedCaching(demands, distribution, connection)
    b = a.calculater()
    c = a.draw_picture()




        

