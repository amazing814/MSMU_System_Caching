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

r"""
In the multi-sender mulit-user system, we have
- I files, J senders and K users, the cache size of user is M

INPUT:
- ''demands'' -- [K*I] matrix: which user is asking for which file
- ''distribution'' -- [I*J] matrix: which file is stored by which sender
- ''connection'' -- [J*K] matrix: which sender is connected to which user
- ''M'' -- cache size of users
"""

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


##demands = np.array([[1, 0, 0],
##                    [0, 1, 0],
##                    [0, 0, 1]])
##
##distribution = np.array([[1,1,1],
##                         [1,1,1],
##                         [1,1,1]])
##
##connection = np.array([[0,1,1],
##                       [1,0,1],
##                       [1,1,0]])


K = demands.shape[0]
I = demands.shape[1]
J = distribution.shape[1]

a = Testify(distribution, connection)
user_demands_file = a.testify_phase()

b = Capability(demands, distribution, connection)
demands_sender = b.capability_matrix().tolist()

R_1 = []
R_2 = []
r_1 = []
r_2 = []

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
            
        R_1.append(R)
        R_2.append(R)
        r_1.append(r)
        r_2.append(r)

    elif M == I:

        R = 0
        r = 0
        R_1.append(R)
        R_2.append(R)
        r_1.append(r)
        r_2.append(r)
        
    else:

        # for the 1st method
        method_1 = FirstRate(demands_sender, t)
        rate_pair_1 = method_1.required_rate() #[R, r] for the first method

        R_1.append(rate_pair_1[0]*packet_size)
        r_1.append(rate_pair_1[1]*packet_size)

        #*****************************************************

        # for the 2nd method
        method_2_step_1 = Table(demands_sender, K, J, M) 
        capability_table = method_2_step_1.table_list() # capablitiy_table is a list [[[{},{},...],...],...]

        method_2_step_2 = SecondMethod(capability_table)
        track = method_2_step_2.assignment_phase() # track is a list of dict.

        method_2_step_3 = SecondRate(demands_sender, track, t)
        rate_pair_2 = method_2_step_3.required_rate() # [R, r] for the second method

        R_2.append(rate_pair_2[0]*packet_size)
        r_2.append(rate_pair_2[1]*packet_size)

print('R_1: ', R_1)
print('R_2: ', R_2)
print('r_1: ', r_1)
print('r_2: ', r_2)

# now, draw the picture
# At first, set the axis for M
cach_size = []
for m in range(I+1):
    cach_size.append(m)
    

plt.subplot(121)
plt.plot(cach_size, R_1, "go-", label="$R_1$", linewidth=2)
plt.plot(cach_size, R_2, "rv-", label="$R_2$")
plt.axis([0, I+0.2 , 0, R_1[0]+0.2])
plt.legend()
plt.xlabel("Cache size M (F-bits)")
plt.ylabel("Performance Analysis (F-bits)")
plt.title("Maximum required transmission rate of senders")

plt.subplot(122)
plt.plot(cach_size, r_1, 'go-', label='$r_1$', linewidth=2)
plt.plot(cach_size, r_2, 'rv-', label='$r_2$')
plt.axis([0, I+0.2 , 0, R_1[0]+0.2])
plt.legend()
plt.xlabel("Cache size M (F-bits)")
plt.ylabel("Performance Analysis (F-bits)")
plt.title("Maximum required transmission rate through links")

    
plt.show()










        

