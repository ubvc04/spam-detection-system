import joblib
import os
import re
import pandas as pd

# For colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA = True
except ImportError:
    COLORAMA = False

# Load models and vectorizers
url_model = joblib.load(os.path.join('src', 'url_model.pkl'))
sms_model = joblib.load(os.path.join('src', 'sms_model.pkl'))
sms_vectorizer = joblib.load(os.path.join('src', 'sms_vectorizer.pkl'))
email_model = joblib.load(os.path.join('src', 'email_model.pkl'))
email_vectorizer = joblib.load(os.path.join('src', 'email_vectorizer.pkl'))

def print_colored(text, color):
    if COLORAMA:
        print(color + text + Style.RESET_ALL)
    else:
        print(text)

def extract_url_features(url):
    """Extract features for URL as in preprocessing."""
    def has_https(url):
        return int(url.lower().startswith('https'))
    def num_dots(url):
        return url.count('.')
    def has_suspicious_chars(url):
        return int(bool(re.search(r'[@\-]', url)))
    return pd.DataFrame({
        'url_length': [len(url)],
        'num_dots': [num_dots(url)],
        'has_https': [has_https(url)],
        'has_suspicious_chars': [has_suspicious_chars(url)],
    })

# 2. Malicious URL prediction
url_input = input('Enter a URL to check if it is malicious (or press Enter to skip): ').strip()
if url_input and url_input.lower() != 'skip':
    url_features = extract_url_features(url_input)
    url_pred = url_model.predict(url_features)[0]
    if url_pred == 1:
        print_colored("Result: The URL is MALICIOUS.", Fore.RED)
    else:
        print_colored("Result: The URL is BENIGN.", Fore.GREEN)
else:
    print("URL check skipped.")

# 3. SMS spam prediction
sms_input = input('Enter an SMS message to check if it is spam (or press Enter to skip): ').strip()
if sms_input and sms_input.lower() != 'skip':
    sms_features = sms_vectorizer.transform([sms_input])
    sms_pred = sms_model.predict(sms_features)[0]
    if sms_pred == 1:
        print_colored("Result: The SMS is SPAM.", Fore.RED)
    else:
        print_colored("Result: The SMS is NOT SPAM.", Fore.GREEN)
else:
    print("SMS check skipped.")

# 4. Phishing email prediction
email_input = input('Enter an email body to check if it is phishing (or press Enter to skip): ').strip()
if email_input and email_input.lower() != 'skip':
    email_features = email_vectorizer.transform([email_input])
    email_pred = email_model.predict(email_features)[0]
    if email_pred == 1:
        print_colored("Result: The email is PHISHING.", Fore.RED)
    else:
        print_colored("Result: The email is NOT PHISHING.", Fore.GREEN)
else:
    print("Email check skipped.") 