import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np

# 1. Load preprocessed data
X_sms, y_sms = joblib.load('src/sms_data.pkl')

# 2. Split into train/test sets (80/20 split)
X_train_df, X_test_df, y_train, y_test = train_test_split(X_sms, y_sms, test_size=0.2, random_state=42)

# 3. Vectorize text using TF-IDF
vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
X_train_tfidf = vectorizer.fit_transform(X_train_df['message'])
X_test_tfidf = vectorizer.transform(X_test_df['message'])

# Combine TF-IDF and extra features
extra_cols = ['msg_length', 'digit_count', 'link_count', 'excl_count', 'has_keyword']
from scipy.sparse import hstack, csr_matrix
X_train = hstack([X_train_tfidf, csr_matrix(X_train_df[extra_cols].values)])
X_test = hstack([X_test_tfidf, csr_matrix(X_test_df[extra_cols].values)])

# 4. Model tuning with GridSearchCV
param_grid = {
    'C': [0.1, 1, 10],
    'penalty': ['l2'],
    'solver': ['lbfgs']
}
clf = LogisticRegression(max_iter=1000, random_state=42)
grid = GridSearchCV(clf, param_grid, cv=3, scoring='f1', n_jobs=-1)
grid.fit(X_train, y_train)

print('Best parameters:', grid.best_params_)
print('Best CV F1-score:', grid.best_score_)

# 5. Evaluate best estimator
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

# 6. Save the best trained model and vectorizer
joblib.dump(best_clf, 'src/sms_model.pkl')
joblib.dump(vectorizer, 'src/sms_vectorizer.pkl') 