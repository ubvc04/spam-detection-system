import pandas as pd
import csv
import io
import uuid
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Service for processing batch uploads of URLs, emails, and SMS"""
    
    def __init__(self, ml_service, threat_analyzer):
        self.ml_service = ml_service
        self.threat_analyzer = threat_analyzer
    
    def process_csv_upload(self, file_content: bytes, file_name: str, job_type: str) -> Dict:
        """Process CSV file upload and return job details"""
        try:
            # Parse CSV content
            csv_data = self._parse_csv(file_content)
            
            if not csv_data:
                return {
                    'success': False,
                    'error': 'No valid data found in CSV file'
                }
            
            # Validate data based on job type
            validation_result = self._validate_csv_data(csv_data, job_type)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Create batch job record
            from detector.models.enhanced_models import BatchProcessingJob
            
            batch_job = BatchProcessingJob.objects.create(
                job_type=job_type,
                file_name=file_name,
                file_size=len(file_content),
                total_items=len(csv_data),
                status='pending'
            )
            
            # Store CSV data for processing
            self._store_csv_data(batch_job.id, csv_data)
            
            return {
                'success': True,
                'batch_id': str(batch_job.id),
                'total_items': len(csv_data),
                'job_type': job_type
            }
            
        except Exception as e:
            logger.error(f"Error processing CSV upload: {str(e)}")
            return {
                'success': False,
                'error': f'Error processing file: {str(e)}'
            }
    
    def process_batch_job(self, batch_id: str) -> Dict:
        """Process a batch job and return results"""
        try:
            from detector.models.enhanced_models import BatchProcessingJob, EnhancedPredictionHistory
            
            batch_job = BatchProcessingJob.objects.get(id=batch_id)
            
            if batch_job.status != 'pending':
                return {
                    'success': False,
                    'error': f'Job is not in pending status: {batch_job.status}'
                }
            
            # Update job status
            batch_job.status = 'processing'
            batch_job.started_at = timezone.now()
            batch_job.save()
            
            # Load CSV data
            csv_data = self._load_csv_data(batch_id)
            
            results = []
            successful_count = 0
            failed_count = 0
            
            # Process each item
            for index, row in enumerate(csv_data):
                try:
                    result = self._process_single_item(row, batch_job.job_type, batch_id, index)
                    results.append(result)
                    successful_count += 1
                    
                    # Update progress
                    batch_job.processed_items = index + 1
                    batch_job.successful_items = successful_count
                    batch_job.failed_items = failed_count
                    batch_job.save()
                    
                except Exception as e:
                    logger.error(f"Error processing item {index}: {str(e)}")
                    results.append({
                        'row': index + 1,
                        'input': row,
                        'success': False,
                        'error': str(e)
                    })
                    failed_count += 1
                    
                    # Update progress
                    batch_job.processed_items = index + 1
                    batch_job.failed_items = failed_count
                    batch_job.save()
            
            # Generate results file
            results_file = self._generate_results_file(results, batch_job.job_type)
            
            # Update job status
            batch_job.status = 'completed'
            batch_job.completed_at = timezone.now()
            batch_job.results_file.save(f'results_{batch_id}.csv', ContentFile(results_file))
            batch_job.save()
            
            return {
                'success': True,
                'batch_id': str(batch_id),
                'total_processed': len(csv_data),
                'successful': successful_count,
                'failed': failed_count,
                'results_file': batch_job.results_file.url if batch_job.results_file else None
            }
            
        except Exception as e:
            logger.error(f"Error processing batch job {batch_id}: {str(e)}")
            
            # Update job status to failed
            try:
                batch_job.status = 'failed'
                batch_job.error_log = str(e)
                batch_job.save()
            except:
                pass
            
            return {
                'success': False,
                'error': f'Error processing batch job: {str(e)}'
            }
    
    def _parse_csv(self, file_content: bytes) -> List[Dict]:
        """Parse CSV content and return list of dictionaries"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    content = file_content.decode(encoding)
                    csv_reader = csv.DictReader(io.StringIO(content))
                    return list(csv_reader)
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("Could not decode CSV file with any supported encoding")
            
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            raise
    
    def _validate_csv_data(self, csv_data: List[Dict], job_type: str) -> Dict:
        """Validate CSV data based on job type"""
        if not csv_data:
            return {'valid': False, 'error': 'CSV file is empty'}
        
        # Check required columns based on job type
        required_columns = self._get_required_columns(job_type)
        
        if not required_columns:
            return {'valid': False, 'error': f'Unknown job type: {job_type}'}
        
        # Check if required columns exist
        sample_row = csv_data[0]
        missing_columns = [col for col in required_columns if col not in sample_row]
        
        if missing_columns:
            return {
                'valid': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }
        
        # Validate data types and content
        for index, row in enumerate(csv_data):
            validation_result = self._validate_row(row, job_type)
            if not validation_result['valid']:
                return {
                    'valid': False,
                    'error': f'Row {index + 1}: {validation_result["error"]}'
                }
        
        return {'valid': True}
    
    def _get_required_columns(self, job_type: str) -> List[str]:
        """Get required columns for each job type"""
        column_mapping = {
            'email': ['email_content'],
            'sms': ['sms_content'],
            'url': ['url'],
            'file': ['file_path', 'file_type']
        }
        return column_mapping.get(job_type, [])
    
    def _validate_row(self, row: Dict, job_type: str) -> Dict:
        """Validate a single row of data"""
        try:
            if job_type == 'email':
                email_content = row.get('email_content', '').strip()
                if not email_content or len(email_content) < 10:
                    return {'valid': False, 'error': 'Email content is too short'}
                
            elif job_type == 'sms':
                sms_content = row.get('sms_content', '').strip()
                if not sms_content or len(sms_content) < 5:
                    return {'valid': False, 'error': 'SMS content is too short'}
                
            elif job_type == 'url':
                url = row.get('url', '').strip()
                if not url or not self._is_valid_url(url):
                    return {'valid': False, 'error': 'Invalid URL format'}
                
            elif job_type == 'file':
                file_path = row.get('file_path', '').strip()
                if not file_path:
                    return {'valid': False, 'error': 'File path is required'}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _store_csv_data(self, batch_id: str, csv_data: List[Dict]):
        """Store CSV data for processing (using Redis or file system)"""
        import json
        import os
        
        # Create batch data directory
        batch_dir = os.path.join(settings.MEDIA_ROOT, 'batch_data')
        os.makedirs(batch_dir, exist_ok=True)
        
        # Store as JSON file
        data_file = os.path.join(batch_dir, f'{batch_id}.json')
        with open(data_file, 'w') as f:
            json.dump(csv_data, f)
    
    def _load_csv_data(self, batch_id: str) -> List[Dict]:
        """Load CSV data for processing"""
        import json
        import os
        
        data_file = os.path.join(settings.MEDIA_ROOT, 'batch_data', f'{batch_id}.json')
        with open(data_file, 'r') as f:
            return json.load(f)
    
    def _process_single_item(self, row: Dict, job_type: str, batch_id: str, position: int) -> Dict:
        """Process a single item from the batch"""
        start_time = timezone.now()
        
        try:
            if job_type == 'email':
                email_content = row.get('email_content', '').strip()
                ml_result = self.ml_service.predict_email(email_content)
                threat_analysis = self.threat_analyzer.analyze_email_threat(
                    email_content, ml_result.get('confidence_score', 0)
                )
                
                # Save to database
                from detector.models.enhanced_models import EnhancedPredictionHistory
                prediction = EnhancedPredictionHistory.objects.create(
                    prediction_type='email',
                    input_text=email_content[:200] + '...' if len(email_content) > 200 else email_content,
                    predicted_label=ml_result.get('result', 'Unknown'),
                    confidence_score=ml_result.get('confidence_score', 0),
                    risk_score=threat_analysis.get('risk_score', 0),
                    batch_id=batch_id,
                    batch_position=position,
                    processing_time=(timezone.now() - start_time).total_seconds()
                )
                
                return {
                    'row': position + 1,
                    'input': email_content[:100] + '...' if len(email_content) > 100 else email_content,
                    'prediction': ml_result.get('result', 'Unknown'),
                    'confidence': ml_result.get('confidence_score', 0),
                    'threat_category': threat_analysis.get('threat_category'),
                    'risk_level': threat_analysis.get('risk_level'),
                    'risk_score': threat_analysis.get('risk_score', 0),
                    'success': True
                }
                
            elif job_type == 'sms':
                sms_content = row.get('sms_content', '').strip()
                ml_result = self.ml_service.predict_sms(sms_content)
                threat_analysis = self.threat_analyzer.analyze_sms_threat(
                    sms_content, ml_result.get('confidence_score', 0)
                )
                
                # Save to database
                from detector.models.enhanced_models import EnhancedPredictionHistory
                prediction = EnhancedPredictionHistory.objects.create(
                    prediction_type='sms',
                    input_text=sms_content[:200] + '...' if len(sms_content) > 200 else sms_content,
                    predicted_label=ml_result.get('result', 'Unknown'),
                    confidence_score=ml_result.get('confidence_score', 0),
                    risk_score=threat_analysis.get('risk_score', 0),
                    batch_id=batch_id,
                    batch_position=position,
                    processing_time=(timezone.now() - start_time).total_seconds()
                )
                
                return {
                    'row': position + 1,
                    'input': sms_content[:100] + '...' if len(sms_content) > 100 else sms_content,
                    'prediction': ml_result.get('result', 'Unknown'),
                    'confidence': ml_result.get('confidence_score', 0),
                    'threat_category': threat_analysis.get('threat_category'),
                    'risk_level': threat_analysis.get('risk_level'),
                    'risk_score': threat_analysis.get('risk_score', 0),
                    'success': True
                }
                
            elif job_type == 'url':
                url = row.get('url', '').strip()
                ml_result = self.ml_service.predict_url(url)
                threat_analysis = self.threat_analyzer.analyze_url_threat(
                    url, ml_result.get('confidence_score', 0)
                )
                
                # Save to database
                from detector.models.enhanced_models import EnhancedPredictionHistory
                prediction = EnhancedPredictionHistory.objects.create(
                    prediction_type='url',
                    input_text=url,
                    predicted_label=ml_result.get('result', 'Unknown'),
                    confidence_score=ml_result.get('confidence_score', 0),
                    risk_score=threat_analysis.get('risk_score', 0),
                    domain=threat_analysis.get('domain_analysis', {}).get('domain'),
                    country=threat_analysis.get('domain_analysis', {}).get('country'),
                    ssl_valid=threat_analysis.get('ssl_analysis', {}).get('valid'),
                    batch_id=batch_id,
                    batch_position=position,
                    processing_time=(timezone.now() - start_time).total_seconds()
                )
                
                return {
                    'row': position + 1,
                    'input': url,
                    'prediction': ml_result.get('result', 'Unknown'),
                    'confidence': ml_result.get('confidence_score', 0),
                    'threat_category': threat_analysis.get('threat_category'),
                    'risk_level': threat_analysis.get('risk_level'),
                    'risk_score': threat_analysis.get('risk_score', 0),
                    'domain': threat_analysis.get('domain_analysis', {}).get('domain'),
                    'country': threat_analysis.get('domain_analysis', {}).get('country'),
                    'ssl_valid': threat_analysis.get('ssl_analysis', {}).get('valid'),
                    'success': True
                }
            
            else:
                raise ValueError(f'Unsupported job type: {job_type}')
                
        except Exception as e:
            logger.error(f"Error processing item {position}: {str(e)}")
            return {
                'row': position + 1,
                'input': str(row),
                'success': False,
                'error': str(e)
            }
    
    def _generate_results_file(self, results: List[Dict], job_type: str) -> bytes:
        """Generate CSV results file"""
        output = io.StringIO()
        
        # Define columns based on job type
        if job_type == 'email':
            fieldnames = ['row', 'input', 'prediction', 'confidence', 'threat_category', 'risk_level', 'risk_score', 'success', 'error']
        elif job_type == 'sms':
            fieldnames = ['row', 'input', 'prediction', 'confidence', 'threat_category', 'risk_level', 'risk_score', 'success', 'error']
        elif job_type == 'url':
            fieldnames = ['row', 'input', 'prediction', 'confidence', 'threat_category', 'risk_level', 'risk_score', 'domain', 'country', 'ssl_valid', 'success', 'error']
        else:
            fieldnames = ['row', 'input', 'success', 'error']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow(result)
        
        return output.getvalue().encode('utf-8')
    
    def get_batch_status(self, batch_id: str) -> Dict:
        """Get current status of a batch job"""
        try:
            from detector.models.enhanced_models import BatchProcessingJob
            
            batch_job = BatchProcessingJob.objects.get(id=batch_id)
            
            return {
                'success': True,
                'batch_id': str(batch_id),
                'status': batch_job.status,
                'progress': batch_job.progress_percentage,
                'total_items': batch_job.total_items,
                'processed_items': batch_job.processed_items,
                'successful_items': batch_job.successful_items,
                'failed_items': batch_job.failed_items,
                'created_at': batch_job.created_at,
                'started_at': batch_job.started_at,
                'completed_at': batch_job.completed_at,
                'results_file': batch_job.results_file.url if batch_job.results_file else None
            }
            
        except BatchProcessingJob.DoesNotExist:
            return {
                'success': False,
                'error': 'Batch job not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 