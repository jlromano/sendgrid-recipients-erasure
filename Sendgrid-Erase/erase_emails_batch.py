#!/usr/bin/env python3
import os
import sys
import csv
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError

load_dotenv()

class SendGridBatchEraser:
    def __init__(self):
        self.api_key_1 = os.getenv("SENDGRID_API_KEY_1", "")
        self.api_key_2 = os.getenv("SENDGRID_API_KEY_2", "")
        
    def read_emails_from_file(self, filepath: str) -> List[str]:
        """Read and clean email addresses from CSV or text file."""
        emails = []
        try:
            # Check if it's a CSV file
            if filepath.endswith('.csv'):
                with open(filepath, 'r', newline='', encoding='utf-8') as f:
                    # Try to detect if it has headers
                    sample = f.read(1024)
                    f.seek(0)
                    has_header = csv.Sniffer().has_header(sample) if sample else False
                    
                    reader = csv.reader(f)
                    if has_header:
                        next(reader)  # Skip header
                    
                    for row in reader:
                        if row:  # Check if row is not empty
                            email = row[0].strip()  # Get first column
                            if email and '@' in email:
                                emails.append(email)
            else:
                # Plain text file
                with open(filepath, 'r') as f:
                    for line in f:
                        email = line.strip()
                        if email and '@' in email:
                            emails.append(email)
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
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
        """Erase multiple emails using Recipients' Data Erasure API."""
        import requests
        
        try:
            # Use the Recipients' Data Erasure API endpoint
            url = "https://api.sendgrid.com/v3/recipients/erasejob"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "email_addresses": emails  # Note: different field name for this endpoint
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)  # POST, not DELETE
            
            # Extract request IDs from headers and response body
            request_ids = {}
            
            # Common headers that contain request/trace IDs
            if 'X-Request-Id' in response.headers:
                request_ids['x_request_id'] = response.headers['X-Request-Id']
            if 'X-Message-Id' in response.headers:
                request_ids['x_message_id'] = response.headers['X-Message-Id']
            if 'X-Trace-Id' in response.headers:
                request_ids['x_trace_id'] = response.headers['X-Trace-Id']
            
            # Try to get job_id from response body if available
            if response.text:
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        if 'job_id' in response_data:
                            request_ids['job_id'] = response_data['job_id']
                        if 'id' in response_data:
                            request_ids['erasure_job_id'] = response_data['id']
                        if 'request_id' in response_data:
                            request_ids['request_id'] = response_data['request_id']
                except:
                    pass
            
            # Recipients' Data Erasure API returns 201 for successful job creation
            if response.status_code in [200, 201, 202, 204]:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "message": f"Successfully initiated erasure for {len(emails)} emails",
                    "emails_processed": emails,
                    "request_ids": request_ids,
                    "response_headers": dict(response.headers)
                }
            else:
                error_message = "Unknown error"
                if response.text:
                    try:
                        error_data = response.json()
                        if isinstance(error_data, dict):
                            error_message = error_data.get("errors", error_data.get("message", "Unknown error"))
                        else:
                            error_message = str(error_data)
                    except:
                        error_message = response.text
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_message,
                    "emails_attempted": emails,
                    "request_ids": request_ids,
                    "response_headers": dict(response.headers)
                }
                
        except requests.exceptions.RequestException as e:
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
                    # Print request IDs if available
                    request_ids = result.get('request_ids', {})
                    if request_ids:
                        print(f"  Request IDs:")
                        for id_type, id_value in request_ids.items():
                            print(f"    - {id_type}: {id_value}")
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
                    # Print request IDs if available
                    request_ids = result.get('request_ids', {})
                    if request_ids:
                        print(f"  Request IDs:")
                        for id_type, id_value in request_ids.items():
                            print(f"    - {id_type}: {id_value}")
                else:
                    print(f"✗ Failed: Status {result.get('status_code', 'N/A')}")
                    print(f"  Error: {result.get('error', 'Unknown error')}")
        
        if not self.api_key_1 and not self.api_key_2:
            print("\n✗ No API keys configured. Please set SENDGRID_API_KEY_1 and/or SENDGRID_API_KEY_2 in .env file")
            return
        
        # Generate report
        self.generate_report(emails, results)
    
    def generate_report(self, emails: List[str], results: Dict[str, Dict[str, Any]]):
        """Generate markdown report and JSON record."""
        timestamp = datetime.now()
        report_filename = f"erasure_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        json_filename = f"erasure_record_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        # Save JSON record with request details
        json_record = {
            "timestamp": timestamp.isoformat(),
            "emails_count": len(emails),
            "emails": emails,
            "results": {}
        }
        
        for integration, result in results.items():
            json_record["results"][integration] = {
                "success": result.get("success", False),
                "status_code": result.get("status_code"),
                "request_ids": result.get("request_ids", {}),
                "message": result.get("message") if result.get("success") else result.get("error")
            }
        
        with open(json_filename, 'w') as f:
            json.dump(json_record, f, indent=2)
        
        print(f"✓ JSON record saved to: {json_filename}")
        
        # Generate markdown report
        with open(report_filename, 'w') as f:
            f.write(f"# SendGrid Email Erasure Report\n\n")
            f.write(f"**Generated**: {timestamp.isoformat()}\n\n")
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
                    
                    # Add request IDs if available
                    request_ids = result.get('request_ids', {})
                    if request_ids:
                        f.write(f"\n#### Request IDs\n\n")
                        for id_type, id_value in request_ids.items():
                            f.write(f"- **{id_type}**: `{id_value}`\n")
                else:
                    f.write(f"- **Status**: ✗ Failed\n")
                    f.write(f"- **Status Code**: {result.get('status_code', 'N/A')}\n")
                    f.write(f"- **Error**: {result.get('error', 'Unknown error')}\n")
                    
                    # Add request IDs even for failed requests if available
                    request_ids = result.get('request_ids', {})
                    if request_ids:
                        f.write(f"\n#### Request IDs\n\n")
                        for id_type, id_value in request_ids.items():
                            f.write(f"- **{id_type}**: `{id_value}`\n")
                f.write("\n")
            
            f.write(f"## Notes\n\n")
            f.write(f"- Erasure jobs are created via Recipients' Data Erasure API\n")
            f.write(f"- Uses endpoint: POST /v3/recipients/erasejob\n")
            f.write(f"- Status 202 indicates job successfully accepted\n")
            f.write(f"- Status 201 indicates job successfully created\n")
            f.write(f"- Status 403 indicates insufficient API permissions\n")
            f.write(f"- Deleted emails cannot be recovered\n")
        
        print(f"\n✓ Report saved to: {report_filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Default to CSV file if available
        if os.path.exists("emails.csv"):
            filepath = "emails.csv"
        else:
            filepath = "emails-26082025.txt"
    
    eraser = SendGridBatchEraser()
    eraser.process_batch(filepath)