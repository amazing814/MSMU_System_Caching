import itertools
import numpy as np
import copy

r"""
Based on matrix 'demands_sender' offered by: a = Capability(demands, distribution, connection)
                                             demands_sender = a.capability_matrix().tolist()
and dict 'track' offered by: c = SecondMethod(capability_table)
                             track = c.assignment_phase().
                                                   
Now we calculate the R and r by the 2nd method
"""

class SecondRate(object):
    r"""

    INPUT:
    - ''demands_sender'' -- [K*J] matrix: which user's demands can be fulfilled by
    which sender
    - ''track'' -- the dictionary_result of assignment_phase: which delivery_task
    is assigned to which sender_union
    - ''t'' -- int(M*K/I)

    OUTPUT:
    - ''.R_max'' -- the maximum required transmission rate of senders (by 2nd method)
    - ''.R_min'' -- the minimum required transmission rate of senders
    - ''.r_max'' -- the maximum required transmission rate through links (by 2nd method)
    - ''.r_min'' -- the minimum required transmission rate through links (except for 0)
    - ''.user_sender_packets'' -- this matrix tells each user gets how many packets
                                  from each sender, i.e., the required transmission
                                  rate through each link
    - ''.single_delivery_task_relevant_sender'' -- this dictionary tells each user
                                                   gets file from which sender during
                                                   different delivery_task
    - ''.sender_packet'' -- the vector tells the required transmission rate of senders
    
    """

    def __init__(self, demands_sender, track, t):
        
        self.__demands_sender = demands_sender
        self.__track = copy.deepcopy(track)
        # the track will be changed in this class, so we use deepcopy to avoid potential damage            
        self.__t = t

        self.R_max = 0
        self.R_min = 0      
        self.r_max = 0
        self.r_min = 0

    def required_rate(self):

        K = len(self.__demands_sender)
        J = len(self.__demands_sender[0])

        US = itertools.combinations(range(K), self.__t+1)
        user_subset = [list(us) for us in US]

        # delivery_task_relevant_user_subset: key = delivery_task; value = its relevant user_subset
        # e.g., delivery_task_relevant_user_subset['DS_1'] = [0, 1, 4] means
        # that the first delivery_task is assigned to sender_one, sender_two and sender_five
        delivery_task_relevant_user_subset = dict()
        for delivery_task, relevant_user_subset in enumerate(user_subset):
            delivery_task_relevant_user_subset['DS_'+str(delivery_task+1)] = relevant_user_subset

        # dict_user_subset_demands_sender: key = delivery_task; value = matrix of the capablitiy senders for this delivery_task
        dict_user_subset_demands_sender = dict()   

        for keys in delivery_task_relevant_user_subset:
            user_subset_demands_sender = np.zeros(np.shape(self.__demands_sender), dtype = np.int)
            
            for user in delivery_task_relevant_user_subset[keys]:
                user_subset_demands_sender[user] = copy.deepcopy(self.__demands_sender[user])

            dict_user_subset_demands_sender[keys] = user_subset_demands_sender

        r"""
        In dict_user_subset_demands_sender: its key is 'DS_XXX'; value is the relevant
        matrix of 'DS_XXX', e.g., DS_1 is the first delivery task aims for user-subset
        [0,1,2] (user_one, user_two and user_three). then
          dict_user_subset_demands_sender['DS_1'] = array([[1, 1, 0, 0],
                                                           [1, 0, 1, 0],
                                                           [1, 0, 0, 1],
                                                           [0, 0, 0, 0],
                                                           [0, 0, 0, 0],
                                                           [0, 0, 0, 0]])
        where the rows for rest users (user_four, user_five and user_six) are set zero.
        """

        # since in the 'track', where {'DS_XXX';{12}}， which means delivery_task XXX is assigned to user_one and user_two
        # now we need to change the form of track into
        # assignment_result_lang, where {'DS_XXX': [0, 1, 0, 1]} 

        assignment_result = dict() # used to calculate R and for assignment_result_lang

        for i in range(len(self.__track)):
            for keys in self.__track[i]:
                recorder = []
                # recorder is to change {DS_1 : 14} to be {DS_1 : [1,4]}
                # then to be {DS_1 : [0,3]}
                for j in range(i+1)[::-1]:
                    recorder_help = int(self.__track[i][keys]/(10**(j)))
                    recorder.append(recorder_help-1)
                    self.__track[i][keys] = self.__track[i][keys]-(recorder_help*(10**j))
                assignment_result[keys] = recorder

    

        assignment_result_lang = dict() # used to calculate r

        for keys in assignment_result:
            lang_list = np.zeros(J, dtype = np.int)
            for i in assignment_result[keys]:
                lang_list[i] = 1
            assignment_result_lang[keys] = lang_list

        r"""
        give assignment_result_lang, e.g., assignment_result_lang['DS_7'] = array([1, 0, 1, 0]),
        which indicates that the 7the delivery_task is taken by sender_one and sender_three
        """
        
        self.sender_packets = np.zeros(J, dtype = np.int)
        for keys in assignment_result_lang:
            self.sender_packets = self.sender_packets+assignment_result_lang[keys]

        ####################################################################
        self.R_max = self.sender_packets.max()
        self.R_min = self.sender_packets.min()
        ###################################################################

        
        r"""
        given dict_user_subset_demands_sender and assignment_result_lang, e.g.,
        dict_user_subset_demands_sender['DS_3']  =  array([[1, 1, 0, 0],
                                                           [1, 0, 1, 0],
                                                           [0, 0, 0, 0],
                                                           [0, 0, 0, 0],
                                                           [0, 1, 0, 1],
                                                           [0, 0, 0, 0]])
        while assignment_result_lang['DS_3'] = array([0, 1, 1, 0]).
        We should get the reult as: array([[0, 1, 0, 0],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 0],
                                           [0, 0, 0, 0],
                                           [0, 1, 0, 0],
                                           [0, 0, 0, 0]])
                                                        
        which indicates that, sender_two sends file-pieces for user_one and user_five,
        and sender_three sends file-piece for user_two. (in the third delivery task)
        """
        
        self.single_delivery_task_relevant_sender = dict() # matrix for every delivery_task and its relevant senders
        self.user_sender_packets = np.zeros(np.shape(dict_user_subset_demands_sender[keys]), dtype=np.int)

        for keys in dict_user_subset_demands_sender:
            
            matrix_recorder_help = np.zeros(np.shape(dict_user_subset_demands_sender[keys]), dtype=np.int)
            
            for i in range(len(dict_user_subset_demands_sender[keys])):
                matrix_recorder_help[i] = dict_user_subset_demands_sender[keys][i]*assignment_result_lang[keys]
                
            self.single_delivery_task_relevant_sender[keys] = matrix_recorder_help
            self.user_sender_packets = self.user_sender_packets + matrix_recorder_help

        #######################################################################            
        self.r_max = self.user_sender_packets.max()

        min_recorder = 10000
        for i in self.user_sender_packets:
            for j in i:
                if j != 0:
                    min_recorder = min(min_recorder, j)
        self.r_min = min_recorder
        #######################################################################
##        T = itertools.combinations(range(K), self.__t)
##        files = [f for f in T]
##        file_size = len(files)
        
        return ([self.R_max, self.r_max])


if __name__ == "__main__":

##    track = [{'DS_6': 2, 'DS_4': 3},
##             {'DS_3': 12, 'DS_1': 13, 'DS_2': 12, 'DS_5': 23}]
##
##    t=1
##
##    demands_sender = [[1, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0]]

    track = [{'DS_15': 3, 'DS_19': 4, 'DS_1': 1, 'DS_8': 2},
             {'DS_6': 12, 'DS_14': 34, 'DS_7': 13, 'DS_9': 23,
              'DS_4': 14, 'DS_11': 34, 'DS_18': 13, 'DS_10': 24,
              'DS_13': 13, 'DS_5': 12, 'DS_16': 14, 'DS_20': 24,
              'DS_12': 14, 'DS_3': 23, 'DS_2': 12, 'DS_17': 34},
             {}]

    t = 2

    demands_sender = [[1, 1, 0, 0],
                      [1, 0, 1, 0],
                      [1, 0, 0, 1],
                      [0, 1, 1, 0],
                      [0, 1, 0, 1],
                      [0, 0, 1, 1]]

    a = SecondRate(demands_sender, track, t)
    b = a.required_rate() # b = [R, r]
    c = [a.R_min, a.r_min]
    print('The maximum required transmission rate pair [R, r] is: ', b)
    print('The minimum required transmission rate pair [R, r] is: ', c)
