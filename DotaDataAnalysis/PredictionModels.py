import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn import svm
import pickle

# Make sure to always run these 4 lines because tensorflow is giving errors if not
config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.8))
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)


def create_models():
    X_train_win, X_test_win, y_train_win, y_test_win = create_split_train_test_win()

    # get models
    model_win = get_model_sigmoid(X_train_win)

    # fit the models
    model_win.fit(X_train_win, y_train_win, validation_data=(X_test_win, y_test_win), epochs=40, verbose=0)

    # get the score of the models
    _, acc_win = model_win.evaluate(X_test_win, y_test_win, verbose=0)

    # currently achieved a 69% accuracy
    print('Test accuracy NN wins:', acc_win)

    # save the model
    model_win.save("./PredictionModels/DotaWinNN.h5")


def create_svm():
    X_train_win, X_test_win, y_train_win, y_test_win = create_split_train_test_win()
    clf_svm = svm.SVC(kernel='poly', degree=10, C=4)
    clf_svm.fit(X_train_win, y_train_win)
    confidence_svm = clf_svm.score(X_test_win, y_test_win)
    print("SVM confidence win: ", confidence_svm)
    pickle.dump(clf_svm, open("./PredictionModels/clfSVM_win.sav", "wb"))


def create_split_train_test_win():
    # df = pd.read_csv("./Data/completeMatches.csv", index_col=False, dtype='float64')
    df = pd.read_csv("./Data/completeMatchesNew.csv", index_col=False, dtype='float64')
    df.dropna(inplace=True)

    # all columns of our data frame are the features except the win that we want to predict
    # X = np.array(df.drop(["Radiant_Score", "Dire_Score", "Win", "Duration"], 1))
    X = np.array(df.drop(["Radiant_Score", "Dire_Score", "Win"], 1))
    y = np.array((df["Win"]))
    min_max_scaler = preprocessing.MinMaxScaler()
    X = min_max_scaler.fit_transform(X)

    # get training and testing data
    return train_test_split(X, y, test_size=0.15)


def create_split_train_test_duration():
    df = pd.read_csv("./Data/completeMatches.csv", index_col=False, dtype='float64')

    # all columns of our data frame are the features except the win that we want to predict
    X = np.array(df.drop(["Radiant_Score", "Dire_Score", "Win", "Duration"], 1))
    y = np.array((df["Duration"]))

    # get training and testing data
    return train_test_split(X, y, test_size=0.1)


def create_split_train_test_radiant_score():
    df = pd.read_csv("./Data/completeMatches.csv", index_col=False, dtype='float64')

    # all columns of our data frame are the features except the win that we want to predict
    X = np.array(df.drop(["Radiant_Score", "Dire_Score", "Win", "Duration"], 1))
    y = np.array((df["Radiant_Score"]))

    # get training and testing data
    return train_test_split(X, y, test_size=0.2)


def create_split_train_test_dire_score():
    df = pd.read_csv("./Data/completeMatches.csv", index_col=False, dtype='float64')

    # all columns of our data frame are the features except the win that we want to predict
    X = np.array(df.drop(["Radiant_Score", "Dire_Score", "Win", "Duration"], 1))
    y = np.array((df["Dire_Score"]))

    # get training and testing data
    return train_test_split(X, y, test_size=0.2)


def get_model_sigmoid(X):
    model = Sequential()
    model.add(Dense(32, activation='relu', input_shape=(int(np.shape(X)[1]),)))
    model.add((Dense(24, activation='relu')))
    model.add((Dense(16, activation='relu')))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=Adam(lr=0.001),
                  metrics=['accuracy'])
    return model


def get_model_mse(X):
    model = Sequential()
    model.add(Dense(148, activation='relu', input_shape=(int(np.shape(X)[1]),)))
    model.add((Dense(92, activation='relu')))
    model.add((Dense(32, activation='relu')))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001),
                  metrics=['accuracy'])
    return model


if __name__ == "__main__":
    create_models()
    # create_svm()
