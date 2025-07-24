import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 1. Load preprocessed data
X_url, y_url = joblib.load('src/url_data.pkl')

# SAMPLE for fast testing (remove or increase n for full run)
X_url = X_url.sample(n=3000, random_state=42)
y_url = y_url.loc[X_url.index]

# 2. Split into train/test sets (80/20 split)
X_train, X_test, y_train, y_test = train_test_split(X_url, y_url, test_size=0.2, random_state=42)

# 3. Model tuning with GridSearchCV (smaller grid, fewer folds, single core)
param_grid = {
    'n_estimators': [100],
    'max_depth': [None, 10],
    'min_samples_split': [2]
}
clf = RandomForestClassifier(random_state=42)
grid = GridSearchCV(clf, param_grid, cv=2, scoring='f1', n_jobs=1)
grid.fit(X_train, y_train)

print('Best parameters:', grid.best_params_)
print('Best CV F1-score:', grid.best_score_)

# 4. Evaluate best estimator
best_clf = grid.best_estimator_
y_pred = best_clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f'Accuracy:  {accuracy:.4f}')
print(f'Precision: {precision:.4f}')
print(f'Recall:    {recall:.4f}')
print(f'F1-score:  {f1:.4f}')

# 5. Save the best trained model
joblib.dump(best_clf, 'src/url_model.pkl') 