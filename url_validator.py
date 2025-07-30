import re
from urllib.parse import urlparse, urljoin
from typing import NamedTuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    valid: bool
    reason: str
    normalized_url: Optional[str] = None

class URLValidator:
    def __init__(self):
        # Whitelisted domains (exactly as specified)
        self.whitelisted_domains = [
            'github.com',
            'gitlab.com', 
            'codeberg.org',
            'sr.ht',  # SourceHut
            'bitbucket.org',
            'npmjs.com',
            'crates.io',
            'pypi.org'
        ]
        
        # Wildcard patterns for gitea instances
        self.wildcard_patterns = [
            r'^.*\.gitea\.(com|org|io)$'  # *.gitea.com, *.gitea.org, *.gitea.io
        ]
        
        # Blocked domains (shorteners, commercial, social)
        self.blocked_domains = [
            'bit.ly', 't.co', 'tinyurl.com', 'goo.gl', 'is.gd', 'v.gd',  # Shorteners
            'gumroad.com', 'notion.so', 'medium.com', 'substack.com',  # Commercial
            'tiktok.com', 'instagram.com', 'youtube.com', 'twitter.com', 'facebook.com'  # Social
        ]
    
    def validate_url(self, url: str) -> ValidationResult:
        """
        Validate and normalize a URL for OSSWire submission.
        
        Args:
            url: The URL to validate
            
        Returns:
            ValidationResult with valid status, reason, and normalized URL
        """
        if not url:
            return ValidationResult(valid=False, reason="URL cannot be empty")
        
        # Normalize URL
        normalized_url = self._normalize_url(url)
        if not normalized_url:
            return ValidationResult(valid=False, reason="Invalid URL format")
        
        # Parse the normalized URL
        try:
            parsed = urlparse(normalized_url)
        except Exception:
            return ValidationResult(valid=False, reason="Invalid URL format")
        
        # Check for required HTTPS
        if parsed.scheme != 'https':
            return ValidationResult(
                valid=False, 
                reason="URL must use HTTPS protocol",
                normalized_url=normalized_url
            )
        
        # Extract domain
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check blocked domains first
        for blocked in self.blocked_domains:
            if domain == blocked or domain.endswith('.' + blocked):
                return ValidationResult(
                    valid=False,
                    reason=f"URLs from {blocked} are not allowed",
                    normalized_url=normalized_url
                )
        
        # Check whitelisted domains
        for whitelisted in self.whitelisted_domains:
            if domain == whitelisted or domain.endswith('.' + whitelisted):
                return ValidationResult(
                    valid=True,
                    reason="URL is from an approved OSS hosting service",
                    normalized_url=normalized_url
                )
        
        # Check wildcard patterns
        for pattern in self.wildcard_patterns:
            if re.match(pattern, domain):
                return ValidationResult(
                    valid=True,
                    reason="URL is from an approved OSS hosting service",
                    normalized_url=normalized_url
                )
        
        # If we get here, the domain is not whitelisted
        return ValidationResult(
            valid=False,
            reason=f"Domain '{domain}' is not in the approved list of OSS hosting services",
            normalized_url=normalized_url
        )
    
    def _normalize_url(self, url: str) -> Optional[str]:
        """
        Normalize URL to ensure it's a complete, valid URL.
        """
        # Remove whitespace
        url = url.strip()
        
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            return url
        except Exception:
            return None

# Create a global instance for easy use
url_validator = URLValidator()

def validate_oss_url(url: str) -> ValidationResult:
    """
    Convenience function to validate a URL for OSSWire submission.
    
    Args:
        url: The URL to validate
        
    Returns:
        ValidationResult with validation status and details
    """
    return url_validator.validate_url(url) 