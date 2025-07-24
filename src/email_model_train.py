import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 1. Load preprocessed data
X_email, y_email = joblib.load('src/email_data.pkl')

# 2. Split into train/test sets (80/20 split)
X_train, X_test, y_train, y_test = train_test_split(X_email, y_email, test_size=0.2, random_state=42)

# 3. Model tuning with GridSearchCV
param_grid = {
    'alpha': [0.1, 0.5, 1.0]
}
clf = MultinomialNB()
grid = GridSearchCV(clf, param_grid, cv=3, scoring='f1', n_jobs=-1)
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
joblib.dump(best_clf, 'src/email_model.pkl') 