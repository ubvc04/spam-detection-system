import re
import requests
import whois
import socket
import ssl
from datetime import datetime, timedelta
from urllib.parse import urlparse
import geoip2.database
import geoip2.errors
from typing import Dict, List, Tuple, Optional
import tldextract
from django.utils import timezone
from django.conf import settings

class ThreatAnalyzer:
    """Advanced threat analysis and intelligence service"""
    
    def __init__(self):
        self.threat_patterns = {
            'financial_fraud': [
                r'bank.*account.*suspended',
                r'paypal.*verify.*account',
                r'credit.*card.*expired',
                r'banking.*security.*update',
                r'account.*locked.*verify',
                r'urgent.*bank.*action',
                r'wire.*transfer.*required',
                r'account.*compromise.*detected'
            ],
            'credential_theft': [
                r'password.*expired',
                r'login.*failed.*verify',
                r'account.*hacked.*secure',
                r'reset.*password.*urgent',
                r'security.*breach.*detected',
                r'verify.*identity.*immediately',
                r'login.*attempt.*suspicious'
            ],
            'malware_distribution': [
                r'free.*download.*virus',
                r'update.*flash.*player',
                r'install.*security.*update',
                r'click.*here.*download',
                r'free.*antivirus.*scan',
                r'update.*java.*required',
                r'install.*browser.*extension'
            ],
            'social_engineering': [
                r'you.*won.*prize',
                r'claim.*inheritance',
                r'lottery.*winner',
                r'urgent.*help.*needed',
                r'friend.*stranded.*abroad',
                r'charity.*donation.*urgent',
                r'limited.*time.*offer'
            ]
        }
        
        self.suspicious_domains = [
            'bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co',
            'is.gd', 'buff.ly', 'adf.ly', 'short.to', 'tr.im'
        ]
        
        self.suspicious_tlds = [
            'xyz', 'top', 'club', 'online', 'site', 'win',
            'bid', 'loan', 'click', 'work', 'live'
        ]
    
    def analyze_email_threat(self, email_content: str, confidence_score: float) -> Dict:
        """Analyze email content for threat categorization and risk scoring"""
        analysis = {
            'threat_category': None,
            'risk_level': 'Low',
            'risk_score': 0.0,
            'patterns_detected': [],
            'suspicious_indicators': []
        }
        
        # Convert to lowercase for analysis
        content_lower = email_content.lower()
        
        # Check for threat patterns
        for category, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    analysis['patterns_detected'].append({
                        'category': category,
                        'pattern': pattern,
                        'matched_text': re.search(pattern, content_lower).group()
                    })
        
        # Calculate risk score based on patterns and confidence
        risk_score = self._calculate_risk_score(
            patterns=analysis['patterns_detected'],
            confidence=confidence_score,
            content_length=len(email_content),
            has_urgency=bool(re.search(r'urgent|immediate|now|asap', content_lower)),
            has_money_mentions=bool(re.search(r'\$|money|bank|account|payment', content_lower))
        )
        
        analysis['risk_score'] = risk_score
        analysis['risk_level'] = self._get_risk_level(risk_score)
        analysis['threat_category'] = self._get_primary_threat_category(analysis['patterns_detected'])
        
        return analysis
    
    def analyze_url_threat(self, url: str, confidence_score: float) -> Dict:
        """Analyze URL for threat categorization and risk scoring"""
        analysis = {
            'threat_category': None,
            'risk_level': 'Low',
            'risk_score': 0.0,
            'domain_analysis': {},
            'ssl_analysis': {},
            'suspicious_indicators': []
        }
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Domain analysis
            domain_analysis = self._analyze_domain(domain)
            analysis['domain_analysis'] = domain_analysis
            
            # SSL analysis
            ssl_analysis = self._analyze_ssl(url)
            analysis['ssl_analysis'] = ssl_analysis
            
            # Check for suspicious indicators
            suspicious_indicators = []
            
            # Suspicious domain
            if domain in self.suspicious_domains:
                suspicious_indicators.append('suspicious_domain')
            
            # Suspicious TLD
            tld = tldextract.extract(url).suffix
            if tld in self.suspicious_tlds:
                suspicious_indicators.append('suspicious_tld')
            
            # Long URL
            if len(url) > 100:
                suspicious_indicators.append('long_url')
            
            # IP address in URL
            if re.search(r'\d+\.\d+\.\d+\.\d+', url):
                suspicious_indicators.append('ip_in_url')
            
            # Special characters
            if re.search(r'[%@\-_]', url):
                suspicious_indicators.append('special_chars')
            
            analysis['suspicious_indicators'] = suspicious_indicators
            
            # Calculate risk score
            risk_score = self._calculate_url_risk_score(
                confidence=confidence_score,
                domain_age=domain_analysis.get('age_days', 0),
                ssl_valid=ssl_analysis.get('valid', False),
                suspicious_indicators=suspicious_indicators,
                domain_reputation=domain_analysis.get('reputation_score', 0)
            )
            
            analysis['risk_score'] = risk_score
            analysis['risk_level'] = self._get_risk_level(risk_score)
            analysis['threat_category'] = self._get_url_threat_category(suspicious_indicators, domain_analysis)
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def analyze_sms_threat(self, sms_content: str, confidence_score: float) -> Dict:
        """Analyze SMS content for threat categorization and risk scoring"""
        analysis = {
            'threat_category': None,
            'risk_level': 'Low',
            'risk_score': 0.0,
            'patterns_detected': [],
            'suspicious_indicators': []
        }
        
        content_lower = sms_content.lower()
        
        # SMS-specific patterns
        sms_patterns = {
            'financial_fraud': [
                r'bank.*text.*verify',
                r'card.*blocked.*call',
                r'account.*suspended.*urgent',
                r'fraud.*detected.*call'
            ],
            'credential_theft': [
                r'password.*reset.*link',
                r'login.*failed.*verify',
                r'account.*locked.*unlock'
            ],
            'social_engineering': [
                r'you.*won.*claim',
                r'urgent.*help.*money',
                r'friend.*needs.*urgent',
                r'limited.*offer.*text'
            ]
        }
        
        # Check for patterns
        for category, patterns in sms_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    analysis['patterns_detected'].append({
                        'category': category,
                        'pattern': pattern,
                        'matched_text': re.search(pattern, content_lower).group()
                    })
        
        # SMS-specific indicators
        indicators = []
        if re.search(r'click.*here', content_lower):
            indicators.append('click_here_link')
        if re.search(r'call.*now', content_lower):
            indicators.append('urgent_call')
        if re.search(r'\$\d+', content_lower):
            indicators.append('money_mention')
        if len(sms_content) > 160:
            indicators.append('long_message')
        
        analysis['suspicious_indicators'] = indicators
        
        # Calculate risk score
        risk_score = self._calculate_sms_risk_score(
            confidence=confidence_score,
            patterns=analysis['patterns_detected'],
            indicators=indicators,
            has_urgency=bool(re.search(r'urgent|now|asap', content_lower))
        )
        
        analysis['risk_score'] = risk_score
        analysis['risk_level'] = self._get_risk_level(risk_score)
        analysis['threat_category'] = self._get_primary_threat_category(analysis['patterns_detected'])
        
        return analysis
    
    def _analyze_domain(self, domain: str) -> Dict:
        """Analyze domain for reputation and characteristics"""
        analysis = {
            'domain': domain,
            'age_days': 0,
            'reputation_score': 0.0,
            'country': None,
            'registrar': None,
            'expiry_date': None
        }
        
        try:
            # WHOIS lookup
            w = whois.whois(domain)
            if w.creation_date:
                creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
                analysis['age_days'] = (timezone.now() - creation_date).days
                analysis['registrar'] = w.registrar
                analysis['expiry_date'] = w.expiration_date
            
            # Geographic analysis
            try:
                reader = geoip2.database.Reader('GeoLite2-City.mmdb')
                response = reader.city(socket.gethostbyname(domain))
                analysis['country'] = response.country.name
                analysis['city'] = response.city.name
            except:
                pass
            
            # Reputation scoring
            analysis['reputation_score'] = self._calculate_domain_reputation(domain, analysis['age_days'])
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_ssl(self, url: str) -> Dict:
        """Analyze SSL certificate for the URL"""
        analysis = {
            'valid': False,
            'expiry_date': None,
            'issuer': None,
            'error': None
        }
        
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            if parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        analysis['valid'] = True
                        analysis['issuer'] = dict(x[0] for x in cert['issuer'])
                        
                        # Parse expiry date
                        if 'notAfter' in cert:
                            expiry_str = cert['notAfter']
                            analysis['expiry_date'] = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
        
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _calculate_risk_score(self, patterns: List, confidence: float, 
                            content_length: int, has_urgency: bool, 
                            has_money_mentions: bool) -> float:
        """Calculate comprehensive risk score"""
        base_score = confidence
        
        # Pattern-based scoring
        pattern_score = len(patterns) * 15
        if patterns:
            # Higher score for financial fraud
            financial_patterns = [p for p in patterns if p['category'] == 'financial_fraud']
            pattern_score += len(financial_patterns) * 10
        
        # Content-based scoring
        content_score = 0
        if has_urgency:
            content_score += 20
        if has_money_mentions:
            content_score += 15
        if content_length > 500:
            content_score += 5
        
        total_score = min(100, base_score + pattern_score + content_score)
        return total_score
    
    def _calculate_url_risk_score(self, confidence: float, domain_age: int,
                                ssl_valid: bool, suspicious_indicators: List,
                                domain_reputation: float) -> float:
        """Calculate URL-specific risk score"""
        base_score = confidence
        
        # Domain age scoring
        age_score = 0
        if domain_age < 30:
            age_score += 25
        elif domain_age < 90:
            age_score += 15
        elif domain_age < 365:
            age_score += 5
        
        # SSL scoring
        ssl_score = 0 if ssl_valid else 20
        
        # Suspicious indicators scoring
        indicator_score = len(suspicious_indicators) * 10
        
        # Reputation scoring
        reputation_score = max(0, -domain_reputation)
        
        total_score = min(100, base_score + age_score + ssl_score + indicator_score + reputation_score)
        return total_score
    
    def _calculate_sms_risk_score(self, confidence: float, patterns: List,
                                indicators: List, has_urgency: bool) -> float:
        """Calculate SMS-specific risk score"""
        base_score = confidence
        
        # Pattern scoring
        pattern_score = len(patterns) * 20
        
        # Indicator scoring
        indicator_score = len(indicators) * 8
        
        # Urgency scoring
        urgency_score = 15 if has_urgency else 0
        
        total_score = min(100, base_score + pattern_score + indicator_score + urgency_score)
        return total_score
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score >= 80:
            return 'Critical'
        elif risk_score >= 60:
            return 'High'
        elif risk_score >= 40:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_primary_threat_category(self, patterns: List) -> str:
        """Get the primary threat category from detected patterns"""
        if not patterns:
            return 'Unknown'
        
        # Count patterns by category
        category_counts = {}
        for pattern in patterns:
            category = pattern['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Return the most common category
        return max(category_counts.items(), key=lambda x: x[1])[0]
    
    def _get_url_threat_category(self, indicators: List, domain_analysis: Dict) -> str:
        """Get threat category for URL analysis"""
        if 'suspicious_domain' in indicators or 'suspicious_tld' in indicators:
            return 'malware_distribution'
        elif 'ip_in_url' in indicators:
            return 'credential_theft'
        elif domain_analysis.get('age_days', 0) < 30:
            return 'financial_fraud'
        else:
            return 'suspicious_activity'
    
    def _calculate_domain_reputation(self, domain: str, age_days: int) -> float:
        """Calculate domain reputation score (-100 to 100)"""
        reputation = 0
        
        # Age-based reputation
        if age_days > 365:
            reputation += 30
        elif age_days > 90:
            reputation += 10
        elif age_days < 30:
            reputation -= 20
        
        # Domain characteristics
        if domain in self.suspicious_domains:
            reputation -= 50
        
        # TLD-based reputation
        tld = domain.split('.')[-1]
        if tld in self.suspicious_tlds:
            reputation -= 30
        
        return max(-100, min(100, reputation)) 