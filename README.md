# Volkswagen-OEM-Anomaly-Detection-Dashboard
[Hackathon] Real-time anomaly detection system for Volkswagen OEM manufacturing processes. This dashboard monitors key production metrics and alerts stakeholders when anomalies are detected.


## Installation

1. Clone the repository:
```bash
git clone https://github.com/MuthuPalaniappan925/Volkswagen-OEM-Anomaly-Detection-Dashboard.git
cd Volkswagen-OEM-Anomaly-Detection-Dashboard
```

2. Create and activate virtual environment (optional):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure Streamlit secrets:
Create `.streamlit/secrets.toml` with:
```toml
EMAIL_HOST = "your-smtp-server"
EMAIL_PORT = "587"
EMAIL_USER = "your-email@example.com"
EMAIL_PASSWORD = "your-password"
RECIPIENT_EMAILS = ["recipient1@example.com", "recipient2@example.com"]
```

## Usage

Run the dashboard:
```bash
streamlit run main.py
```


## License

This project is licensed under the MIT License - see the LICENSE file for details.