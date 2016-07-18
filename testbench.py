import numpy as np

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

r"""
INPUT:
- ''demands'' -- [K*I] matrix: which user is asking for which file
- ''distribution'' -- [I*J] matrix: which file is stored by which sender
- ''connection'' -- [J*K] matrix: which sender is connected to which user
- ''M'' -- cache size of users
"""

M = 2

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


K = demands.shape[0]
I = demands.shape[1]
J = distribution.shape[1]
t = int(M*K/I)

f = Testify(distribution, connection)
user_demands_file = f.testify_phase()


a = Capability(demands, distribution, connection)
demands_sender = a.capability_matrix().tolist()

# for the 1st method
e = FirstRate(demands_sender, t)
rate_pair_1 = e.required_rate() #[R, r]
print('1:',rate_pair_1)

b = Table(demands_sender, K, J, M)
capability_table = b.table_list()

# for the 2nd method
c = SecondMethod(capability_table)
track = c.assignment_phase() # or track = c.track

d = SecondRate(demands_sender, track, t)
rate_pair_2 = d.required_rate() # [R, r]
print('2:', rate_pair_2)

