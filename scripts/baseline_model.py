# baseline model python file

import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_text
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt


from evaluation import plot_cf, get_f1_score, get_precision_score

def load_data():
    return pd.read_csv("data/student_depression_dataset.csv")

def train_baseline_model():
    df = load_data()

    # preprocess data and drop certain columns that may affect accuracy of model
    drop_cols = ['id', 'Work Pressure', 'Job Satisfaction', 'Gender', 'City', 'Profession']
    df = df.drop(columns=drop_cols)
    print(df.columns)

    # encode categorical variables
    df_encoded = pd.get_dummies(df)

    # variable X contains all non-dropped columns except for 'Depression'
    X = df_encoded.drop("Depression", axis=1)

    # y variable contains only the 'Depression' column to serve as the target label the model tries to predict
    y = df_encoded["Depression"]

    # using train_test_split from sklearn.model_selection to split dataset into training/testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state = 99)

    # define TreeClassifier model
    clf = DecisionTreeClassifier(random_state=1)

    # train the model
    clf.fit(X_train, y_train)

    # make predictions
    y_pred = clf.predict(X_test)

    # prints accuracy score of actual vs. predicted
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy}')
    
    # prints F1 score
    f1 = get_f1_score(y_test, y_pred)
    print(f'F1 score: {f1}')
    
    # prints Precision score
    precision = get_precision_score(y_test, y_pred)
    print(f'Precision score: {precision}')

    # use randomized search cv to enhance model
    print("\n=== RUNNING FAST RANDOMIZED SEARCH ===")
    
    # define random parameter space
    param_distributions = {
        'max_depth': [3, 5, 7, 9, 11, 13, 15, None],
        'min_samples_leaf': [1, 2, 5, 10, 15],
        'min_samples_split': [2, 5, 10, 15, 20],
        'criterion': ["entropy", "gini"]
    }
    
    # utilise RandomizedSearchCV
    random_search = RandomizedSearchCV(
        estimator=clf, 
        param_distributions=param_distributions,
        n_iter= 150,  # only try 150 random combinations
        cv=5,       # use 3-fold cv instead of 5
        n_jobs=-1,  # use all cpu cores
        verbose=1,
        random_state=42
    )
    
    random_search.fit(X_train, y_train)
    
    print("Random search best accuracy:", random_search.best_score_)
    print("Random search best parameters:", random_search.best_params_)
    
    # use best model for predictions
    best_model = random_search.best_estimator_
    y_pred_best = best_model.predict(X_test)
    best_accuracy = accuracy_score(y_test, y_pred_best)
    print(f"Best model test accuracy: {best_accuracy}")
    best_f1 = get_f1_score(y_test, y_pred_best)
    print(f"Best model F1 score: {best_f1}")
    best_precision = get_precision_score(y_test, y_pred_best)
    print(f"Best model Precision score: {best_precision}")

    # fix: X_train may be a numpy array or dataframe
    if hasattr(X_train, "columns"):
        feature_names = X_train.columns.tolist()
    else:
        feature_names = [f"feature_{i}" for i in range(X_train.shape[1])]

    tree_rules = export_text(best_model, feature_names=feature_names)
    print(tree_rules)

    return y_test, y_pred_best

def random_forest():
    print("Starting Random Forest")

    df = pd.read_csv("data/student_depression_dataset.csv", encoding="latin-1")

    # Encode categorical variables
    df = pd.get_dummies(df)

    # Drop rows with missing values (optional but often necessary)
    df = df.dropna()

    X = df.drop(columns=['Depression'])
    y = df['Depression']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=17)
    
    rf = RandomForestClassifier()
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)

    importances = rf.feature_importances_
    feature_names = X_train.columns

    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    })

    # Sort by importance (descending)
    importance_df = importance_df.sort_values(by='Importance', ascending=False)
    print(importance_df)

    # print(y_pred)

    # print("Accuracy of Random Forest 1: " + str(rf.score(X_test, y_test)))
    print("Accuracy of Random Forest 1 (all features): " + str(accuracy_score(y_test, y_pred)))
    print("F1 Score of Random Forest 1 (all features): " + str(f1_score(y_test, y_pred)))

    #########################################################
    
    search = RandomizedSearchCV(
        RandomForestClassifier(random_state=42),
        {
            'n_estimators': [100, 200],
            'max_depth': [10, 20, None],
            'max_features': ['sqrt'],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        },
        n_iter=10,
        scoring='f1_weighted',
        cv=3,
        n_jobs=-1
    )
    print(search.get_params())
    search.fit(X_train, y_train)
    model = search.best_estimator_

    y_pred_best = model.predict(X_test)

    print("Accuracy of Random Forest 2 (best model): " + str(accuracy_score(y_test, y_pred_best)))
    print("F1 Score of Random Forest 2 (best model): " + str(f1_score(y_test, y_pred_best)))

    return y_test, y_pred_best


if __name__ == "__main__":
    y_test, y_pred = train_baseline_model()

    labels = ['Not Depressed', 'Depressed']
    plot_cf(y_test, y_pred, labels)

    print("Random Forest")
    y_test, y_pred = random_forest()
    plot_cf(y_test, y_pred, labels)


# resources used as guidance
# - https://www.geeksforgeeks.org/machine-learning/building-and-implementing-decision-tree-classifiers-with-scikit-learn-a-comprehensive-guide/
# - https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
# - https://www.geeksforgeeks.org/pandas/python-pandas-get_dummies-method/ 
# - https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html
# - https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html
# - https://www.geeksforgeeks.org/machine-learning/comparing-randomized-search-and-grid-search-for-hyperparameter-estimation-in-scikit-learn/
# - https://www.analyticsvidhya.com/blog/2022/11/hyperparameter-tuning-using-randomized-search/
# - https://www.geeksforgeeks.org/machine-learning/random-forest-algorithm-in-machine-learning/
# - https://www.youtube.com/watch?v=_QuGM_FW9eo