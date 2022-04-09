import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dropout
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline

# Reading training dataset
train = pd.read_csv("Training.csv")

# Reading testing dataset
test = pd.read_csv("Testing.csv")

X = train.drop(columns=['prognosis'])
y = test['prognosis']

from sklearn.preprocessing import LabelEncoder

encoder = LabelEncoder()
encoder.fit(y)
encoded_y = encoder.transform(y)
dummy_y = np_utils.to_categorical(encoded_y)

def baseline_model():
	# create model
  model = Sequential()
  model.add(Dense(60, activation='relu'))
  model.add(Dense(40, input_shape=(60,), activation='relu'))
  model.add(Dense(30, activation='softmax'))
	# Compile model
  model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
  return model

estimator = KerasClassifier(build_fn=baseline_model, epochs=5, batch_size=5, verbose=2)
kfold = KFold(n_splits=10, shuffle=True)
results = cross_val_score(estimator, X, dummy_y, cv=kfold)
print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

#dropout layers
def baseline_model():
	# create model
  model = Sequential()
  model.add(Dense(60, activation='relu'))
  model.add(Dropout(0.3))
  model.add(Dense(40, input_shape=(60,), activation='relu'))
  model.add(Dropout(0.3))
  model.add(Dense(30, activation='softmax'))
	# Compile model
  model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
  return model

estimator = KerasClassifier(build_fn=baseline_model, epochs=5, batch_size=5, verbose=2)
kfold = KFold(n_splits=10, shuffle=True)
results = cross_val_score(estimator, X, dummy_y, cv=kfold)
print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))
