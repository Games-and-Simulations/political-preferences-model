from estimator import Estimator
from dataset_loader import DatasetLoader
from dataset_loader import DataScheme
from sklearn.model_selection import KFold
import utils
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# zde se importuje konkretni model
import models_source.model01 as source

create_model = source.create_model
n_splits = source.n_splits
epochs = source.epochs
batch_size = source.batch_size


# Priprav DATA
dataset = DatasetLoader("data/demography.csv", "data/Results_snemovna2017.csv")
inputset = dataset.get_input_acc_to_scheme(DataScheme.ALL)
outputset = dataset.get_outputset()
metadata = dataset.metadata

# test MODEL
estimator = Estimator(create_model)
split = KFold(n_splits=n_splits)


res = estimator.learning_rate(inputset, outputset, split, epochs=epochs, batch_size=batch_size)


# jmeno python souboru jako string
modelname = (create_model.__module__).split('.')[1]


# estimator.save_prediction_to_file(inputset, metadata, 'data/predictions/' + modelname + '.csv')

# uloz model do souboru .h5
#estimator.save_model_to_file()





fig = plt.figure(figsize=size)
ax1 = fig.add_subplot(111)        
ax1.plot(range(10), res[:,0]
         , linestyle='-', lw=2)

ax1.set_xlabel('epocha')
ax1.set_ylabel(str(metric))
plt.show()

#    fig.savefig(filepath + '.png')

