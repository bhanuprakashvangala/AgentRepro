import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

def generate_synthetic_data():
    """Generates a non-stationary time series with trend and seasonality."""
    np.random.seed(42)
    dates = pd.date_range(start='2021-01-01', periods=150, freq='D')
    
    # Trend + Seasonality + Noise
    trend = np.linspace(0, 20, 150)
    seasonality = 10 * np.sin(np.arange(150) * (2 * np.pi / 30)) # Monthly seasonality
    noise = np.random.normal(0, 2, 150)
    
    data = trend + seasonality + noise
    ts = pd.Series(data, index=dates)
    return ts

def test_stationarity(timeseries):
    """Performs the Augmented Dickey-Fuller test to check for stationarity."""
    print("--- Augmented Dickey-Fuller Test ---")
    result = adfuller(timeseries, autolag='AIC')
    df_output = pd.Series(result[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
    for key, value in result[4].items():
        df_output[f'Critical Value ({key})'] = value
    print(df_output)
    
    if result[1] <= 0.05:
        print("\nConclusion: The series is likely stationary (p-value <= 0.05).")
    else:
        print("\nConclusion: The series is likely non-stationary (p-value > 0.05).")
    print("-------------------------------------")

def plot_forecast(ts, forecast, conf_int, n_forecast):
    """Visualizes the original time series, forecast, and confidence interval."""
    plt.figure(figsize=(12, 6))
    plt.plot(ts, label='Observed Data')
    
    # Create index for the forecast
    forecast_index = pd.date_range(start=ts.index[-1] + pd.Timedelta(days=1), periods=n_forecast, freq='D')
    
    plt.plot(forecast_index, forecast, color='red', label='Forecast')
    plt.fill_between(forecast_index, 
                     conf_int.iloc[:, 0], 
                     conf_int.iloc[:, 1], 
                     color='pink', alpha=0.5, label='95% Confidence Interval')

    plt.title('ARIMA Time Series Forecast')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.savefig('forecast_plot.png')
    print("\nForecast plot saved as forecast_plot.png")

if __name__ == "__main__":
    # 1. Get Data
    time_series_data = generate_synthetic_data()

    # 2. Check for stationarity
    print("Checking stationarity of the original series:")
    test_stationarity(time_series_data)
    
    # The data is non-stationary, so we need to difference it (the 'I' in ARIMA).
    # A `d` value of 1 is appropriate for data with a linear trend.

    # 3. Fit ARIMA model
    # We choose an order of (5,1,0) for this synthetic data.
    # p=5: Captures lags from the Auto-Regressive (AR) part.
    # d=1: First-degree differencing to handle the trend.
    # q=0: No Moving Average (MA) term needed for this example.
    print("\nFitting ARIMA(5,1,0) model...")
    model = ARIMA(time_series_data, order=(5, 1, 0))
    fitted_model = model.fit()
    print(fitted_model.summary())

    # 4. Generate Forecasts
    n_forecast = 30
    print(f"\nGenerating forecast for the next {n_forecast} periods...")
    forecast_results = fitted_model.get_forecast(steps=n_forecast)
    
    # Extract forecast values and confidence intervals
    forecast_values = forecast_results.predicted_mean
    confidence_interval = forecast_results.conf_int()

    print("\nForecasted Values:")
    print(forecast_values)

    # 5. Visualize the results
    plot_forecast(time_series_data, forecast_values, confidence_interval, n_forecast)
