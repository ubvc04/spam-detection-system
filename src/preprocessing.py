import pandas as pd
import os
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import string
from bs4 import BeautifulSoup
import tldextract

# Get base directory (IBM folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, 'datasets')

# Paths to datasets
DATASETS = {
    'malicious_urls': os.path.join(DATASETS_DIR, 'malicious_urls.csv'),
    'phishing_emails': os.path.join(DATASETS_DIR, 'phishing_emails.csv'),
    'sms_spam': os.path.join(DATASETS_DIR, 'sms_spam.csv'),
}

def explore_dataset(name, path):
    print(f'\n===== {name} =====')
    print(f'Attempting to load from: {path}')  # Print the full path
    try:
        try:
            df = pd.read_csv(path, encoding='utf-8')
        except UnicodeDecodeError:
            print('UTF-8 decode failed, trying latin1 encoding...')
            df = pd.read_csv(path, encoding='latin1')
        print('First 5 rows:')
        print(df.head())
        print(f'Shape: {df.shape}')
        print('Missing values per column:')
        print(df.isnull().sum())
    except Exception as e:
        print(f'Error loading {name}: {e}')

def extract_url_additional_features(url):
    # Special characters
    specials = ['/', '=', '?', '%', '&', ':', '_', '~']
    special_counts = {f'count_{c}': url.count(c) for c in specials}
    # IP address presence
    ip_pattern = r'(\d{1,3}\.){3}\d{1,3}'
    has_ip = int(bool(re.search(ip_pattern, url)))
    # Domain length
    ext = tldextract.extract(url)
    domain_len = len(ext.domain)
    # Shortening service
    shorteners = ['bit.ly', 'goo.gl', 'tinyurl', 'ow.ly', 't.co', 'is.gd', 'buff.ly', 'adf.ly']
    is_shortened = int(any(s in url for s in shorteners))
    # Suspicious keywords
    keywords = ['login', 'secure', 'update', 'verify', 'account', 'bank', 'free', 'bonus']
    has_keyword = int(any(k in url.lower() for k in keywords))
    # Digits and uppercase
    digit_count = sum(c.isdigit() for c in url)
    upper_count = sum(c.isupper() for c in url)
    # Suspicious TLD
    suspicious_tlds = ['xyz', 'top', 'club', 'online', 'site', 'win']
    tld = ext.suffix
    is_suspicious_tld = int(tld in suspicious_tlds)
    features = {
        **special_counts,
        'has_ip': has_ip,
        'domain_length': domain_len,
        'is_shortened': is_shortened,
        'has_keyword': has_keyword,
        'digit_count': digit_count,
        'upper_count': upper_count,
        'is_suspicious_tld': is_suspicious_tld
    }
    return features

def preprocess_malicious_urls():
    """
    Enhanced: Extract more features for ML from malicious_urls.csv
    """
    path = DATASETS['malicious_urls']
    df = pd.read_csv(path, encoding='utf-8')
    def has_https(url):
        return int(url.lower().startswith('https'))
    def num_dots(url):
        return url.count('.')
    def has_suspicious_chars(url):
        return int(bool(re.search(r'[@\-]', url)))
    # Basic features
    X_url = pd.DataFrame({
        'url_length': df['url'].astype(str).apply(len),
        'num_dots': df['url'].astype(str).apply(num_dots),
        'has_https': df['url'].astype(str).apply(has_https),
        'has_suspicious_chars': df['url'].astype(str).apply(has_suspicious_chars),
    })
    # Additional features
    add_feats = df['url'].astype(str).apply(extract_url_additional_features)
    add_feats_df = pd.DataFrame(list(add_feats))
    X_url = pd.concat([X_url, add_feats_df], axis=1)
    y_url = (df['type'] != 'benign').astype(int)
    out_path = os.path.join(os.path.dirname(__file__), 'url_data.pkl')
    joblib.dump((X_url, y_url), out_path)
    return X_url, y_url

# --- SMS/Email extra features ---
def extract_text_features(text):
    text = str(text)
    features = {
        'msg_length': len(text),
        'digit_count': sum(c.isdigit() for c in text),
        'link_count': len(re.findall(r'http[s]?://', text)),
        'excl_count': text.count('!'),
        'has_keyword': int(any(k in text.lower() for k in ['free', 'win', 'urgent', 'prize', 'account', 'click', 'verify', 'bank'])),
    }
    return features

def preprocess_sms_spam():
    path = DATASETS['sms_spam']
    df = pd.read_csv(path, encoding='latin1')
    sms_spam = df[['v1', 'v2']].copy()
    sms_spam.columns = ['label', 'message']
    sms_spam['label'] = sms_spam['label'].map({'ham': 0, 'spam': 1})
    # Extra features
    extra_feats = sms_spam['message'].apply(extract_text_features)
    extra_feats_df = pd.DataFrame(list(extra_feats))
    X_sms = pd.DataFrame({'message': sms_spam['message']})
    X_sms = pd.concat([X_sms, extra_feats_df], axis=1)
    y_sms = sms_spam['label']
    out_path = os.path.join(os.path.dirname(__file__), 'sms_data.pkl')
    joblib.dump((X_sms, y_sms), out_path)
    return X_sms, y_sms

def clean_text(text):
    # Remove HTML tags
    text = BeautifulSoup(str(text), 'html.parser').get_text()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_phishing_emails():
    path = DATASETS['phishing_emails']
    df = pd.read_csv(path, encoding='utf-8')
    df['body_clean'] = df['body'].apply(clean_text)
    # Extra features
    extra_feats = df['body_clean'].apply(extract_text_features)
    extra_feats_df = pd.DataFrame(list(extra_feats))
    # TF-IDF vectorization
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    X_tfidf = tfidf.fit_transform(df['body_clean'])
    # Combine TF-IDF and extra features
    import scipy.sparse
    X_email = scipy.sparse.hstack([X_tfidf, scipy.sparse.csr_matrix(extra_feats_df.values)])
    y_email = df['label']
    out_path = os.path.join(os.path.dirname(__file__), 'email_data.pkl')
    joblib.dump((X_email, y_email), out_path)
    # Save the vectorizer
    vectorizer_path = os.path.join(os.path.dirname(__file__), 'email_vectorizer.pkl')
    joblib.dump(tfidf, vectorizer_path)
    return X_email, y_email

if __name__ == '__main__':
    for name, path in DATASETS.items():
        explore_dataset(name, path)
    X_url, y_url = preprocess_malicious_urls()
    print(X_url.head())
    print(y_url.head())
    X_sms, y_sms = preprocess_sms_spam()
    print(X_sms.head())
    print(y_sms.head())
    X_email, y_email = preprocess_phishing_emails()
    print(X_email.shape)
    print(y_email.head())
