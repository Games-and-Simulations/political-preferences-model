from estimator import Estimator
from dataset_loader import DatasetLoader
from dataset_loader import DataScheme
from sklearn.model_selection import KFold


'''
Skript vygeneruje Learning Rate graf
pro naimportovaný model.

'''

# zde se importuje konkretni model
import models_source.model05 as source

# MODEL
create_model = source.create_model
n_splits = source.n_splits
epochs = source.epochs
batch_size = source.batch_size
modelname = (create_model.__module__).split('.')[1]

# DATA
dataset = DatasetLoader("data/demography.csv", "data/Results_snemovna2017.csv")
inputset = dataset.get_input_acc_to_scheme(DataScheme.ALL)
outputset = dataset.get_outputset()
metadata = dataset.metadata

# TRENINK
estimator = Estimator(create_model)
split = KFold(n_splits=n_splits)

# GRAF
subset_score_progress = estimator.get_LR(inputset, outputset, range(10,101,5), 0.2, split, epochs, batch_size) 

estimator.plot_LR(subset_score_progress, range(10,101,5), label1='Testovací sada 20%', filepath='graphs/learning_rate/'+ modelname)
