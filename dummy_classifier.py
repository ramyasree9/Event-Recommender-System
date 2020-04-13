from sklearn.dummy import DummyClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import fbeta_score
from sklearn.metrics import make_scorer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
import pandas as pd

dataPath = "./data/"
X_train = pd.read_csv(dataPath + 'X_train.csv')
X_test = pd.read_csv(dataPath + 'X_test.csv')
y_test = pd.read_csv(dataPath + 'y_test.csv')
y_train = pd.read_csv(dataPath + 'y_train.csv')

X_train.same_city = X_train.same_city.astype(int)
X_train.same_country = X_train.same_country.astype(int)
X_train.is_creator_friend = X_train.is_creator_friend.astype(int)

X_test.same_city = X_test.same_city.astype(int)
X_test.same_country = X_test.same_country.astype(int)
X_test.is_creator_friend = X_test.is_creator_friend.astype(int)

y_train = y_train.squeeze()
y_test = y_test.squeeze()

pipe =  DummyClassifier(random_state=0, strategy="constant", constant=1)


cross_scores = cross_val_score(pipe, X_train, y_train, cv=5)
print("Cross Validation Scores: ", cross_scores)

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
print("Accuracy: ", accuracy_score(y_test, y_pred))
print("Recall: ", recall_score(y_test, y_pred))
print("F0.5: ", fbeta_score(y_test, y_pred, beta = 0.5))
print("Precision: ", precision_score(y_test, y_pred))
print("F1: ", f1_score(y_test, y_pred))
print("Confusion matrix", confusion_matrix(y_test, y_pred))



