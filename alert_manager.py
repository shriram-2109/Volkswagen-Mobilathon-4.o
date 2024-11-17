import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Tuple
from config import Config
import pandas as pd

class AlertManager:
    def __init__(self, config: Config):
        self.config = config
    
    def send_alert(self, data_point: pd.DataFrame, anomaly_score: float, 
                   historical_data: pd.DataFrame) -> Tuple[bool, str]:
        try:
            msg = self._create_email_message(data_point, anomaly_score, historical_data)
            
            with smtplib.SMTP(self.config.EMAIL_HOST, self.config.EMAIL_PORT) as server:
                server.starttls()
                server.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
                server.send_message(msg)
            
            return True, "Alert sent successfully"
        except Exception as e:
            return False, f"Failed to send alert: {str(e)}"
    
    def _create_email_message(self, data_point: pd.DataFrame, anomaly_score: float,
                            historical_data: pd.DataFrame) -> MIMEMultipart:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'⚠️ ANOMALY DETECTED - Score: {anomaly_score:.2f} | OEM Risk Team | Updates'
        msg['From'] = self.config.EMAIL_USER
        msg['To'] = ', '.join(self.config.RECIPIENT_EMAILS)
        
        html_content = self._generate_alert_html(data_point, anomaly_score, historical_data)
        msg.attach(MIMEText(html_content, 'html'))
        return msg
    
    def _generate_alert_html(self, data_point: pd.DataFrame, anomaly_score: float,
                           historical_data: pd.DataFrame) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""
        <html>
        <body>
            <h2>⚠️ Anomaly Detection Alert</h2>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <p><strong>Anomaly Score:</strong> {anomaly_score:.2f}</p>
            
            <h3>Current Metrics</h3>
            <ul>
                <li>Machine Temperature: {data_point['machine_temp'].iloc[0]:.2f}°C</li>
                <li>Power Consumption: {data_point['power_consumption'].iloc[0]:.2f}kW</li>
                <li>Vibration: {data_point['vibration'].iloc[0]:.2f}mm/s</li>
                <li>Pressure: {data_point['pressure'].iloc[0]:.2f}Pa</li>
                <li>Production Rate: {data_point['production_rate'].iloc[0]:.2f}units/hour</li>
                <li>Cycle Time: {data_point['cycle_time'].iloc[0]:.2f}s</li>
                <li>Lubricant Level: {data_point['lubricant_level'].iloc[0]:.2f}%</li>
            </ul>
            
            <h3>Statistical Summary</h3>
            <ul>
                <li>Temperature Change (last 5 min): {(data_point['machine_temp'].iloc[0] - historical_data['machine_temp'].tail(5).mean()):.2f}°C</li>
                <li>Power Fluctuation: {historical_data['power_consumption'].tail(5).std():.2f}kW</li>
                <li>Average Vibration (last 5 min): {historical_data['vibration'].tail(5).mean():.2f}mm/s</li>
            </ul>
            
            <p><strong>Please investigate immediately!</strong></p>
            <br><br>
            <p><em>Regards,</em><br><strong>OEM Risk Team</strong></p>
        </body>
        </html>
        """