# ML Security Detector - Django Web Application

A modern Django web application that provides AI-powered security detection for phishing emails, spam SMS, and malicious URLs.

## Features

- 🛡️ **Email Phishing Detection**: Analyze email content for phishing attempts
- 📱 **SMS Spam Detection**: Detect spam messages in SMS content
- 🔗 **URL Malicious Check**: Identify potentially malicious URLs
- 🌙 **Dark Mode**: Toggle between light and dark themes
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- ⚡ **Real-time Analysis**: Instant results using pre-trained ML models

## Technology Stack

- **Backend**: Django 5.0.2
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **ML Models**: Scikit-learn (pre-trained models)
- **Model Storage**: Joblib (.pkl files)

## Project Structure

```
ml_security_detector/
├── detector/                 # Main Django app
│   ├── ml_service.py        # ML model service
│   ├── views.py             # Django views
│   ├── urls.py              # URL routing
│   └── ...
├── ml_security_detector/     # Django project settings
├── templates/               # HTML templates
│   └── detector/
│       └── home.html        # Main application page
├── src/                     # Original ML models and data
│   ├── email_model.pkl
│   ├── sms_model.pkl
│   ├── url_model.pkl
│   └── ...
├── manage.py
└── requirements.txt
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
python manage.py migrate
```

### 3. Start the Development Server

```bash
python manage.py runserver
```

### 4. Access the Application

Open your browser and navigate to: `http://127.0.0.1:8000/`

## Usage

1. **Email Classification**: 
   - Click on the "Email Classification" tab
   - Paste email content in the text area
   - Click "Analyze Email" to get results

2. **SMS Spam Detection**:
   - Click on the "SMS Spam Detection" tab
   - Enter SMS message text
   - Click "Analyze SMS" to check for spam

3. **URL Malicious Check**:
   - Click on the "URL Malicious Check" tab
   - Enter the URL to check
   - Click "Check URL" to analyze

## API Endpoints

The application provides REST API endpoints for programmatic access:

- `POST /predict/email/` - Email phishing detection
- `POST /predict/sms/` - SMS spam detection  
- `POST /predict/url/` - URL malicious check

### Example API Usage

```bash
# Email prediction
curl -X POST http://127.0.0.1:8000/predict/email/ \
  -H "Content-Type: application/json" \
  -d '{"email_text": "Your email content here"}'

# SMS prediction
curl -X POST http://127.0.0.1:8000/predict/sms/ \
  -H "Content-Type: application/json" \
  -d '{"sms_text": "Your SMS text here"}'

# URL prediction
curl -X POST http://127.0.0.1:8000/predict/url/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Model Information

The application uses three pre-trained machine learning models:

1. **Email Model**: TF-IDF vectorizer + classifier for phishing detection
2. **SMS Model**: TF-IDF vectorizer + classifier for spam detection
3. **URL Model**: Feature-based classifier for malicious URL detection

All models are loaded once when the application starts and reused for predictions.

## Development

### Adding New Features

1. Models are defined in `detector/models.py`
2. Views are in `detector/views.py`
3. Templates are in `templates/detector/`
4. URL routing is in `detector/urls.py`

### Customization

- Modify the UI by editing `templates/detector/home.html`
- Add new ML models in `detector/ml_service.py`
- Extend API endpoints in `detector/views.py`

## Security Notes

- The application is configured for development use
- For production deployment, update `DEBUG = False` in settings
- Consider adding authentication and rate limiting
- Ensure proper CORS configuration for production

## Troubleshooting

### Common Issues

1. **Model Loading Error**: Ensure all .pkl files are in the `src/` directory
2. **Import Errors**: Verify all dependencies are installed
3. **Port Already in Use**: Change the port with `python manage.py runserver 8001`

### Debug Mode

The application runs in debug mode by default. Check the Django debug page for detailed error information.

## License

This project is part of the ML Security Detector system. Please refer to the main project documentation for licensing information. 