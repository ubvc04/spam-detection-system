# IBM Threat Detection Suite

Detect malicious URLs, spam SMS, and phishing emails using machine learning.

---

## 🚀 Features
- **Malicious URL Detection**: Classifies URLs as benign or malicious using feature engineering and Random Forest.
- **SMS Spam Detection**: Detects spam SMS using TF-IDF and Logistic Regression.
- **Phishing Email Detection**: Identifies phishing emails using TF-IDF and Naive Bayes.
- **Modern Web Interface**: FastAPI-powered web app with Bootstrap 5 styling for real-time predictions.
- **Command-Line Interface**: Run predictions and training from the terminal.
- **Extensible**: Modular code for easy feature addition and model tuning.

---

## 📊 Dataset Sources
- **Malicious URLs**: [Kaggle - Malicious and Benign URLs](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset)
- **Phishing Emails**: [Kaggle - Phishing Email Dataset](https://www.kaggle.com/datasets/charleshadi/phishing-emails)
- **SMS Spam**: [UCI - SMS Spam Collection](https://archive.ics.uci.edu/ml/datasets/sms+spam+collection)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```sh
git clone <your-repo-url>
cd IBM
```

### 2. Create and Activate Virtual Environment (Recommended)
#### Windows
```sh
python -m venv venv
venv\Scripts\activate
```
#### Linux/Mac
```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Download Datasets
Place the following files in the `datasets/` folder:
- `malicious_urls.csv`
- `phishing_emails.csv`
- `sms_spam.csv`

---

## 🛠️ How to Run

### CLI: Preprocessing & Training
```sh
python src/preprocessing.py
python src/url_model_train.py
python src/sms_model_train.py
python src/email_model_train.py
```

### CLI: Prediction
```sh
python src/predict.py
```

### Web App
```sh
uvicorn src.webapp:app --reload
```
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 💡 Example Usage

### CLI Example
```
$ python src/predict.py
Enter a URL to check if it is malicious (or press Enter to skip): http://badsite.com
Result: The URL is MALICIOUS.
Enter an SMS message to check if it is spam (or press Enter to skip): Free money!!!
Result: The SMS is SPAM.
Enter an email body to check if it is phishing (or press Enter to skip): Please update your account info at this link.
Result: The email is PHISHING.
```

### Web App Example
- Go to the web app, select a tab, enter your data, and get instant, color-coded results.

---

## 📦 Project Structure
```
IBM/
  datasets/
  models/
  reports/
  src/
    preprocessing.py
    url_model_train.py
    sms_model_train.py
    email_model_train.py
    predict.py
    webapp.py
    templates/
      home.html
  requirements.txt
  README.md
```

---

## 🤝 License
This project is for educational and research purposes only. Please respect the licenses of the original datasets. 