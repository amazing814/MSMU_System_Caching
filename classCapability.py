#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import numpy as np

r"""
This script outputs the capability matrix for MSMU system
"""

class Capability(object):
    r"""
    INPUT:
    - ''demands'' -- [K*I] matrix: which user is asking for which file
    - ''distribution'' -- [I*J] matrix: which file is stored by which sender
    - ''connection'' -- [J*K] matrix: which sender is connected to which user

    OUTPUT:
    - ''demands_distribution'' -- [K*J] matrix: which demanded file of user k
    is stored by which sender
    - ''demands_sender'' -- [K*J] matrix: which demanded file of user k can be
    sent by which sender
    """
    def __init__(self, demands, distribution, connection):

        self.__demands = demands
        self.__distribution = distribution
        self.__connection = connection

    def capability_matrix(self):
        self.__demands_distribution = np.dot(self.__demands, self.__distribution)
        self.__demands_sender = self.__demands_distribution * self.__connection.T
        return(self.__demands_sender)
        

if __name__ == "__main__":
    
    demands = np.array([[0, 0, 1],
                    [1, 0, 0],
                    [0, 1, 0]])

    distribution = np.array([[1, 0, 1],
                         [1, 1, 0],
                         [0, 1, 1]])

    connection = np.array([[0, 1, 1],
                       [1, 0, 1],
                       [1, 1, 0]])

    a = Capability(demands, distribution, connection)
    c = a.capability_matrix()
##    print (c)
    



        
    
