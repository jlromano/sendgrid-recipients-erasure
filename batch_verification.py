#!/usr/bin/env python3
"""
VerifyMyAge Batch Email Verification Script
Processes multiple emails using the batch API with webhook callback
"""

import hashlib
import hmac
import json
import requests
import time
from datetime import datetime
from config_template import (
    API_KEY, API_SECRET, BASE_URL, 
    BATCH_ESTIMATE_ENDPOINT, 
    GITHUB_USERNAME, REPO_NAME, CSV_FILENAME
)


class BatchVerification:
    def __init__(self, webhook_url):
        """
        Initialize batch verification
        
        Args:
            webhook_url: Public webhook URL to receive results
        """
        self.webhook_url = webhook_url
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.base_url = BASE_URL
        
    def _generate_hmac(self, payload):
        """Generate HMAC-SHA256 signature for authentication"""
        message = bytes(payload, 'utf-8')
        secret = bytes(self.api_secret, 'utf-8')
        return hmac.new(secret, message, hashlib.sha256).hexdigest()
    
    def verify_webhook(self):
        """Test if webhook is accessible"""
        try:
            response = requests.get(f"{self.webhook_url}", timeout=5)
            if response.status_code == 200:
                print(f"✅ Webhook is accessible: {self.webhook_url}")
                return True
            else:
                print(f"⚠️ Webhook returned status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot reach webhook: {e}")
            return False
    
    def create_batch_job(self, csv_url):
        """
        Create a batch verification job
        
        Args:
            csv_url: Public URL to CSV file with emails
            
        Returns:
            Batch job details or None if failed
        """
        # Prepare request
        payload = {
            "file_url": csv_url,
            "callback_url": f"{self.webhook_url}/callback"
        }
        
        payload_json = json.dumps(payload)
        hmac_signature = self._generate_hmac(payload_json)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"hmac {self.api_key}:{hmac_signature}"
        }
        
        url = f"{self.base_url}{BATCH_ESTIMATE_ENDPOINT}"
        
        print(f"\n📤 Sending batch request to VerifyMyAge...")
        print(f"   CSV URL: {csv_url}")
        print(f"   Callback URL: {self.webhook_url}/callback")
        
        try:
            response = requests.post(url, headers=headers, data=payload_json, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                batch_id = result.get('batch_id', result.get('id', 'N/A'))
                
                print(f"\n✅ Batch job created successfully!")
                print(f"   Batch ID: {batch_id}")
                print(f"   Status: {result.get('status', 'N/A')}")
                
                # Save job details
                self._save_job_details(batch_id, result, csv_url)
                
                return result
            else:
                print(f"\n❌ Request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            return None
    
    def _save_job_details(self, batch_id, result, csv_url):
        """Save job details to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"batch_job_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "batch_id": batch_id,
                "job_info": result,
                "csv_url": csv_url,
                "callback_url": self.webhook_url,
                "timestamp": timestamp
            }, f, indent=2)
        
        print(f"   📁 Job details saved to: {filename}")
    
    def monitor_results(self, max_wait=30):
        """
        Monitor webhook for results
        
        Args:
            max_wait: Maximum seconds to wait for results
        """
        print(f"\n⏳ Monitoring for results (max {max_wait} seconds)...")
        print(f"   Check webhook at: {self.webhook_url}/webhooks")
        
        elapsed = 0
        check_interval = 5
        
        while elapsed < max_wait:
            time.sleep(check_interval)
            elapsed += check_interval
            
            try:
                response = requests.get(f"{self.webhook_url}/webhooks", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    total = data.get('total', 0)
                    
                    if total > 0:
                        print(f"\n✅ Received {total} callback(s)!")
                        self._process_callbacks(data.get('callbacks', []))
                        return True
                    
                print(f"   Waiting... ({elapsed}s elapsed)", end='\r')
            except:
                pass
        
        print(f"\n⏳ No results received after {max_wait} seconds")
        print("   Results may still be processing. Check webhook server.")
        return False
    
    def _process_callbacks(self, callbacks):
        """Process received callbacks"""
        for callback in callbacks[-1:]:  # Process latest callback
            data = callback.get('data', {})
            
            if 'report_url' in data:
                print(f"\n📊 Batch results received!")
                print(f"   Report URL: {data['report_url'][:80]}...")
                print(f"   Expires in: {data.get('expires_in_minutes', 'N/A')} minutes")
                
                # Optionally download and display results
                self._download_results(data['report_url'])
    
    def _download_results(self, report_url):
        """Download and display batch results"""
        try:
            response = requests.get(report_url)
            if response.status_code == 200:
                filename = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                with open(filename, 'w') as f:
                    f.write(response.text)
                
                print(f"   📁 Results saved to: {filename}")
                
                # Display summary
                lines = response.text.strip().split('\n')
                if len(lines) > 1:
                    print(f"\n   Summary: {len(lines)-1} emails processed")
                    print("   Sample results:")
                    for line in lines[1:4]:  # Show first 3 results
                        print(f"     • {line}")
        except Exception as e:
            print(f"   ⚠️ Could not download results: {e}")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("🚀 VERIFYMYAGE BATCH EMAIL VERIFICATION")
    print("="*60)
    
    # Check configuration
    if API_KEY == 'your-api-key-here':
        print("\n❌ Please configure your API credentials in .env file")
        print("   Copy .env.example to .env and add your credentials")
        return
    
    # Get webhook URL from user or environment
    webhook_url = input("\nEnter your webhook URL (e.g., https://abc123.ngrok.app): ").strip()
    
    if not webhook_url.startswith('http'):
        print("❌ Invalid webhook URL. Must start with http:// or https://")
        return
    
    # Construct CSV URL
    csv_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/{CSV_FILENAME}"
    
    # Initialize batch verification
    batch = BatchVerification(webhook_url)
    
    # Verify webhook is accessible
    if not batch.verify_webhook():
        print("\n⚠️ Webhook may not be accessible. Continue anyway? (y/n): ", end='')
        if input().lower() != 'y':
            return
    
    # Create batch job
    result = batch.create_batch_job(csv_url)
    
    if result:
        # Monitor for results
        batch.monitor_results(max_wait=30)
        
        print("\n" + "="*60)
        print("✅ Batch verification initiated successfully!")
        print("   Monitor your webhook server for complete results")
        print("="*60)
    else:
        print("\n❌ Batch verification failed. Check error messages above.")


if __name__ == "__main__":
    main()