import keras
import numpy as np
import pandas as pd
import pickle
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from sklearn import svm
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sys import platform
from sklearn.preprocessing import MinMaxScaler

# Make sure to always run these 4 lines because tensorflow is giving errors if not
config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.8))
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)
from datetime import datetime


def build_models_machine_learning_all_matches_wins():
    # get training and testing data
    X_train, X_test, y_train, y_test = get_split_train_test_all_matches()

    clfSVM = get_fitted_classifier(X_train, y_train)

    # get the confidence of the classifiers
    confidence_SVM = clfSVM.score(X_test, y_test)

    # SVM achieved 68.8%
    print("SVM confidence all matches wins: ", confidence_SVM)

    # save the classifiers for future predictions
    if platform == "linux" or platform == "linux2":
        pickle.dump(clfSVM, open("./PredictionModels/clfSVM_allMatchesWins_linux.sav", "wb"))
    if platform == "win32":
        pickle.dump(clfSVM, open("./PredictionModels/clfSVM_allMatchesWins.sav", "wb"))


def build_models_machine_learning_best_of_3_wins():
    # get training and testing data
    X_train, X_test, y_train, y_test = get_split_train_test_best_of_3_wins()

    clfSVM = get_fitted_classifier(X_train, y_train)

    # get the confidence of the classifiers
    confidence_SVM = clfSVM.score(X_test, y_test)

    # SVM achieved 71.6% confidence and KNeighbors 64.4%
    print("SVM confidence best of 3 wins: ", confidence_SVM)

    # save the classifiers for future predictions
    if platform == "linux" or platform == "linux2":
        pickle.dump(clfSVM, open("./PredictionModels/clfSVM_bestOf3Wins_linux.sav", "wb"))
    if platform == "win32":
        pickle.dump(clfSVM, open("./PredictionModels/clfSVM_bestOf3Wins.sav", "wb"))


def build_models_machine_learning_best_of_3_rounds():
    # get training and testing data
    X_train, X_test, y_train, y_test = get_split_train_test_best_of_3_rounds()

    clfSVM = get_fitted_classifier(X_train, y_train)

    # get the confidence of the classifiers
    confidence_SVM = clfSVM.score(X_test, y_test)

    # SVM achieved 64.3% confidence and KNeighbors 58.7%
    print("SVM confidence best of 3 rounds: ", confidence_SVM)

    # save the classifiers for future predictions
    if platform == "linux" or platform == "linux2":
        pickle.dump(clfSVM, open("./PredictionModels/clfSVM_bestOf3Rounds_linux.sav", "wb"))
    if platform == "win32":
        pickle.dump(clfSVM, open("./PredictionModels/clfSVM_bestOf3Rounds.sav", "wb"))


def build_models_deep_learning_all_matches_wins():
    # get training and testing data
    X_train, X_test, y_train, y_test = get_split_train_test_all_matches()

    model = get_fitted_nn_model(X_train, X_test, y_train, y_test)

    # get the score of the model
    score, acc = model.evaluate(X_test, y_test, verbose=0)

    # currently achieved a 69.2% accuracy
    print('Test score NN all wins:', score)
    print('Test accuracy NN all wins:', acc)

    # save the model
    if platform == "linux" or platform == "linux2":
        model.save("./PredictionModels/NNModel_allMatchesWins_linux.h5")
    if platform == "win32":
        model.save("./PredictionModels/NNModel_allMatchesWins.h5")


def build_models_deep_learning_best_of_3_wins():
    # get training and testing data
    X_train, X_test, y_train, y_test = get_split_train_test_best_of_3_wins()

    model = get_fitted_nn_model(X_train, X_test, y_train, y_test)

    # get the score of the model
    score, acc = model.evaluate(X_test, y_test, verbose=0)

    # currently achieved a 73.8% accuracy
    print('Test score NN best of 3 wins:', score)
    print('Test accuracy NN best of 3 wins:', acc)

    # save the model
    if platform == "linux" or platform == "linux2":
        model.save("./PredictionModels/NNModel_bestOf3Wins_linux.h5")
    if platform == "win32":
        model.save("./PredictionModels/NNModel_bestOf3Wins.h5")


def build_models_deep_learning_best_of_3_rounds():
    # get training and testing data
    X_train, X_test, y_train, y_test = get_split_train_test_best_of_3_rounds()

    model = get_fitted_nn_model(X_train, X_test, y_train, y_test)

    # get the score of the model
    score, acc = model.evaluate(X_test, y_test, verbose=0)

    # currently achieved a 65.4% accuracy
    print('Test score NN best of 3 rounds:', score)
    print('Test accuracy NN best of 3 rounds:', acc)

    # save the model
    if platform == "linux" or platform == "linux2":
        model.save("./PredictionModels/NNModel_bestOf3Rounds_linux.h5")
    if platform == "win32":
        model.save("./PredictionModels/NNModel_bestOf3Rounds.h5")


def get_split_train_test_all_matches():
    df = pd.read_csv("./Data/complete_matches.csv", index_col=False, dtype='float64')
    # df.drop(columns=["Team_1_Winning_Percentage", "Team_2_Winning_Percentage"], inplace=True)
    # for col in df.columns:
    #     if "_ADR" in col:
    #         df.drop(columns=[col], inplace=True)

    # all columns of our data frame are the features except the win that we want to predict
    X = np.array(df.drop(["Win"], 1))
    y = np.array((df["Win"]))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    print(X_test)
    np.save("X_test.npy", X_test)
    np.save("y_test.npy", y_test)
    print(np.load("X_test.npy"))
    print(np.load("X_test.npy") == X_test)

    # get training and testing data
    return X_train, X_test, y_train, y_test


def get_split_train_test_best_of_3_wins():
    df = pd.read_csv("./Data/complete_matches_best_of_3.csv", index_col=False, dtype='float64')

    # all columns of our data frame are the features except the win that we want to predict
    X = np.array(df.drop(["Win", "Rounds_Played"], 1))
    y = np.array((df["Win"]))

    # scale data
    # scaler = MinMaxScaler()
    # X = scaler.fit_transform(X)
    # print(X)

    # get training and testing data
    return train_test_split(X, y, test_size=0.2)


def get_split_train_test_best_of_3_rounds():
    df = pd.read_csv("./Data/complete_matches_best_of_3.csv", index_col=False, dtype='float64')

    # all columns of our data frame are the features except the win that we want to predict
    X = np.array(df.drop(["Win", "Rounds_Played"], 1))
    y = np.array((df["Rounds_Played"]))

    # get training and testing data
    return train_test_split(X, y, test_size=0.2)


def get_fitted_nn_model(X_train, X_test, y_train, y_test):
    # TODO make sure to tran with keras and not with tf.keras
    # build the model
    model = Sequential()
    model.add(Dense(80, activation='relu', input_shape=(int(np.shape(X_train)[1]),)))
    model.add(Dropout(0.2))
    model.add((Dense(40, activation='relu')))
    model.add(Dropout(0.2))
    model.add((Dense(20, activation='relu')))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=Adam(lr=0.001),
                  metrics=['accuracy'])

    log_dir = "logs/" + datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    # fit the model
    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=1200, verbose=0,
              callbacks=[tensorboard_callback])

    return model


def get_fitted_classifier(X_train, y_train):
    # define the classifiers
    clfSVM = svm.SVC(kernel='poly', degree=10, C=4)

    # fit the classifiers
    clfSVM.fit(X_train, y_train)

    return clfSVM


def test_prediction():
    model = keras.models.load_model("./PredictionModels/NNModel_allMatchesWins.h5")
    prediction = model.predict(np.array(
        [[0.72, 0.62, 0.74, 1.17, 78.2, 0.79, 0.67, 0.71, 1.10, 81.1, 0.69, 0.63, 0.73, 1.03, 73.4, 0.67, 0.62, 0.71,
          1.19, 76.4, 0.74, 0.69, 0.7, 1.10, 79.4, 0.71, 0.49, 0.71, 0.68, 1.08, 80.0, 0.71, 0.64, 0.69, 0.90, 65.5,
          0.63, 0.68, 0.68, 0.95, 77.7, 0.7, 0.71, 0.7, 0.99, 71.6, 0.64, 0.69, 0.7, 1.13, 78.8, 0.71]]))
    print(prediction)


def build_kfold_svm():
    df = pd.read_csv("./Data/complete_matches.csv", index_col=False, dtype='float64')

    X = np.array(df.drop(["Win"], 1))
    y = np.array((df["Win"]))

    kfold = KFold(n_splits=10, shuffle=True)

    fold_no = 1
    accurracy_per_fold = []

    for train, test in kfold.split(X, y):
        clfSVM = svm.SVC(kernel='poly', degree=10, C=4)
        clfSVM.fit(X[train], y[train])
        confidence_SVM = clfSVM.score(X[test], y[test])
        print(f"Confidence for fold {fold_no}: {confidence_SVM}")
        accurracy_per_fold.append(confidence_SVM)
        fold_no = fold_no + 1

    print("--------------------------------------------------")
    print(f"average confidence: {np.mean(accurracy_per_fold)}")


def variance_check():
    X_test = np.load("X_test.npy")
    y_test = np.load("y_test.npy")
    model = tf.keras.models.load_model("./PredictionModels/NNModel_allMatchesWins.h5")
    print(X_test.shape)
    print(y_test.shape)
    for sample in range(0, 10000, 300):
        sliced_test_x = X_test[sample:sample+300, :]
        sliced_test_y = y_test[sample:sample+300]
        score, acc = model.evaluate(sliced_test_x, sliced_test_y, verbose=0)
        print(acc)


if __name__ == "__main__":
    # build_models_machine_learning_all_matches_wins()
    # build_models_machine_learning_best_of_3_wins()
    # build_models_machine_learning_best_of_3_rounds()
    # build_models_deep_learning_all_matches_wins()
    # build_models_deep_learning_best_of_3_wins()
    # build_models_deep_learning_best_of_3_rounds()
    # test_prediction()
    # build_kfold_svm()
    variance_check()
