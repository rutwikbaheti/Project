import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import VotingClassifier
from sklearn import model_selection
from sklearn.metrics import confusion_matrix
from sklearn. preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Reading training dataset
train = pd.read_csv("Training.csv")

# Reading testing dataset
test = pd.read_csv("Testing.csv")

# Training lables
X_train = train.drop(columns=['prognosis'])
# Training Targets
X_test = test.drop(columns=['prognosis'])
# Testing lables
y_train = train['prognosis']
# Testing Targets
y_test = test['prognosis']

sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

estimators = []
model1 = DecisionTreeClassifier(max_depth = 10)
estimators.append(('cart1', model1))
model2 = KNeighborsClassifier(n_neighbors = 9)
estimators.append(('knn1', model2))
model3 = GaussianNB()
estimators.append(('nbs1', model3))

ensemble = VotingClassifier(estimators,voting='hard')
ensemble.fit(X_train, y_train)
y_pred = ensemble.predict(X_test)

from sklearn.metrics import classification_report, confusion_matrix,accuracy_score
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
print(accuracy_score(y_test, y_pred))
