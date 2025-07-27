from django.contrib import admin
from .models import (
    PredictionHistory, EnhancedPredictionHistory, ThreatCategory, 
    RiskLevel, BatchProcessingJob, ThreatPattern, DomainReputation, 
    URLScreenshot, AuditLog
)

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ['prediction_type', 'predicted_label', 'confidence_score', 'timestamp']
    list_filter = ['prediction_type', 'predicted_label', 'timestamp']
    search_fields = ['input_text', 'predicted_label']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']

@admin.register(EnhancedPredictionHistory)
class EnhancedPredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ['prediction_type', 'predicted_label', 'confidence_score', 'risk_level', 'threat_category', 'timestamp']
    list_filter = ['prediction_type', 'predicted_label', 'risk_level', 'threat_category', 'timestamp']
    search_fields = ['input_text', 'predicted_label', 'domain']
    readonly_fields = ['timestamp', 'id', 'processing_time']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'

@admin.register(ThreatCategory)
class ThreatCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon']
    search_fields = ['name', 'description']
    list_filter = ['icon']

@admin.register(RiskLevel)
class RiskLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'color', 'description']
    list_filter = ['level']
    ordering = ['level']

@admin.register(BatchProcessingJob)
class BatchProcessingJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'job_type', 'status', 'total_items', 'processed_items', 'created_at']
    list_filter = ['job_type', 'status', 'created_at']
    readonly_fields = ['id', 'created_at', 'started_at', 'completed_at', 'progress_percentage']
    ordering = ['-created_at']

@admin.register(ThreatPattern)
class ThreatPatternAdmin(admin.ModelAdmin):
    list_display = ['pattern_type', 'pattern_value', 'confidence', 'threat_category', 'occurrence_count', 'last_seen']
    list_filter = ['pattern_type', 'threat_category', 'risk_level', 'last_seen']
    search_fields = ['pattern_value', 'description']
    readonly_fields = ['first_seen', 'last_seen', 'occurrence_count']
    ordering = ['-last_seen']

@admin.register(DomainReputation)
class DomainReputationAdmin(admin.ModelAdmin):
    list_display = ['domain', 'reputation_score', 'threat_score', 'is_blacklisted', 'country', 'last_checked']
    list_filter = ['is_blacklisted', 'ssl_valid', 'country', 'last_checked']
    search_fields = ['domain', 'registrar', 'country']
    readonly_fields = ['first_seen', 'last_checked', 'check_count']
    ordering = ['-last_checked']

@admin.register(URLScreenshot)
class URLScreenshotAdmin(admin.ModelAdmin):
    list_display = ['url', 'width', 'height', 'file_size', 'created_at']
    list_filter = ['created_at']
    search_fields = ['url']
    readonly_fields = ['created_at', 'processing_time']
    ordering = ['-created_at']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user_ip', 'success', 'timestamp']
    list_filter = ['action', 'success', 'timestamp']
    search_fields = ['user_ip', 'user_agent', 'error_message']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
