import re
from urllib.parse import urlparse
from typing import Dict, Tuple, Optional

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    if not url:
        return "osswire.com"
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return "osswire.com"

def determine_thumbnail_type(url: str, title: str, content: str) -> Tuple[str, str]:
    """
    Determine the appropriate thumbnail type and URL based on content.
    Returns (thumbnail_type, thumbnail_url)
    """
    if not url:
        return "default", None
    
    domain = extract_domain(url)
    
    # Only whitelisted domains get special treatment
    whitelisted_domains = ['github.com', 'gitlab.com', 'codeberg.org', 'sr.ht', 'bitbucket.org', 
                          'npmjs.com', 'crates.io', 'pypi.org']
    
    if any(whitelisted_domain in domain for whitelisted_domain in whitelisted_domains):
        return "code", None
    
    # Everything else gets default treatment
    return "default", None

def get_thumbnail_data(post) -> Dict:
    """Generate thumbnail data for a post."""
    if not post.url:
        return {
            "type": "default",
            "url": None,
            "domain": "osswire.com",
            "color": "#0891b2"
        }
    
    domain = extract_domain(post.url)
    thumbnail_type, thumbnail_url = determine_thumbnail_type(post.url, post.title, post.content)
    
    # Generate domain-based colors
    domain_colors = {
        "github.com": "#24292e",
        "gitlab.com": "#fc6d26",
        "codeberg.org": "#d71a1b",
        "sr.ht": "#5bc0de",
        "bitbucket.org": "#0052cc",
        "npmjs.com": "#cb3837",
        "crates.io": "#dea584",
        "pypi.org": "#3775a4",
        "osswire.com": "#0891b2"
    }
    
    color = domain_colors.get(domain, "#0891b2")
    
    return {
        "type": thumbnail_type,
        "url": thumbnail_url,
        "domain": domain,
        "color": color
    }

def generate_thumbnail_html(thumbnail_data: Dict) -> str:
    """Generate HTML for thumbnail display."""
    thumbnail_type = thumbnail_data["type"]
    domain = thumbnail_data["domain"]
    color = thumbnail_data["color"]
    
    # Domain initials (first two letters)
    domain_initials = domain[:2].upper() if len(domain) >= 2 else domain.upper()
    
    if thumbnail_type == "code":
        return f"""
        <div class="post-thumbnail code-thumbnail" style="background: {color};">
            <div class="code-icon">{domain_initials}</div>
        </div>
        """
    else:  # default
        return f"""
        <div class="post-thumbnail website-thumbnail" style="background: {color};">
            <div class="website-icon">{domain_initials}</div>
        </div>
        """ 