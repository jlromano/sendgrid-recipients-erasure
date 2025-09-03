#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any
from sendgrid import SendGridAPIClient
from python_http_client.exceptions import HTTPError

load_dotenv()

class SendGridBatchEraser:
    def __init__(self):
        self.api_key_1 = os.getenv("SENDGRID_API_KEY_1", "")
        self.api_key_2 = os.getenv("SENDGRID_API_KEY_2", "")
        
    def read_emails_from_file(self, filepath: str) -> List[str]:
        """Read and clean email addresses from file."""
        emails = []
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    email = line.strip()
                    if email and '@' in email:
                        emails.append(email)
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            sys.exit(1)
        return emails
    
    def test_api_connection(self, api_key: str, integration_name: str) -> bool:
        """Test API connection using SDK."""
        try:
            sg = SendGridAPIClient(api_key)
            response = sg.client.user.profile.get()
            
            if response.status_code == 200:
                print(f"✓ {integration_name}: API connection successful")
                return True
            else:
                print(f"✗ {integration_name}: API connection failed (Status: {response.status_code})")
                return False
        except HTTPError as e:
            print(f"✗ {integration_name}: API error - Status: {e.status_code}")
            return False
        except Exception as e:
            print(f"✗ {integration_name}: Connection error - {e}")
            return False
    
    def erase_emails(self, emails: List[str], api_key: str, integration_name: str) -> Dict[str, Any]:
        """Erase multiple emails using SendGrid SDK."""
        try:
            sg = SendGridAPIClient(api_key)
            
            data = {
                "emails": emails
            }
            
            response = sg.client.suppression.emails.delete(request_body=data)
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "status_code": 204,
                    "message": f"Successfully deleted {len(emails)} emails",
                    "emails_processed": emails
                }
            else:
                error_message = "Unknown error"
                if response.body:
                    try:
                        error_data = json.loads(response.body)
                        error_message = error_data.get("errors", error_data.get("message", "Unknown error"))
                    except:
                        error_message = response.body
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_message,
                    "emails_attempted": emails
                }
                
        except HTTPError as e:
            error_message = "HTTP Error"
            if hasattr(e, 'body') and e.body:
                try:
                    error_data = json.loads(e.body)
                    error_message = error_data.get("errors", error_data.get("message", str(e)))
                except:
                    error_message = str(e)
            
            return {
                "success": False,
                "status_code": e.status_code if hasattr(e, 'status_code') else None,
                "error": error_message,
                "emails_attempted": emails
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {e}",
                "emails_attempted": emails
            }
    
    def process_batch(self, filepath: str):
        """Process batch erasure from file."""
        print(f"\n{'='*60}")
        print(f"SendGrid Batch Email Erasure")
        print(f"{'='*60}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"File: {filepath}")
        
        # Read emails
        emails = self.read_emails_from_file(filepath)
        print(f"\nFound {len(emails)} valid email addresses")
        
        if not emails:
            print("No valid emails found to process.")
            return
        
        print("\nEmails to be erased:")
        for i, email in enumerate(emails, 1):
            print(f"  {i}. {email}")
        
        # Process with available API keys
        results = {}
        
        if self.api_key_1:
            print(f"\n{'='*60}")
            print("Processing with Integration 1")
            print(f"{'='*60}")
            
            if self.test_api_connection(self.api_key_1, "Integration 1"):
                result = self.erase_emails(emails, self.api_key_1, "Integration 1")
                results["Integration 1"] = result
                
                if result["success"]:
                    print(f"✓ Success: {result['message']}")
                else:
                    print(f"✗ Failed: Status {result.get('status_code', 'N/A')}")
                    print(f"  Error: {result.get('error', 'Unknown error')}")
        
        if self.api_key_2:
            print(f"\n{'='*60}")
            print("Processing with Integration 2")
            print(f"{'='*60}")
            
            if self.test_api_connection(self.api_key_2, "Integration 2"):
                result = self.erase_emails(emails, self.api_key_2, "Integration 2")
                results["Integration 2"] = result
                
                if result["success"]:
                    print(f"✓ Success: {result['message']}")
                else:
                    print(f"✗ Failed: Status {result.get('status_code', 'N/A')}")
                    print(f"  Error: {result.get('error', 'Unknown error')}")
        
        if not self.api_key_1 and not self.api_key_2:
            print("\n✗ No API keys configured. Please set SENDGRID_API_KEY_1 and/or SENDGRID_API_KEY_2 in .env file")
            return
        
        # Generate report
        self.generate_report(emails, results)
    
    def generate_report(self, emails: List[str], results: Dict[str, Dict[str, Any]]):
        """Generate markdown report."""
        report_filename = f"erasure_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_filename, 'w') as f:
            f.write(f"# SendGrid Email Erasure Report\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Emails Processed**: {len(emails)}\n")
            f.write(f"- **Integrations Tested**: {len(results)}\n\n")
            
            f.write(f"## Emails Processed\n\n")
            for i, email in enumerate(emails, 1):
                f.write(f"{i}. {email}\n")
            
            f.write(f"\n## Results by Integration\n\n")
            
            for integration, result in results.items():
                f.write(f"### {integration}\n\n")
                if result["success"]:
                    f.write(f"- **Status**: ✓ Success\n")
                    f.write(f"- **Status Code**: {result.get('status_code', 'N/A')}\n")
                    f.write(f"- **Message**: {result.get('message', 'N/A')}\n")
                else:
                    f.write(f"- **Status**: ✗ Failed\n")
                    f.write(f"- **Status Code**: {result.get('status_code', 'N/A')}\n")
                    f.write(f"- **Error**: {result.get('error', 'Unknown error')}\n")
                f.write("\n")
            
            f.write(f"## Notes\n\n")
            f.write(f"- Erasure requests are processed immediately by SendGrid\n")
            f.write(f"- Deleted emails cannot be recovered\n")
            f.write(f"- Status 204 indicates successful deletion\n")
            f.write(f"- Status 403 indicates insufficient API permissions\n")
        
        print(f"\n✓ Report saved to: {report_filename}")

if __name__ == "__main__":
    eraser = SendGridBatchEraser()
    eraser.process_batch("emails-26082025.txt")