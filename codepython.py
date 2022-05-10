# -*- coding: utf-8 -*-
"""01_prod_manip2_lr_complete_tutorial_advertising.ipynb

## Collect data using pandas
"""

# Commented out IPython magic to ensure Python compatibility.
# modules nécessaires pour le notebook
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
##
import mlflow
import mlflow.sklearn


import logging
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)
# %matplotlib inline

# lire le fichier de données
#utiliser le param index_col: Column to use as the row labels of the DataFrame
df = pd.read_csv('Advertising.csv', index_col=0)


#utilisation d'une figure avec 3 plots aligné sur une ligne
#fig, axes = plt.subplots(1,3,sharey=False)
#df.plot(kind='scatter', x='TV', y='sales', ax=axes[0], figsize=(16,8))
#df.plot(kind='scatter', x='radio', y='sales', ax=axes[1], figsize=(16,8))
#df.plot(kind='scatter', x='newspaper', y='sales', ax=axes[2], figsize=(16,8))

"""On voit au niveau des graphes qu'il existe une certaine relation linéaire entre TV et Sales ainsi que radio et Sales"""

#meme chose mais avec seaborn
import seaborn as sns
sns.pairplot(df, x_vars=['TV','radio','newspaper'], y_vars='sales', size=7, aspect=0.7)
# savegarder comme artefact
plt.savefig('pairplot.png')
"""# Tracé des correlations entre les différents descripteurs et cible"""


sns.heatmap(data=df.corr().round(2), cmap='coolwarm', annot=True, annot_kws={"size":8})
plt.tight_layout()
plt.savefig('heatmap.png')
#plt.show()

"""On confirme qu'il n'y a pas vraiment de dépendance entre les descripteurs.

# Développement du modele linear regression
"""

from sklearn.linear_model import LinearRegression
cols_predicteurs = ['TV','radio','newspaper']
#predicteurs
X = df[cols_predicteurs]
y = df.sales

#Effectuer la séparation Training-Test
from sklearn.model_selection import train_test_split
 
X_train, X_test, y_train, y_test = train_test_split(X, y , test_size = 0.2)
#detail de chacun des sous-dataset
print (X_train.shape, y_train.shape)
print (X_test.shape, y_test.shape)

#estimation des coeeficients du modele lineaire
lm = LinearRegression()
lm.fit(X_train,y_train)
#Afficher les coefficients
print(lm.intercept_)
print(lm.coef_)

#Afficher l'equation
list(zip(cols_predicteurs, lm.coef_))

# proceder au test
y_pred = lm.predict(X_test)

#comparer les valeurs test et prédites
test_pred_df = pd.DataFrame( { 'Valeurs test': y_test,
                            'Valeurs prédites': np.round( y_pred, 2),
                            'residuels': y_test - y_pred } )
test_pred_df[0:10]

import pickle
from sklearn import metrics
# RMSE
print(np.sqrt(metrics.mean_squared_error(y_test, y_pred)))

#Calcul du R-squared
r2 = metrics.r2_score(y_test, y_pred)
print(r2)

"""# K-Fold Cross Validation"""

from sklearn.model_selection import cross_val_score
lm = LinearRegression()
lm.fit(X_train,y_train)
cv_scores = cross_val_score(lm, X_train, y_train, scoring='r2', cv=10)
print(cv_scores)
pickle.dump(lm,open("model.pkl","wb"))
#calcul du scores
print(np.round(np.mean(cv_scores), 2))

"""# Selectionner les meilleurs prédicteurs

* on utilise p-value
"""

from sklearn.feature_selection import SelectKBest, f_regression
model =SelectKBest(score_func = f_regression, k = 4)# tous les descripteurs pour k
resultats = model.fit(X_train, y_train)

print(resultats.scores_)

print(resultats.pvalues_)

#afficher pour 4 chiffres après la virgule
[ '{0:5.3f}'.format(p) for p in resultats.pvalues_]

"""un predicteur sera significatif si p-val est moins de 5% et la valeur F en devenant plus grande indique une plus grande importance

Par ordre de classement, on voit que c'est TV et radio qui sont de bons candidats pour le modele

# Modele avec seulement TV et radio
"""

cols_predicteurs = ['TV','radio']
#predicteurs
X = df[cols_predicteurs]
y = df.sales

#Effectuer la séparation Training-Test

 
X_train, X_test, y_train, y_test = train_test_split(X, y ,test_size = 0.2)
#detail de chacun des sous-dataset
print (X_train.shape, y_train.shape)
print (X_test.shape, y_test.shape)

#estimation des coeeficients du modele lineaire
lm = LinearRegression()
lm.fit(X_train,y_train)
#Afficher les coefficients
print(lm.intercept_)
print(lm.coef_)

#Afficher l'equation
list(zip(cols_predicteurs, lm.coef_))

# proceder au test
y_pred = lm.predict(X_test)

#comparer les valeurs test et prédites
test_pred_df = pd.DataFrame( { 'Valeurs test': y_test,
                            'Valeurs prédites': np.round( y_pred, 2),
                            'residuels': y_test - y_pred } )
print(test_pred_df[0:10])

import numpy as np
from sklearn import metrics
# RMSE
print(np.sqrt(metrics.mean_squared_error(y_test, y_pred)))

#Calcul du R-squared
r2 = metrics.r2_score(y_test, y_pred)
print(r2)

#avec cross-validation
from sklearn.model_selection import cross_val_score
lm = LinearRegression()
cv_scores = cross_val_score(lm, X_train, y_train, scoring='r2', cv=10)
print(cv_scores)
#calcul du scores
print(np.round(np.mean(cv_scores), 2))

with mlflow.start_run():
    mlflow.log_param("RMSE",r2)
    mlflow.log_param("CV_scores",cv_scores)

"""On voit que le score sous cross validation est legerement mieux qu'avec les 3 predicteurs"""

#Référence: The Elements of Statistical Learning - Hastie, Tibshirani and Friedman, voir https://web.stanford.edu/~hastie/ElemStatLearn/
