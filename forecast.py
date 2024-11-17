# forecast.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller

class Forecast:

    def check_stationarity(data):
        result = adfuller(data)
        p_value = result[1]
        if p_value < 0.05:
            return 0  
        else:
            return 1  

    
    
    def auto_select_sarimax_params(data, column, seasonal_period=12):
        best_aic = np.inf
        best_bic = np.inf
        best_order = None
        best_seasonal_order = None

        for p in range(1, 4):  
            for d in range(0, 2):
                for q in range(1, 4):
                    for P in range(1, 3):
                        for D in range(0, 2):
                            for Q in range(1, 3):
                                try:
                                    seasonal_order = (P, D, Q, seasonal_period)
                                    order = (p, d, q)
                                    model = SARIMAX(data[column], order=order, seasonal_order=seasonal_order)
                                    result = model.fit(disp=False)
                                    aic = result.aic
                                    bic = result.bic

                                    if aic < best_aic and bic < best_bic:
                                        best_aic = aic
                                        best_bic = bic
                                        best_order = order
                                        best_seasonal_order = seasonal_order
                                except Exception as e:
                                    continue

        return best_order, best_seasonal_order

    @staticmethod
    def forecast_data_sarimax(data, productline, date_col, column, forecast_months=6):
        try:

            data = data[data['PRODUCTLINE'] == productline]
            data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
            data = data.dropna(subset=[date_col])
            data.set_index(date_col, inplace=True)
            data = data.fillna(0)
            data = data.resample('M').sum()
            d = Forecast.check_stationarity(data[column])

            data['month'] = data.index.month
            data['lag1'] = data[column].shift(1)
            data['lag2'] = data[column].shift(2)
            data = data.dropna(subset=['lag1', 'lag2'])

            best_order, best_seasonal_order = Forecast.auto_select_sarimax_params(data, column)

            if best_order is None or best_seasonal_order is None:
                raise Exception("Unable to find optimal SARIMAX parameters.")

            exog = data[['month', 'lag1', 'lag2']] 
            model = SARIMAX(data[column], exog=exog, order=best_order, seasonal_order=best_seasonal_order)
            model_fit = model.fit(disp=False)

            forecast = model_fit.forecast(steps=forecast_months, exog=exog.tail(forecast_months))
            forecast = np.where(np.isfinite(forecast), forecast, 0)
            forecast = np.round(forecast).astype(int)


            return forecast
        except Exception as e:
            print(f"Error in forecasting: {e}")
            return None
