import joblib
import os
import re
import pandas as pd
from pathlib import Path

class MLSecurityService:
    def __init__(self):
        # Get the path to the src directory where models are stored
        base_dir = Path(__file__).resolve().parent.parent
        src_dir = base_dir / 'src'
        
        # Load models and vectorizers
        self.url_model = joblib.load(src_dir / 'url_model.pkl')
        self.sms_model = joblib.load(src_dir / 'sms_model.pkl')
        self.sms_vectorizer = joblib.load(src_dir / 'sms_vectorizer.pkl')
        self.email_model = joblib.load(src_dir / 'email_model.pkl')
        self.email_vectorizer = joblib.load(src_dir / 'email_vectorizer.pkl')
    
    def extract_url_features(self, url):
        """Extract features for URL as in preprocessing."""
        import tldextract
        
        def has_https(url):
            return int(url.lower().startswith('https'))
        def num_dots(url):
            return url.count('.')
        def has_suspicious_chars(url):
            return int(bool(re.search(r'[@\-]', url)))
        
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
        
        # Basic features (exactly as in preprocessing)
        basic_features = pd.DataFrame({
            'url_length': [len(url)],
            'num_dots': [num_dots(url)],
            'has_https': [has_https(url)],
            'has_suspicious_chars': [has_suspicious_chars(url)],
        })
        
        # Additional features (exactly as in preprocessing)
        additional_features = extract_url_additional_features(url)
        additional_features_df = pd.DataFrame([additional_features])
        
        # Combine exactly as in preprocessing
        combined_features = pd.concat([basic_features, additional_features_df], axis=1)
        
        return combined_features
    
    def predict_url(self, url):
        """Predict if a URL is malicious."""
        try:
            url_features = self.extract_url_features(url)
            prediction = self.url_model.predict(url_features)[0]
            
            # Get confidence score
            try:
                confidence_proba = self.url_model.predict_proba(url_features)[0]
                confidence_score = max(confidence_proba) * 100
            except:
                confidence_score = 85.0  # Default confidence if predict_proba not available
            
            return {
                'is_malicious': bool(prediction),
                'confidence_score': confidence_score,
                'result': 'MALICIOUS' if prediction == 1 else 'SAFE'
            }
        except Exception as e:
            return {
                'error': str(e),
                'result': 'ERROR'
            }
    
    def extract_sms_features(self, sms_text):
        """Extract features for SMS as in preprocessing."""
        import re
        import scipy.sparse
        
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
        
        # Get TF-IDF features
        tfidf_features = self.sms_vectorizer.transform([sms_text])
        
        # Get extra features
        extra_features = extract_text_features(sms_text)
        extra_features_matrix = scipy.sparse.csr_matrix([[extra_features['msg_length'], 
                                                        extra_features['digit_count'], 
                                                        extra_features['link_count'], 
                                                        extra_features['excl_count'], 
                                                        extra_features['has_keyword']]])
        
        # Combine TF-IDF and extra features (same as training)
        combined_features = scipy.sparse.hstack([tfidf_features, extra_features_matrix])
        
        return combined_features
    
    def predict_sms(self, sms_text):
        """Predict if an SMS is spam."""
        try:
            sms_features = self.extract_sms_features(sms_text)
            prediction = self.sms_model.predict(sms_features)[0]
            
            # Get confidence score
            try:
                confidence_proba = self.sms_model.predict_proba(sms_features)[0]
                confidence_score = max(confidence_proba) * 100
            except:
                confidence_score = 85.0  # Default confidence if predict_proba not available
            
            return {
                'is_spam': bool(prediction),
                'confidence_score': confidence_score,
                'result': 'SPAM' if prediction == 1 else 'NOT SPAM'
            }
        except Exception as e:
            return {
                'error': str(e),
                'result': 'ERROR'
            }
    
    def extract_email_features(self, email_text):
        """Extract features for email as in preprocessing."""
        import re
        from bs4 import BeautifulSoup
        import string
        import scipy.sparse
        
        # Clean text (same as preprocessing)
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
        
        # Clean the email text
        cleaned_text = clean_text(email_text)
        
        # Get TF-IDF features
        tfidf_features = self.email_vectorizer.transform([cleaned_text])
        
        # Get extra features
        extra_features = extract_text_features(cleaned_text)
        extra_features_matrix = scipy.sparse.csr_matrix([[extra_features['msg_length'], 
                                                        extra_features['digit_count'], 
                                                        extra_features['link_count'], 
                                                        extra_features['excl_count'], 
                                                        extra_features['has_keyword']]])
        
        # Combine TF-IDF and extra features (same as training)
        combined_features = scipy.sparse.hstack([tfidf_features, extra_features_matrix])
        
        return combined_features
    
    def predict_email(self, email_text):
        """Predict if an email is phishing."""
        try:
            email_features = self.extract_email_features(email_text)
            prediction = self.email_model.predict(email_features)[0]
            
            # Get confidence score
            try:
                confidence_proba = self.email_model.predict_proba(email_features)[0]
                confidence_score = max(confidence_proba) * 100
            except:
                confidence_score = 85.0  # Default confidence if predict_proba not available
            
            return {
                'is_phishing': bool(prediction),
                'confidence_score': confidence_score,
                'result': 'PHISHING' if prediction == 1 else 'NOT PHISHING'
            }
        except Exception as e:
            return {
                'error': str(e),
                'result': 'ERROR'
            }

# Global instance to be used across the application
ml_service = MLSecurityService() 