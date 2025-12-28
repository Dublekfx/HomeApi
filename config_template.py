"""Security configuration for Home API"""

# API Key - change this to something unique and keep it secret
API_KEY = "Insert API key here"

# Allowed IP addresses (empty list = allow all)
# Examples: ["192.168.68.1", "192.168.1.50"]
ALLOWED_IPS = []

# SSL/TLS settings
SSL_CERT = "cert.pem"
SSL_KEY = "key.pem"
USE_HTTPS = True

# Tapo configuration
SWITCHES = {
    "bedroom": "192.168.1.xx",
    "icicles": "192.168.1.xx",
    "tree": "192.168.1.xx",
    "office": "192.168.1.xx"
}
USER="user@gmail.com"
PW="pass"
