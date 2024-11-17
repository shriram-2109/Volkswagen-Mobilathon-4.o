import streamlit as st
import time
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from config import Config
from data_simulator import DataSimulator
from anomaly_detector import AnomalyDetector
from alert_manager import AlertManager
from visualization import DashboardVisualizer
from forecast import Forecast


warnings.filterwarnings('ignore')



class AnomalyDashboard:
    def __init__(self):
        """Initialize the dashboard components and configurations."""
        self.config = Config()
        self.simulator = DataSimulator()
        self.detector = AnomalyDetector(
            "model_card/isolation_forest_model.pkl",
            "model_card/scaler.pkl"
        )
        self.alert_manager = AlertManager(self.config)
        self.visualizer = DashboardVisualizer(self.config)
        self.historical_data = pd.DataFrame()
        self.forecast_data = None
    
    def setup_page(self):
        """Configure the Streamlit page layout and title."""
        st.set_page_config(
            page_title="Volkswagen OEMs Anomaly Detection",
            page_icon="🏭",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        tab1, tab2 = st.tabs(["🔍 Anomaly Detection", "📈 Forecasting"])
        
        with tab1:
            st.title("🏭 Volkswagen OEMs Anomaly Detection Dashboard")
        
        with tab2:
            st.title("📈 Production Forecasting Dashboard")
            self.setup_forecasting()
    
    def setup_forecasting(self):

        st.write("This dashboard allows you to select a product line and view a forecast of its values.")

        try:
            data = pd.read_csv(r"Path_to_dataset")

            productline = st.selectbox("Select Product Line", data['PRODUCTLINE'].unique())
            column = 'SALES'

            filtered_data = data[data['PRODUCTLINE'] == productline]
            filtered_data['ORDERDATE'] = pd.to_datetime(filtered_data['ORDERDATE'])
            monthly_data = filtered_data.resample('M', on='ORDERDATE').sum()
            forecast_months = st.slider("Select number of months to forecast", 1, 12, 6)

            if st.button("Generate Forecast"):
                forecast = Forecast.forecast_data_sarimax(data, productline, 'ORDERDATE', column, forecast_months)
                forecast_df = pd.DataFrame(
                    forecast, 
                    columns=[column], 
                    index=pd.date_range(data['ORDERDATE'].max(), periods=forecast_months + 1, freq='M')[1:]
                )

                st.write("Forecasted values for the next months:")
                st.write(forecast_df)

                if forecast is not None:

                    plt.figure(figsize=(8, 5))
                    plt.plot(monthly_data.index, monthly_data[column], label='Actual', color='green', linewidth=2)
                    plt.plot(forecast_df.index, forecast_df[column], label='Forecast', color='red', linewidth=2)
                    plt.title(f'{column} Forecast for {productline}', fontsize=14, color='white')
                    plt.xlabel('Date', fontsize=12, color='white')
                    plt.ylabel(column, fontsize=12, color='white')
                    plt.legend(facecolor='black', edgecolor='white', fontsize=10, labelcolor='white')
                    ax = plt.gca()  
                    ax.patch.set_alpha(0)  
                    plt.gcf().patch.set_alpha(0)
                    ax.tick_params(colors='white', labelsize=10)
                    plt.tight_layout()
                    st.pyplot(plt)
                
                else:
                    st.error("Forecasting failed. Please check the dataset or parameters.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    def setup_sidebar(self) -> tuple:
        """Configure the sidebar settings."""
        st.sidebar.title("⚙️ Dashboard Settings")
        st.sidebar.markdown("---")
        
        refresh_rate = st.sidebar.slider(
            "📊 Refresh Interval (seconds)",
            self.config.REFRESH_RATE_MIN,
            self.config.REFRESH_RATE_MAX,
            self.config.REFRESH_RATE_DEFAULT,
            help="Select how often the dashboard should update"
        )
        
        email_alerts = st.sidebar.checkbox(
            "📧 Enable Email Alerts",
            True,
            help="Send email notifications when anomalies are detected"
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 System Information")
        st.sidebar.info(f"""
        - Monitoring Active: Yes
        - Last Update: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        
        return refresh_rate, email_alerts
    
    def update_data(self, new_data: pd.DataFrame):
        """
        Process new data and update historical records.
        
        Args:
            new_data (pd.DataFrame): New sensor readings
            
        Returns:
            tuple: (is_anomaly, anomaly_score)
        """
        
        is_anomaly, anomaly_score = self.detector.detect(
            new_data[[
                'machine_temp', 'power_consumption', 'vibration', 'pressure',
                'production_rate', 'cycle_time', 'lubricant_level'
            ]]
        )
        
        new_data['anomaly'] = int(is_anomaly)
        new_data['anomaly_score'] = anomaly_score[0]
        new_data['timestamp'] = pd.Timestamp.now()
        
        self.historical_data = pd.concat(
            [self.historical_data, new_data],
            ignore_index=True
        )
     
        if len(self.historical_data) > self.config.HISTORICAL_DATA_LIMIT:
            self.historical_data = self.historical_data.tail(
                self.config.HISTORICAL_DATA_LIMIT
            )
        
        return is_anomaly, anomaly_score[0]
    
    def display_metrics(self, data: pd.DataFrame, is_anomaly: bool, anomaly_score: float):
        """Display the current metrics in the dashboard."""
        st.subheader("📊 Production Status")
        cols = st.columns(4)
        
        status_icon = "🔴" if is_anomaly else "🟢"
        
        metrics = [
            ("Production Rate", f"{data['production_rate'].iloc[0]:.1f} units/hour"),
            ("Cycle Time", f"{data['cycle_time'].iloc[0]:.1f} seconds"),
            ("Lubricant Level", f"{data['lubricant_level'].iloc[0]:.1f}%"),
            ("System Status", f"{status_icon} {'Anomaly' if is_anomaly else 'Normal'}")
        ]
        
        for col, (label, value) in zip(cols, metrics):
            if label == "System Status":
                col.metric(
                    label=label,
                    value=value,
                    delta=f"Score: {anomaly_score:.2f}",
                    delta_color="inverse" if is_anomaly else "normal"
                )
            else:
                col.metric(label=label, value=value)
    
    def update_dashboard(self, metrics_placeholder, gauges_placeholder, 
                        plots_placeholder, new_data, is_anomaly, anomaly_score):
        """Update all dashboard components with new data."""
        
        with gauges_placeholder.container():
            st.subheader("🔍 Real-Time Metrics")
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns(4)
            
            for i, metric in enumerate(['machine_temp', 'power_consumption', 
                                      'vibration', 'pressure']):
                with cols[i]:
                    fig = self.visualizer.create_gauge(
                        new_data[metric].iloc[0],
                        metric
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with metrics_placeholder.container():
            self.display_metrics(new_data, is_anomaly, anomaly_score)
        
        with plots_placeholder.container():
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📈 Production Historical Trends")
            fig = self.visualizer.create_historical_plots(self.historical_data)
            st.plotly_chart(fig, use_container_width=True)
    
    def handle_anomaly_alert(self, new_data: pd.DataFrame, anomaly_score: float, 
                           email_alerts: bool):
        """Handle anomaly detection and alert sending."""
        if email_alerts:
            success, message = self.alert_manager.send_alert(
                new_data,
                anomaly_score,
                self.historical_data
            )
            
            if success:
                st.sidebar.success("✅ Anomaly alert sent successfully!")
            else:
                st.sidebar.error(f"❌ Failed to send alert: {message}")
    
    def run(self):
        """Main application loop."""
        try:
            self.setup_page()
            refresh_rate, email_alerts = self.setup_sidebar()
            
            metrics_placeholder = st.empty()
            gauges_placeholder = st.empty()
            plots_placeholder = st.empty()
            
            # Main loop
            while True:
                try:
                    new_data = self.simulator.generate_data()
                    is_anomaly, anomaly_score = self.update_data(new_data)
                    
                    if is_anomaly:
                        self.handle_anomaly_alert(new_data, anomaly_score, email_alerts)
                    
                    self.update_dashboard(
                        metrics_placeholder,
                        gauges_placeholder,
                        plots_placeholder,
                        new_data,
                        is_anomaly,
                        anomaly_score
                    )
    
                    time.sleep(refresh_rate)
                    
                except Exception as e:
                    st.error(f"Error in dashboard update: {str(e)}")
                    time.sleep(refresh_rate)
                    
        except Exception as e:
            st.error(f"Critical error in dashboard: {str(e)}")
            st.stop()
            

if __name__ == "__main__":
    dashboard = AnomalyDashboard()
    dashboard.run()