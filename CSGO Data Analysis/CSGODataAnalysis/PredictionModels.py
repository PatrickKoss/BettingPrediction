import pickle

import keras
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import Dense, Dropout
from keras.models import Sequential
from keras.optimizers import Adam
from sklearn import neighbors, svm
from sklearn.model_selection import train_test_split

# Make sure to always run these 4 lines because tensorflow is giving errors if not
config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.8))
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)


def build_models_machine_learning_all_matches_wins():
    # get training and testing data
    X_train, X_test, y_train, y_test = get_split_train_test_all_matches()

    clfSVM, clfKNeighbors = get_fitted_classifier(X_train, y_train)

    # get the confidence of the classifiers
    confidence_SVM = clfSVM.score(X_test, y_test)
    confidence_KNeighbors = clfKNeighbors.score(X_test, y_test)

    # SVM achieved 68.8% confidence and KNeighbors 59.4%
    print("SVM confidence all matches wins: ", confidence_SVM)
    print("KNeighbors confidence all matches wins: ", confidence_KNeighbors)

    # save the classifiers for future predictions
    pickle.dump(clfSVM, open("./PredictionModels/clfSVM_allMatchesWins.sav", "wb"))
    pickle.dump(clfKNeighbors, open("./PredictionModels/clfKNeighbors_allMatchesWins.sav", "wb"))


def build_models_machine_learning_best_of_3_wins():
    # get training and testing data
    X_train, X_test, y_train, y_test = get_split_train_test_best_of_3_wins()

    clfSVM, clfKNeighbors = get_fitted_classifier(X_train, y_train)

    # get the confidence of the classifiers
    confidence_SVM = clfSVM.score(X_test, y_test)
    confidence_KNeighbors = clfKNeighbors.score(X_test, y_test)

    # SVM achieved 71.6% confidence and KNeighbors 64.4%
    print("SVM confidence best of 3 wins: ", confidence_SVM)
    print("KNeighbors confidence best of 3 wins: ", confidence_KNeighbors)

    # save the classifiers for future predictions
    pickle.dump(clfSVM, open("./PredictionModels/clfSVM_bestOf3Wins.sav", "wb"))
    pickle.dump(clfKNeighbors, open("./PredictionModels/clfKNeighbors_bestOf3Wins.sav", "wb"))


def build_models_machine_learning_best_of_3_rounds():
    # get training and testing data
    X_train, X_test, y_train, y_test = get_split_train_test_best_of_3_rounds()

    clfSVM, clfKNeighbors = get_fitted_classifier(X_train, y_train)

    # get the confidence of the classifiers
    confidence_SVM = clfSVM.score(X_test, y_test)
    confidence_KNeighbors = clfKNeighbors.score(X_test, y_test)

    # SVM achieved 64.3% confidence and KNeighbors 58.7%
    print("SVM confidence best of 3 rounds: ", confidence_SVM)
    print("KNeighbors confidence best of 3 rounds: ", confidence_KNeighbors)

    # save the classifiers for future predictions
    pickle.dump(clfSVM, open("./PredictionModels/clfSVM_bestOf3Rounds.sav", "wb"))
    pickle.dump(clfKNeighbors, open("./PredictionModels/clfKNeighbors_bestOf3Rounds.sav", "wb"))


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
    model.save("./PredictionModels/NNModel_allMatchesWins_new.h5")


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

    # get training and testing data
    return train_test_split(X, y, test_size=0.2)


def get_split_train_test_best_of_3_wins():
    df = pd.read_csv("./Data/complete_matches_best_of_3.csv", index_col=False, dtype='float64')

    # all columns of our data frame are the features except the win that we want to predict
    X = np.array(df.drop(["Win", "Rounds_Played"], 1))
    y = np.array((df["Win"]))

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
    # build the model
    model = Sequential()
    model.add(Dense(80, activation='relu', input_shape=(int(np.shape(X_train)[1]),)))
    model.add(Dropout(20))
    model.add((Dense(40, activation='relu')))
    model.add(Dropout(20))
    model.add((Dense(20, activation='relu')))
    model.add(Dropout(20))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=Adam(lr=0.001),
                  metrics=['accuracy'])

    # fit the model
    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=1200, verbose=0)

    return model


def get_fitted_classifier(X_train, y_train):
    # define the classifiers
    clfSVM = svm.SVC(kernel='poly', degree=10, C=4)
    clfKNeighbors = neighbors.KNeighborsClassifier(n_neighbors=9, algorithm='auto', n_jobs=-1, weights='distance')

    # fit the classifiers
    clfSVM.fit(X_train, y_train)
    clfKNeighbors.fit(X_train, y_train)

    return clfSVM, clfKNeighbors


def test_prediction():
    model = keras.models.load_model("./PredictionModels/NNModel_allMatchesWins.h5")
    prediction = model.predict(np.array(
        [[0.72, 0.62, 0.74, 1.17, 78.2, 0.79, 0.67, 0.71, 1.10, 81.1, 0.69, 0.63, 0.73, 1.03, 73.4, 0.67, 0.62, 0.71,
          1.19, 76.4, 0.74, 0.69, 0.7, 1.10, 79.4, 0.71, 0.49, 0.71, 0.68, 1.08, 80.0, 0.71, 0.64, 0.69, 0.90, 65.5,
          0.63, 0.68, 0.68, 0.95, 77.7, 0.7, 0.71, 0.7, 0.99, 71.6, 0.64, 0.69, 0.7, 1.13, 78.8, 0.71]]))
    print(prediction)


if __name__ == "__main__":
    # build_models_machine_learning_all_matches_wins()
    # build_models_machine_learning_best_of_3_wins()
    # build_models_machine_learning_best_of_3_rounds()
    # build_models_deep_learning_all_matches_wins()
    build_models_deep_learning_best_of_3_wins()
    # build_models_deep_learning_best_of_3_rounds()
    # build_softmax_models()
    # test_prediction()