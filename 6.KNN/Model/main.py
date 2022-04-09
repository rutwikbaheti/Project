import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# Reading training dataset
train = pd.read_csv("Training.csv")

# Reading testing dataset
test = pd.read_csv("Testing.csv")

# Training lables
x_train = train.drop(columns=['prognosis'])
# Training Targets
x_test = test.drop(columns=['prognosis'])
# Testing lables
y_train = train['prognosis']
# Testing Targets
y_test = test['prognosis']

# Model Training
classifier = KNeighborsClassifier(n_neighbors=8)
classifier.fit(x_train,y_train)

# Model Prediction
y_pred = classifier.predict(x_test)
print(accuracy_score(y_test, y_pred))

# New sample prediction
x_new = np.array([0,0,0,0,0,1,1,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1,1,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
x_new = x_new.reshape(1,-1)
y_new = classifier.predict(x_new)
print(y_new)
