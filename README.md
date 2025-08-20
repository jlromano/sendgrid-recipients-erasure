# VerifyMyAge Email Batch Verification System

A complete Python implementation for batch email age verification using the VerifyMyAge API, including webhook server setup and ngrok integration.

## 🚀 Features

- **Batch Email Verification**: Process multiple emails in a single API call
- **Webhook Server**: Fully functional webhook server to receive verification results
- **Ngrok Integration**: Easy local testing with public URL exposure
- **HMAC Authentication**: Secure API communication
- **CSV Support**: Upload email lists via GitHub or other public hosting
- **Result Processing**: Automatic handling and storage of verification results

## 📋 Prerequisites

- Python 3.7+
- VerifyMyAge API credentials (get them at [VerifyMyAge Dashboard](https://dashboard.verifymyage.com))
- Ngrok account (free at [ngrok.com](https://ngrok.com))
- GitHub account (for CSV hosting)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/jlromano/email-batch-tests.git
cd email-batch-tests
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

## ⚙️ Configuration

### 1. VerifyMyAge API Credentials

Edit `.env` file with your credentials:
```env
VERIFYMYAGE_API_KEY=your-api-key-here
VERIFYMYAGE_API_SECRET=your-api-secret-here
VERIFYMYAGE_ENVIRONMENT=https://email.verification.verifymyage.com
```

### 2. Ngrok Setup

Install and configure ngrok:
```bash
# Install ngrok (macOS)
brew install ngrok

# Or download from https://ngrok.com/download

# Add your auth token
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 3. CSV File Setup

1. Edit `emails_example.csv` with your email list
2. Commit and push to GitHub:
```bash
git add emails_example.csv
git commit -m "Update email list"
git push
```

Your CSV will be available at:
```
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/emails_example.csv
```

## 📝 Usage

### Step 1: Start the Webhook Server

```bash
python webhook_server_enhanced.py
```

The server will start on port 5002 with endpoints:
- `/callback` - Receives verification results
- `/health` - Health check
- `/webhooks` - View all received callbacks

### Step 2: Start Ngrok Tunnel

In a new terminal:
```bash
ngrok http 5002
```

Note the public URL (e.g., `https://abc123.ngrok.app`)

### Step 3: Run Batch Verification

Update the webhook URL in the script and run:
```bash
python batch_verification.py
```

### Step 4: Monitor Results

Results will be:
1. Displayed in the webhook server console
2. Saved to `verifymyage_callbacks.json`
3. Available at `http://localhost:5002/webhooks`

## 📁 Project Structure

```
email-batch-tests/
├── webhook_server_enhanced.py   # Webhook server implementation
├── batch_verification.py        # Main batch verification script
├── config_template.py           # Configuration template
├── emails_example.csv          # Example email list
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## 🔧 API Endpoints

### Individual Verification
```python
POST /api/v1/estimate
{
  "email": "user@example.com"
}
```

### Batch Verification
```python
POST /api/v1/estimate/batch
{
  "file_url": "https://example.com/emails.csv",
  "callback_url": "https://your-webhook.com/callback"
}
```

## 📊 Response Format

### Individual Response
```json
{
  "id": "verification_id",
  "minimum_age": 18,
  "is_adult": true
}
```

### Batch Callback
```json
{
  "batch_id": "batch_id",
  "report_url": "https://storage.googleapis.com/..."
}
```

The report URL contains a CSV with:
```csv
Email,Minimum Age,Is Adult,Verification ID
email@example.com,18,true,verification_id
```

## 🚨 Troubleshooting

### "invalid callback url" Error
- Ensure webhook is publicly accessible
- Use HTTPS (not HTTP)
- Verify ngrok is running and forwarding correctly

### No Callbacks Received
- Check webhook server console for errors
- Verify CSV format is correct
- Ensure API credentials are valid

### Connection Issues
- Check firewall settings
- Verify ngrok tunnel is active
- Test webhook endpoint manually: `curl https://your-ngrok-url/health`

## 🔒 Security Notes

- **Never commit API credentials** - Use environment variables
- **Rotate API keys regularly**
- **Use HTTPS for all webhook URLs**
- **Validate webhook signatures** in production
- **Store results securely**

## 📈 Rate Limits

- Individual API: 1000 requests/minute
- Batch API: 100,000 emails per batch (production)
- Batch API: 1,000 emails per batch (sandbox)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- VerifyMyAge Documentation: [docs.verifymyage.com](https://docs.verifymyage.com)
- API Support: support@verifymyage.com
- GitHub Issues: [Create an issue](https://github.com/jlromano/email-batch-tests/issues)

## 🙏 Acknowledgments

- VerifyMyAge for the API
- Ngrok for tunnel services
- Flask for the webhook server

---

**Note**: This is a demonstration project. For production use, implement proper error handling, logging, and security measures.