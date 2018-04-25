from estimator import Estimator
from dataset_loader import DatasetLoader
from dataset_loader import DataScheme
from sklearn.model_selection import KFold
import utils

# zde se importuje konkretni model
import models_source.model06 as source

create_model = source.create_model
n_splits = source.n_splits
epochs = source.epochs
batch_size = source.batch_size


# Prepare DATA
dataset = DatasetLoader("data/demography.csv", "data/Results_snemovna2017.csv")
inputset = dataset.get_input_acc_to_scheme(DataScheme.ALL)
outputset = dataset.get_outputset()
metadata = dataset.metadata

# test MODEL
estimator = Estimator(create_model)
split = KFold(n_splits=n_splits)


estimator.train(inputset, outputset, split, epochs=epochs, batch_size=batch_size)

# jmeno python souboru jako string
modelname = (create_model.__module__).split('.')[1]

estimator.save_prediction_to_file(inputset, metadata, 'data/predictions/' + modelname + '.csv')
estimator.save_model_to_file()

utils.generate_graphs(estimator, modelname)

