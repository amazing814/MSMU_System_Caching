##this is to simplify my program

import numpy as np

demands = np.array([[0, 0, 1],
                    [1, 0, 0],
                    [0, 1, 0]])
## which user asks for which file [K*I] matrix

distribution = np.array([[1, 0, 1],
                         [1, 1, 0],
                         [0, 1, 1]])
## which file is stored by which sender [I*J] matrix


connection = np.array([[0, 1, 1],
                       [1, 0, 1],
                       [1, 1, 0]])
## which sender is connected to which user [J*K] matrix

demands_distribution = np.dot(demands, distribution)
#[K*I]*[I*J]=[K*J] matrix, the demanded file of user k is stored by which sender

demands_sender = demands_distribution * connection.T
## [K*J] matrix, which demands can be taken by which sender

print(demands_sender)
