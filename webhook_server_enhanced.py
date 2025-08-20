#!/usr/bin/env python3
"""
Enhanced webhook server for VerifyMyAge API callbacks
Handles both validation checks and actual callbacks
"""

from flask import Flask, request, jsonify, Response
import json
from datetime import datetime
import os

app = Flask(__name__)

# Store callbacks in memory and file
callbacks_received = []
CALLBACKS_FILE = "verifymyage_callbacks.json"

def load_callbacks():
    """Load existing callbacks from file"""
    if os.path.exists(CALLBACKS_FILE):
        try:
            with open(CALLBACKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_callback(callback_data):
    """Save callback to file"""
    callbacks = load_callbacks()
    callbacks.append(callback_data)
    with open(CALLBACKS_FILE, 'w') as f:
        json.dump(callbacks, f, indent=2)

@app.route('/', methods=['GET'])
def home():
    """Root endpoint - shows server status"""
    return jsonify({
        "service": "VerifyMyAge Webhook Server",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/": "Server status",
            "/callback": "Webhook endpoint for VerifyMyAge",
            "/webhooks": "View all received webhooks",
            "/health": "Health check endpoint"
        },
        "callbacks_received": len(callbacks_received)
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "webhook-server",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/callback', methods=['GET', 'POST', 'HEAD', 'OPTIONS'])
def callback():
    """
    Main webhook endpoint for VerifyMyAge
    Handles validation checks (GET/HEAD) and actual callbacks (POST)
    """
    
    # Handle OPTIONS for CORS preflight
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200
    
    # Handle HEAD requests (connection check)
    if request.method == 'HEAD':
        response = Response()
        response.headers['X-Webhook-Status'] = 'active'
        return response, 200
    
    # Handle GET requests (validation/status check)
    if request.method == 'GET':
        return jsonify({
            "status": "ready",
            "message": "Webhook is active and ready to receive callbacks",
            "timestamp": datetime.now().isoformat(),
            "callbacks_count": len(callbacks_received)
        }), 200
    
    # Handle POST requests (actual callbacks)
    if request.method == 'POST':
        try:
            # Get request data
            content_type = request.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                data = request.get_json()
            else:
                # Try to parse as JSON anyway
                raw_data = request.get_data(as_text=True)
                try:
                    data = json.loads(raw_data) if raw_data else {}
                except:
                    data = {"raw_data": raw_data}
            
            # Create callback record
            callback_record = {
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "headers": dict(request.headers),
                "url": request.url,
                "remote_addr": request.remote_addr,
                "data": data
            }
            
            # Store callback
            callbacks_received.append(callback_record)
            save_callback(callback_record)
            
            # Log to console
            print(f"\n{'='*60}")
            print(f"✅ CALLBACK RECEIVED at {callback_record['timestamp']}")
            print(f"{'='*60}")
            print(f"From: {request.remote_addr}")
            print(f"Method: {request.method}")
            print(f"Content-Type: {content_type}")
            
            if isinstance(data, dict):
                # Check if this is a batch result
                if 'batch_id' in data or 'results' in data:
                    print("\n📊 BATCH VERIFICATION RESULTS:")
                    print(json.dumps(data, indent=2))
                    
                    # Process batch results if present
                    if 'results' in data and isinstance(data['results'], list):
                        print(f"\nTotal emails processed: {len(data['results'])}")
                        adults = sum(1 for r in data['results'] if r.get('is_adult'))
                        print(f"Adults (18+): {adults}")
                        print(f"Minors: {len(data['results']) - adults}")
                        
                        # Save detailed results
                        results_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        with open(results_file, 'w') as f:
                            json.dump(data, f, indent=2)
                        print(f"\n📁 Results saved to: {results_file}")
                else:
                    print("\nData received:")
                    print(json.dumps(data, indent=2))
            else:
                print(f"\nRaw data: {data}")
            
            print(f"{'='*60}\n")
            
            # Return success response
            return jsonify({
                "status": "success",
                "message": "Callback received and processed",
                "timestamp": datetime.now().isoformat(),
                "callback_id": len(callbacks_received)
            }), 200
            
        except Exception as e:
            print(f"\n❌ Error processing callback: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

@app.route('/webhooks', methods=['GET'])
def get_webhooks():
    """View all received webhooks"""
    # Reload from file to get all historical callbacks
    all_callbacks = load_callbacks()
    
    return jsonify({
        "total": len(all_callbacks),
        "callbacks": all_callbacks[-10:],  # Last 10 callbacks
        "message": f"Showing last {min(10, len(all_callbacks))} of {len(all_callbacks)} callbacks"
    }), 200

@app.route('/webhooks/clear', methods=['POST'])
def clear_webhooks():
    """Clear all stored webhooks"""
    global callbacks_received
    callbacks_received = []
    
    # Clear file
    if os.path.exists(CALLBACKS_FILE):
        os.remove(CALLBACKS_FILE)
    
    return jsonify({
        "status": "cleared",
        "message": "All webhooks cleared"
    }), 200

@app.route('/test', methods=['GET', 'POST'])
def test():
    """Test endpoint to verify server is working"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.get_data(as_text=True)
        return jsonify({
            "status": "test successful",
            "method": "POST",
            "received": data
        }), 200
    
    return jsonify({
        "status": "test successful",
        "method": "GET",
        "message": "Server is working correctly"
    }), 200

def run_server(port=5002):
    """Run the enhanced webhook server"""
    print("\n" + "="*60)
    print("🚀 ENHANCED WEBHOOK SERVER FOR VERIFYMYAGE")
    print("="*60)
    print(f"Starting server on port {port}...")
    print(f"\nLocal endpoints:")
    print(f"  http://localhost:{port}/          - Server status")
    print(f"  http://localhost:{port}/callback  - Webhook endpoint")
    print(f"  http://localhost:{port}/webhooks  - View callbacks")
    print(f"  http://localhost:{port}/health    - Health check")
    print(f"\n⏳ Waiting for ngrok tunnel to be configured...")
    print(f"   Run: ngrok http {port}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    # Use port 5002 to avoid conflicts
    run_server(port=5002)