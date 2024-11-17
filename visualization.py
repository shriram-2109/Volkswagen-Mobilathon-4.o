import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
from typing import Dict, Any
from config import Config

class DashboardVisualizer:
    def __init__(self, config: Config):
        self.config = config
    
    def create_gauge(self, value: float, metric: str) -> go.Figure:
        settings = self.config.GAUGE_RANGES[metric]
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"{metric.replace('_', ' ').title()} ({settings['unit']})", 
                   'font': {'size': 24}},
            gauge={
                'axis': {'range': [settings['min'], settings['max']]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': settings['normal'], 'color': "#2ecc71"},
                    {'range': settings['danger'], 'color': "#e74c3c"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': settings['danger'][0]
                }
            }
        ))
        
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
        return fig
    
    def create_historical_plots(self, historical_data: pd.DataFrame) -> go.Figure:
        fig = sp.make_subplots(
            rows=3, cols=2,
            subplot_titles=("Machine Temperature", "Power Consumption",
                          "Vibration", "Pressure",
                          "Anomaly Score", "Anomalies in Temperature")
        )
        self._add_metric_trace(fig, historical_data, 'machine_temp', 1, 1)
        self._add_metric_trace(fig, historical_data, 'power_consumption', 1, 2, 'green')
        self._add_metric_trace(fig, historical_data, 'vibration', 2, 1, 'red')
        self._add_metric_trace(fig, historical_data, 'pressure', 2, 2, 'purple')
        self._add_metric_trace(fig, historical_data, 'anomaly_score', 3, 1, 'orange')
        
        self._add_temperature_anomalies(fig, historical_data)
        
        fig.update_layout(height=800, showlegend=True, template='plotly_white')
        return fig
    
    def _add_metric_trace(self, fig: go.Figure, data: pd.DataFrame, 
                         metric: str, row: int, col: int, color: str = None):
        trace_kwargs = {
            'y': data[metric],
            'mode': 'lines',
            'name': metric.replace('_', ' ').title()
        }
        if color:
            trace_kwargs['line'] = dict(color=color)
            
        fig.add_trace(go.Scatter(**trace_kwargs), row=row, col=col)
    
    def _add_temperature_anomalies(self, fig: go.Figure, data: pd.DataFrame):
        fig.add_trace(
            go.Scatter(y=data['machine_temp'], mode='lines', 
                      name='Temperature', showlegend=False),
            row=3, col=2
        )
        
        if not data[data['anomaly'] == 1].empty:
            fig.add_trace(
                go.Scatter(
                    x=data[data['anomaly'] == 1].index,
                    y=data[data['anomaly'] == 1]['machine_temp'],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='red', size=10, symbol='x')
                ),
                row=3, col=2
            )