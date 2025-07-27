import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ml_security_detector.settings')

app = Celery('ml_security_detector')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'cleanup-old-predictions': {
        'task': 'detector.tasks.cleanup_tasks.cleanup_old_predictions',
        'schedule': 86400.0,  # Daily
    },
    'update-threat-intelligence': {
        'task': 'detector.tasks.intelligence_tasks.update_threat_intelligence',
        'schedule': 3600.0,  # Hourly
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 