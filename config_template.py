"""
VerifyMyAge API Configuration Template
Replace the placeholder values with your actual credentials
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Credentials - Get these from VerifyMyAge dashboard
API_KEY = os.getenv('VERIFYMYAGE_API_KEY', 'your-api-key-here')
API_SECRET = os.getenv('VERIFYMYAGE_API_SECRET', 'your-api-secret-here')

# Environment URLs
SANDBOX_URL = "https://email.sandbox.verifymyage.com"
PRODUCTION_URL = "https://email.verification.verifymyage.com"

# Select environment (SANDBOX_URL for testing, PRODUCTION_URL for live)
BASE_URL = os.getenv('VERIFYMYAGE_ENVIRONMENT', PRODUCTION_URL)

# API Endpoints
ESTIMATE_ENDPOINT = "/api/v1/estimate"
BATCH_ESTIMATE_ENDPOINT = "/api/v1/estimate/batch"
STATUS_ENDPOINT = "/v2/age_assurance/verification/{id}/status"

# Webhook Configuration
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '5002'))
NGROK_DOMAIN = os.getenv('NGROK_DOMAIN', '')  # Optional: custom ngrok domain

# GitHub Configuration for CSV hosting
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'your-github-username')
REPO_NAME = os.getenv('GITHUB_REPO', 'email-batch-tests')
CSV_FILENAME = os.getenv('CSV_FILENAME', 'emails_to_verify.csv')