import streamlit as st

class Config:
    EMAIL_HOST = st.secrets["EMAIL_HOST"]
    EMAIL_PORT = int(st.secrets["EMAIL_PORT"])
    EMAIL_USER = st.secrets["EMAIL_USER"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    RECIPIENT_EMAILS = st.secrets["RECIPIENT_EMAILS"]
    
    ##Dashboard settings
    REFRESH_RATE_MIN = 1
    REFRESH_RATE_MAX = 10
    REFRESH_RATE_DEFAULT = 5
    HISTORICAL_DATA_LIMIT = 100
    
    GAUGE_RANGES = {
        'machine_temp': {'min': 0, 'max': 100, 'normal': (50, 80), 'danger': (80, 100), 'unit': '°C'},
        'power_consumption': {'min': 0, 'max': 15, 'normal': (5, 10), 'danger': (10, 15), 'unit': 'kW'},
        'vibration': {'min': 0, 'max': 3, 'normal': (0, 1.5), 'danger': (1.5, 3), 'unit': 'mm/s'},
        'pressure': {'min': 0, 'max': 50, 'normal': (20, 35), 'danger': (35, 50), 'unit': 'Pa'}
    }