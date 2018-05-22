from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.metrics import mae
from keras.losses import categorical_crossentropy
import sys
sys.path.append('../')
from custom_metrics import root_mean_squared_error as rmse

def create_model():
    model = Sequential()
    model.add(Dense(20, activation='relu', input_dim=30))
    model.add(Dense(20, activation='relu'))
    model.add(Dense(12, activation='softmax'))
    model.compile(optimizer='adam', loss=categorical_crossentropy, metrics=[mae, rmse])
    return model

n_splits= 10
epochs= 10
batch_size= 100
