import numpy

class DataScheme:
    ALL, DEMOGRAPHY_FEW_PER_CATEGORY, DEMOGRAPHY_BASED_ON_PCA = range(3)

class DatasetLoader:
    
    def __init__(self, inputset_file, outputset_file):
        self.inputset = numpy.loadtxt(inputset_file, delimiter=",", skiprows=1)
        self.outputset = numpy.loadtxt(outputset_file, delimiter=",", skiprows=1)[:,5:]

        self.metadata = self.inputset[:,0:3]
        self.inputset = self.inputset[:,3:]

        # count share of votes for other parties so that all shares sums to one
        # this is done because the results published by czso.cz by default do not (they are rounded)
        for i in range(len(self.outputset)):
            for j in range(len(self.outputset[0])):
                self.outputset[i][j] = self.outputset[i][j] / 100 
            self.outputset[i][0] = 1 - self.outputset[i][1:].sum()  
    
    def get_outputset(self):
        return self.outputset
    
    def get_input_acc_to_scheme(self, scheme=DataScheme.ALL):
        '''
        Get input data according to predefined schemes.
        '''  
        return self.get_input_columns(self.get_input_scheme(scheme))
    
    def get_input_scheme(self, scheme):
        return {
            DataScheme.ALL:                 range(0,self.inputset.shape[1]),    # 30 - all columns
            DataScheme.DEMOGRAPHY_FEW_PER_CATEGORY:    [0,1,3,8,9,13,15,16,18,21,22,26],   # 12 - few per category
            DataScheme.DEMOGRAPHY_BASED_ON_PCA:        [5,10,12,13,14,20,22]               # 7 most significant
                }.get(scheme, range(0,self.inputset.shape[1]))
    
    def get_input_columns(self, columns_arr):
        '''
        columns_arr - list with indeces of columns to be returned
        '''
        return self.inputset[:,columns_arr]