from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class ThreatCategory(models.Model):
    """Categories for different types of threats"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    color = models.CharField(max_length=7, default="#FF0000")  # Hex color
    icon = models.CharField(max_length=50, default="warning")
    
    class Meta:
        verbose_name_plural = "Threat Categories"
    
    def __str__(self):
        return self.name

class RiskLevel(models.Model):
    """Risk levels for threats"""
    name = models.CharField(max_length=20, unique=True)
    level = models.IntegerField(unique=True)  # 1=Low, 2=Medium, 3=High, 4=Critical
    color = models.CharField(max_length=7)
    description = models.TextField()
    
    class Meta:
        ordering = ['level']
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"

class EnhancedPredictionHistory(models.Model):
    """Enhanced prediction history with threat intelligence"""
    PREDICTION_TYPES = [
        ('email', 'Email Phishing'),
        ('sms', 'SMS Spam'),
        ('url', 'URL Malicious'),
        ('file', 'File Analysis'),
        ('batch', 'Batch Processing'),
    ]
    
    # Basic prediction info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction_type = models.CharField(max_length=10, choices=PREDICTION_TYPES)
    input_text = models.TextField()
    predicted_label = models.CharField(max_length=50)
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Threat intelligence
    threat_category = models.ForeignKey(ThreatCategory, on_delete=models.SET_NULL, null=True, blank=True)
    risk_level = models.ForeignKey(RiskLevel, on_delete=models.SET_NULL, null=True, blank=True)
    risk_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Domain analysis
    domain = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    isp = models.CharField(max_length=200, blank=True)
    
    # SSL and security
    ssl_valid = models.BooleanField(null=True, blank=True)
    ssl_expiry = models.DateTimeField(null=True, blank=True)
    
    # Additional metadata
    user_agent = models.CharField(max_length=500, blank=True)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    processing_time = models.FloatField(default=0.0)  # in seconds
    
    # Batch processing
    batch_id = models.UUIDField(null=True, blank=True)
    batch_position = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['prediction_type', 'timestamp']),
            models.Index(fields=['threat_category', 'risk_level']),
            models.Index(fields=['domain', 'country']),
            models.Index(fields=['batch_id']),
        ]
    
    def __str__(self):
        return f"{self.prediction_type} - {self.predicted_label} ({self.confidence_score:.1f}%)"
    
    @property
    def confidence_percentage(self):
        return f"{self.confidence_score:.1f}%"
    
    @property
    def is_malicious(self):
        malicious_labels = ['PHISHING', 'SPAM', 'MALICIOUS', 'SUSPICIOUS']
        return self.predicted_label in malicious_labels
    
    @property
    def age_hours(self):
        return (timezone.now() - self.timestamp).total_seconds() / 3600

class BatchProcessingJob(models.Model):
    """Batch processing jobs"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_type = models.CharField(max_length=20, choices=EnhancedPredictionHistory.PREDICTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # File information
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    total_items = models.IntegerField(default=0)
    processed_items = models.IntegerField(default=0)
    successful_items = models.IntegerField(default=0)
    failed_items = models.IntegerField(default=0)
    
    # Timing
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    results_file = models.FileField(upload_to='batch_results/', null=True, blank=True)
    error_log = models.TextField(blank=True)
    
    # Metadata
    user_agent = models.CharField(max_length=500, blank=True)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Batch {self.id} - {self.job_type} ({self.status})"
    
    @property
    def progress_percentage(self):
        if self.total_items == 0:
            return 0
        return (self.processed_items / self.total_items) * 100
    
    @property
    def duration(self):
        if not self.started_at:
            return None
        end_time = self.completed_at or timezone.now()
        return end_time - self.started_at

class ThreatPattern(models.Model):
    """Identified threat patterns"""
    pattern_type = models.CharField(max_length=50)  # 'email_template', 'url_pattern', 'keyword'
    pattern_value = models.TextField()
    confidence = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    threat_category = models.ForeignKey(ThreatCategory, on_delete=models.CASCADE)
    risk_level = models.ForeignKey(RiskLevel, on_delete=models.CASCADE)
    
    # Usage statistics
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    occurrence_count = models.IntegerField(default=1)
    
    # Metadata
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['pattern_type', 'pattern_value']
        ordering = ['-last_seen']
    
    def __str__(self):
        return f"{self.pattern_type}: {self.pattern_value[:50]}"

class DomainReputation(models.Model):
    """Domain reputation and analysis data"""
    domain = models.CharField(max_length=255, unique=True)
    
    # Basic info
    registration_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    registrar = models.CharField(max_length=200, blank=True)
    
    # Reputation scores
    reputation_score = models.FloatField(default=0.0, validators=[MinValueValidator(-100), MaxValueValidator(100)])
    threat_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Threat intelligence
    is_blacklisted = models.BooleanField(default=False)
    threat_categories = models.ManyToManyField(ThreatCategory, blank=True)
    
    # Geographic info
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    isp = models.CharField(max_length=200, blank=True)
    
    # SSL info
    ssl_valid = models.BooleanField(null=True, blank=True)
    ssl_expiry = models.DateTimeField(null=True, blank=True)
    ssl_issuer = models.CharField(max_length=200, blank=True)
    
    # Statistics
    first_seen = models.DateTimeField(default=timezone.now)
    last_checked = models.DateTimeField(default=timezone.now)
    check_count = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-last_checked']
    
    def __str__(self):
        return f"{self.domain} (Score: {self.reputation_score})"

class URLScreenshot(models.Model):
    """Screenshots of analyzed URLs"""
    url = models.URLField(max_length=2000)
    screenshot = models.ImageField(upload_to='screenshots/')
    thumbnail = models.ImageField(upload_to='screenshots/thumbnails/', null=True, blank=True)
    
    # Metadata
    width = models.IntegerField()
    height = models.IntegerField()
    file_size = models.IntegerField()  # in bytes
    
    # Analysis
    prediction = models.ForeignKey(EnhancedPredictionHistory, on_delete=models.CASCADE, null=True, blank=True)
    
    # Timing
    created_at = models.DateTimeField(default=timezone.now)
    processing_time = models.FloatField(default=0.0)  # in seconds
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Screenshot of {self.url}"

class AuditLog(models.Model):
    """Audit log for security and compliance"""
    ACTION_CHOICES = [
        ('prediction', 'Prediction Made'),
        ('batch_upload', 'Batch Upload'),
        ('history_clear', 'History Cleared'),
        ('admin_action', 'Admin Action'),
        ('api_access', 'API Access'),
        ('file_upload', 'File Upload'),
    ]
    
    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user_ip = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Details
    details = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Related objects
    prediction = models.ForeignKey(EnhancedPredictionHistory, on_delete=models.SET_NULL, null=True, blank=True)
    batch_job = models.ForeignKey(BatchProcessingJob, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user_ip', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} at {self.timestamp} from {self.user_ip}"

# Keep the old model for backward compatibility
class PredictionHistory(models.Model):
    PREDICTION_TYPES = [
        ('email', 'Email Phishing'),
        ('sms', 'SMS Spam'),
        ('url', 'URL Malicious'),
    ]
    
    prediction_type = models.CharField(max_length=10, choices=PREDICTION_TYPES)
    input_text = models.TextField()
    predicted_label = models.CharField(max_length=50)
    confidence_score = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Prediction Histories'
    
    def __str__(self):
        return f"{self.prediction_type} - {self.predicted_label} ({self.confidence_score:.1f}%)"
    
    @property
    def confidence_percentage(self):
        return f"{self.confidence_score:.1f}%"
    
    @property
    def is_malicious(self):
        """Check if the prediction indicates malicious/spam content"""
        malicious_labels = ['PHISHING', 'SPAM', 'MALICIOUS']
        return self.predicted_label in malicious_labels
