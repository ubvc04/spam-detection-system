# 🛠️ Installation Fix Guide - ML Security Platform

## 🚨 **Errors Found & Solutions**

### **Error 1: Non-existent packages**
- ❌ `phishtank-api>=0.1.0` - Package doesn't exist
- ❌ `abuseipdb>=0.0.3` - Package doesn't exist

### **Error 2: Windows compatibility issues**
- ❌ `python-magic` - May not work on Windows

## 🔧 **Step-by-Step Fix Commands**

### **Step 1: Clean up and install fixed requirements**

```bash
# Navigate to your project directory
cd "C:\Users\baves\Downloads\IBM - Copy"

# Install the fixed requirements file
pip install -r requirements/enhanced_requirements_fixed.txt
```

### **Step 2: Install Playwright browsers (for screenshots)**

```bash
# Install Playwright browsers
playwright install chromium
```

### **Step 3: Set up Redis (Windows)**

Since you're on Windows, you have a few options for Redis:

#### **Option A: Use Docker (Recommended)**
```bash
# Install Docker Desktop first, then run:
docker run -d -p 6379:6379 redis:latest
```

#### **Option B: Use Windows Subsystem for Linux (WSL)**
```bash
# Install WSL, then in WSL terminal:
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start
```

#### **Option C: Use Redis for Windows (Alternative)**
```bash
# Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases
# Or use a cloud Redis service
```

### **Step 4: Create Django migrations**

```bash
# Create migrations for enhanced models
python manage.py makemigrations detector

# Apply migrations
python manage.py migrate
```

### **Step 5: Create initial data**

```bash
# Create initial threat categories and risk levels
python manage.py shell
```

In the Django shell, run:
```python
from detector.models.enhanced_models import ThreatCategory, RiskLevel

# Create threat categories
categories = [
    {'name': 'Financial Fraud', 'description': 'Banking and payment fraud attempts', 'color': '#ef4444'},
    {'name': 'Credential Theft', 'description': 'Password and login credential theft', 'color': '#f59e0b'},
    {'name': 'Malware Distribution', 'description': 'Malicious software distribution', 'color': '#8b5cf6'},
    {'name': 'Social Engineering', 'description': 'Social engineering attacks', 'color': '#ec4899'},
    {'name': 'Suspicious Activity', 'description': 'General suspicious behavior', 'color': '#6b7280'},
]

for cat in categories:
    ThreatCategory.objects.get_or_create(
        name=cat['name'],
        defaults=cat
    )

# Create risk levels
risk_levels = [
    {'name': 'Low', 'level': 1, 'color': '#10b981', 'description': 'Minimal risk'},
    {'name': 'Medium', 'level': 2, 'color': '#f59e0b', 'description': 'Moderate risk'},
    {'name': 'High', 'level': 3, 'color': '#f97316', 'description': 'High risk'},
    {'name': 'Critical', 'level': 4, 'color': '#ef4444', 'description': 'Critical risk'},
]

for risk in risk_levels:
    RiskLevel.objects.get_or_create(
        name=risk['name'],
        defaults=risk
    )

exit()
```

### **Step 6: Test the installation**

```bash
# Test Django setup
python manage.py check

# Test Celery (if Redis is running)
python manage.py shell
```

In Django shell:
```python
from celery import current_app
print("Celery is working!" if current_app else "Celery not configured")
exit()
```

## 🚀 **Alternative: Minimal Installation (If you want to start simple)**

If you want to start with just the basic enhanced features without all the advanced dependencies:

```bash
# Create a minimal requirements file
echo "Django>=4.2.0,<5.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
celery>=5.3.0
redis>=4.5.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
joblib>=1.3.0
beautifulsoup4>=4.12.0
tldextract>=5.0.0
requests>=2.31.0
Pillow>=10.0.0
python-dotenv>=1.0.0
bleach>=6.0.0" > requirements/minimal_requirements.txt

# Install minimal requirements
pip install -r requirements/minimal_requirements.txt
```

## 🔍 **Troubleshooting Common Issues**

### **Issue 1: Redis Connection Error**
```bash
# Test Redis connection
python -c "import redis; r = redis.Redis(); print('Redis OK' if r.ping() else 'Redis Failed')"
```

### **Issue 2: Celery Worker Not Starting**
```bash
# Start Celery worker with debug info
celery -A ml_security_detector worker -l debug
```

### **Issue 3: Database Migration Errors**
```bash
# Reset migrations (if needed)
python manage.py migrate detector zero
python manage.py makemigrations detector
python manage.py migrate
```

### **Issue 4: Import Errors**
```bash
# Check if all packages are installed
pip list | findstr -i "django celery redis"
```

## 📋 **Verification Checklist**

After running the commands, verify:

- [ ] All packages installed without errors
- [ ] Django migrations applied successfully
- [ ] Redis is running and accessible
- [ ] Celery worker can start
- [ ] Initial data (threat categories, risk levels) created
- [ ] Django server starts without errors

## 🎯 **Next Steps After Installation**

1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Start Celery worker (in new terminal):**
   ```bash
   celery -A ml_security_detector worker -l info
   ```

3. **Start Celery beat (in new terminal):**
   ```bash
   celery -A ml_security_detector beat -l info
   ```

4. **Access the enhanced dashboard:**
   - Go to `http://localhost:8000/dashboard/`

## 🆘 **If You Still Have Issues**

If you encounter any specific errors, please share the exact error message and I'll help you resolve it step by step!

**Common fallback approach:**
```bash
# If all else fails, install only the essential packages
pip install Django djangorestframework celery redis scikit-learn pandas numpy joblib
```

This will give you the core functionality to start building the enhanced features gradually. 