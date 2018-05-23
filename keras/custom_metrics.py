import keras.backend as backend
import numpy as np

def root_mean_squared_error(y_true, y_pred):
    return backend.sqrt(backend.mean(backend.square(y_pred - y_true), axis=-1)) 

def root_mean_squared_error_numpy(y_true, y_pred):
    return np.sqrt(np.mean(np.square(y_pred - y_true)))
