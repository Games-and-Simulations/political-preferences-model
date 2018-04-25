from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.metrics import mae


def create_model(neurons, layers, first):
    model = Sequential()
    model.add(Dense(neurons, activation='relu', input_dim=30))
    for i in range(layers):
        model.add(Dropout(0.25))
        model.add(Dense(neurons, activation='relu'))
    model.add(Dense(12, activation='softmax'))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=[mae])
    return model

n_splits = 10
epochs = 50
batch_size = 50
