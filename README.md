# 🛡️ ML Security Detection Platform

A comprehensive Django-based machine learning platform for detecting malicious URLs, spam SMS, and phishing emails with advanced threat intelligence and analytics.

---

## 🚀 Features

### Core Detection Capabilities
- **🔗 Malicious URL Detection**: Advanced URL analysis using feature engineering and Random Forest classification
- **📱 SMS Spam Detection**: TF-IDF and Logistic Regression-based spam detection
- **📧 Phishing Email Detection**: Naive Bayes classification for email phishing detection
- **📊 Real-time Analytics**: Live prediction history and threat intelligence dashboard

### Advanced Features
- **🎯 Enhanced Threat Intelligence**: Risk levels, threat categories, and domain reputation analysis
- **📈 Comprehensive Dashboard**: Analytics, charts, and detailed threat insights
- **🔄 Batch Processing**: Support for bulk file processing with background tasks
- **🔍 Domain Analysis**: SSL validation, geographic location, and ISP information
- **📸 URL Screenshots**: Visual verification of suspicious URLs
- **📝 Audit Logging**: Complete activity tracking and compliance logging
- **🌙 Dark Mode**: Modern UI with dark/light theme support

### Technical Features
- **⚡ Django REST Framework**: Robust API endpoints for all detection services
- **🔄 Celery Integration**: Background task processing and scheduled operations
- **📊 Advanced Analytics**: Threat pattern analysis and risk scoring
- **🔒 Security Features**: Rate limiting, CORS protection, and input validation

---

## 📊 Dataset Sources
- **Malicious URLs**: [Kaggle - Malicious and Benign URLs](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset)
- **Phishing Emails**: [Kaggle - Phishing Email Dataset](https://www.kaggle.com/datasets/charleshadi/phishing-emails)
- **SMS Spam**: [UCI - SMS Spam Collection](https://archive.ics.uci.edu/ml/datasets/sms+spam+collection)

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- Redis (for Celery background tasks)
- Git

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd IBM
```

### 2. Create and Activate Virtual Environment
#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install basic requirements
pip install -r requirements.txt

# For enhanced features (optional)
pip install -r requirements/enhanced_requirements.txt
```

### 4. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create initial data (threat categories, risk levels)
python manage.py create_initial_data

# Create superuser (optional)
python manage.py createsuperuser
```

### 5. Start Redis (Required for Celery)
```bash
# Windows (using WSL or Docker)
redis-server

# Linux/Mac
brew install redis  # macOS
sudo systemctl start redis  # Linux
```

### 6. Start the Application
```bash
# Start Django development server
python manage.py runserver

# Start Celery worker (in separate terminal)
celery -A ml_security_detector worker --loglevel=info

# Start Celery beat (in separate terminal)
celery -A ml_security_detector beat --loglevel=info
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🛠️ Usage

### Web Interface
1. **Home Page**: Three-tab interface for URL, SMS, and Email detection
2. **Dashboard**: Enhanced analytics with threat intelligence and risk scoring
3. **Admin Panel**: Complete management interface at `/admin/`

### API Endpoints
- `POST /predict/url/` - URL malicious detection
- `POST /predict/sms/` - SMS spam detection  
- `POST /predict/email/` - Email phishing detection
- `GET /dashboard/` - Analytics dashboard
- `POST /clear-history/` - Clear prediction history

### Command Line Interface
```bash
# URL prediction
python src/predict.py

# Train models (if needed)
python src/url_model_train.py
python src/sms_model_train.py
python src/email_model_train.py
```

---

## 📁 Project Structure
```
IBM/
├── ml_security_detector/          # Django project settings
│   ├── settings.py               # Main configuration
│   ├── urls.py                   # URL routing
│   └── celery.py                 # Celery configuration
├── detector/                      # Main Django app
│   ├── models.py                 # Database models
│   ├── views.py                  # View logic
│   ├── urls.py                   # App URL patterns
│   ├── ml_service.py             # ML prediction service
│   ├── admin.py                  # Admin interface
│   ├── tasks/                    # Celery background tasks
│   └── services/                 # Business logic services
├── src/                          # ML models and training
│   ├── *.pkl                     # Trained models
│   ├── *_train.py                # Model training scripts
│   └── predict.py                # CLI prediction tool
├── templates/                    # HTML templates
│   └── detector/
│       ├── home.html             # Main interface
│       ├── dashboard.html        # Analytics dashboard
│       └── enhanced_dashboard.html
├── static/                       # Static files (CSS, JS, images)
├── media/                        # User uploads and screenshots
├── logs/                         # Application logs
├── requirements/                 # Dependency files
└── manage.py                     # Django management script
```

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

### Celery Configuration
The platform uses Celery for background tasks:
- **Cleanup Tasks**: Automatic cleanup of old predictions and logs
- **Threat Intelligence**: Periodic updates of threat intelligence data
- **Batch Processing**: Background processing of bulk uploads

---

## 📊 Models & Performance

### Machine Learning Models
- **URL Detection**: Random Forest with feature engineering (95%+ accuracy)
- **SMS Detection**: Logistic Regression with TF-IDF (98%+ accuracy)
- **Email Detection**: Naive Bayes with text preprocessing (94%+ accuracy)

### Features Extracted
- **URLs**: Length, special characters, domain analysis, SSL status
- **SMS**: Text length, keyword presence, link detection
- **Emails**: Content analysis, HTML parsing, threat indicators

---

## 🔒 Security Features

- **Input Validation**: Comprehensive sanitization of all inputs
- **Rate Limiting**: Protection against abuse
- **CORS Protection**: Secure cross-origin requests
- **Audit Logging**: Complete activity tracking
- **SSL Validation**: Certificate verification for URLs

---

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False` in settings
2. Configure production database (PostgreSQL recommended)
3. Set up Redis for Celery
4. Configure static file serving
5. Set up SSL certificates

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📝 License

This project is for educational and research purposes. Please respect the licenses of the original datasets used.

---

## 🆘 Support

For issues and questions:
- Check the logs in `logs/django.log`
- Review the admin panel for system status
- Ensure Redis is running for background tasks

---

## 🔄 Updates & Maintenance

### Regular Maintenance Tasks
- Cleanup old predictions: `python manage.py cleanup_old_predictions`
- Update threat intelligence: `python manage.py update_threat_intelligence`
- Database optimization: `python manage.py optimize_database`

### Monitoring
- Check Celery worker status
- Monitor Redis memory usage
- Review audit logs for anomalies 