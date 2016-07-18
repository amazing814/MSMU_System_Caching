#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import numpy as np

class Testify(object):
    r"""
    To testify if the flexible matrix fits in the fixed matrix

    INPUT:

    file_sender_distribution -- [I*J] matrix: which file is stored by which sender
    sender_user_connection -- [J*K] matrix: which sender is connected to which user

    OUTPUT:
    file_user_distribution -- [I*K] matrix: which file is connected to which user, by how many times

    """

    def __init__(self, file_sender_distribution, sender_user_connection):

        self.__file_sender_distribution = file_sender_distribution
        self.__sender_user_connection = sender_user_connection

    def testify_phase(self):

        self.__file_user_distribution = np.dot(self.__file_sender_distribution,
                                        self.__sender_user_connection)
        if self.__file_user_distribution.min() == 0:
            print ('Wrong, type in a new distribution matrix.')
        else:
            print ('Right, let us move on.')

        return (self.__file_user_distribution)



if __name__ == "__main__":
    
    a = np.array([[0, 1], [1, 1]])
    b = np.array([[1, 1], [1, 1]])
    c= Testify(a, b).testify_phase()





    
