from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from detector.models import EnhancedPredictionHistory, AuditLog

@shared_task
def cleanup_old_predictions():
    """Clean up old prediction history (older than 90 days)"""
    cutoff_date = timezone.now() - timedelta(days=90)
    deleted_count = EnhancedPredictionHistory.objects.filter(
        timestamp__lt=cutoff_date
    ).delete()[0]
    
    print(f"Cleaned up {deleted_count} old predictions")
    return deleted_count

@shared_task
def cleanup_old_audit_logs():
    """Clean up old audit logs (older than 30 days)"""
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = AuditLog.objects.filter(
        timestamp__lt=cutoff_date
    ).delete()[0]
    
    print(f"Cleaned up {deleted_count} old audit logs")
    return deleted_count 