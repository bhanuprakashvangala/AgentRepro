# ARIMA Time Series Forecasting

This project demonstrates how to build a time series forecast using an ARIMA (AutoRegressive Integrated Moving Average) model. The script uses the `statsmodels` library to perform the analysis.

## Features

- **Synthetic Data**: Generates its own sample time series data, making the script fully self-contained and reproducible.
- **Stationarity Test**: Performs an Augmented Dickey-Fuller (ADF) test to check if the time series is stationary and prints the conclusion.
- **ARIMA Modeling**: Fits an ARIMA(5,1,0) model to the data.
- **Forecasting**: Predicts future values and calculates 95% confidence intervals.
- **Visualization**: Creates a plot (`forecast_plot.png`) showing the original data, the forecasted values, and the confidence interval.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the script:**
    ```bash
    python arima_forecast.py
    ```

## Output

When you run the script, it will:

1.  Print the results of the ADF stationarity test to the console.
2.  Print a summary of the fitted ARIMA model.
3.  Print the forecasted values for the next 30 periods.
4.  Generate a `forecast_plot.png` file in the same directory, visualizing the forecast.
