"""
ARIMA Time Series Forecasting Script
Includes stationarity tests, model training, and visualization
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
warnings.filterwarnings('ignore')


def adf_test(series, name=''):
    """
    Perform Augmented Dickey-Fuller test for stationarity

    Args:
        series: Time series data
        name: Name of the series for display

    Returns:
        bool: True if stationary, False otherwise
    """
    print(f'\n{"="*50}')
    print(f'ADF Test Results for {name}')
    print(f'{"="*50}')

    result = adfuller(series.dropna())

    print(f'ADF Statistic: {result[0]:.6f}')
    print(f'p-value: {result[1]:.6f}')
    print(f'Critical Values:')
    for key, value in result[4].items():
        print(f'\t{key}: {value:.3f}')

    # Interpret results
    if result[1] <= 0.05:
        print(f'\nResult: Series is STATIONARY (p-value <= 0.05)')
        return True
    else:
        print(f'\nResult: Series is NON-STATIONARY (p-value > 0.05)')
        return False


def make_stationary(series, max_diff=2):
    """
    Make time series stationary through differencing

    Args:
        series: Time series data
        max_diff: Maximum number of differencing operations

    Returns:
        tuple: (stationary_series, number_of_differences)
    """
    current_series = series.copy()

    for d in range(max_diff + 1):
        is_stationary = adf_test(current_series, f'Series (d={d})')

        if is_stationary:
            return current_series, d

        if d < max_diff:
            current_series = current_series.diff().dropna()

    print('\nWarning: Series may not be fully stationary')
    return current_series, max_diff


def plot_diagnostics(series, title='Time Series'):
    """
    Plot ACF and PACF for model parameter selection

    Args:
        series: Time series data
        title: Plot title
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    plot_acf(series.dropna(), lags=40, ax=axes[0])
    axes[0].set_title(f'Autocorrelation Function (ACF) - {title}')

    plot_pacf(series.dropna(), lags=40, ax=axes[1])
    axes[1].set_title(f'Partial Autocorrelation Function (PACF) - {title}')

    plt.tight_layout()
    plt.savefig('acf_pacf_plots.png', dpi=300, bbox_inches='tight')
    print(f'\nACF/PACF plots saved as "acf_pacf_plots.png"')
    plt.close()


def find_best_arima_params(series, p_range=(0, 5), q_range=(0, 5), d=1):
    """
    Find best ARIMA parameters using AIC criterion

    Args:
        series: Time series data
        p_range: Range for AR parameter p
        q_range: Range for MA parameter q
        d: Differencing parameter

    Returns:
        tuple: Best (p, d, q) parameters
    """
    print(f'\n{"="*50}')
    print('Searching for Best ARIMA Parameters...')
    print(f'{"="*50}')

    best_aic = np.inf
    best_params = None

    for p in range(p_range[0], p_range[1] + 1):
        for q in range(q_range[0], q_range[1] + 1):
            try:
                model = ARIMA(series, order=(p, d, q))
                fitted_model = model.fit()

                if fitted_model.aic < best_aic:
                    best_aic = fitted_model.aic
                    best_params = (p, d, q)

                print(f'ARIMA({p},{d},{q}) - AIC: {fitted_model.aic:.2f}')

            except Exception as e:
                continue

    print(f'\nBest Parameters: ARIMA{best_params} with AIC: {best_aic:.2f}')
    return best_params


def train_arima_model(series, order):
    """
    Train ARIMA model with specified parameters

    Args:
        series: Time series data
        order: ARIMA order (p, d, q)

    Returns:
        Fitted ARIMA model
    """
    print(f'\n{"="*50}')
    print(f'Training ARIMA{order} Model')
    print(f'{"="*50}')

    model = ARIMA(series, order=order)
    fitted_model = model.fit()

    print(fitted_model.summary())

    return fitted_model


def generate_forecast(model, steps=30):
    """
    Generate forecasts with confidence intervals

    Args:
        model: Fitted ARIMA model
        steps: Number of steps to forecast

    Returns:
        DataFrame with forecasts and confidence intervals
    """
    print(f'\n{"="*50}')
    print(f'Generating {steps}-step Forecast')
    print(f'{"="*50}')

    forecast_result = model.get_forecast(steps=steps)
    forecast_df = forecast_result.summary_frame()

    print(forecast_df)

    return forecast_df


def plot_forecast(series, forecast_df, title='ARIMA Forecast'):
    """
    Visualize historical data and forecasts with confidence intervals

    Args:
        series: Historical time series data
        forecast_df: DataFrame with forecasts and confidence intervals
        title: Plot title
    """
    plt.figure(figsize=(14, 7))

    # Plot historical data
    plt.plot(series.index, series.values, label='Historical Data',
             color='blue', linewidth=2)

    # Plot forecast
    forecast_index = pd.date_range(
        start=series.index[-1],
        periods=len(forecast_df) + 1,
        freq=series.index.freq
    )[1:]

    plt.plot(forecast_index, forecast_df['mean'],
             label='Forecast', color='red', linewidth=2)

    # Plot confidence intervals
    plt.fill_between(forecast_index,
                      forecast_df['mean_ci_lower'],
                      forecast_df['mean_ci_upper'],
                      color='pink', alpha=0.3,
                      label='95% Confidence Interval')

    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig('forecast_plot.png', dpi=300, bbox_inches='tight')
    print(f'\nForecast plot saved as "forecast_plot.png"')
    plt.show()


def plot_residuals(model):
    """
    Plot residual diagnostics

    Args:
        model: Fitted ARIMA model
    """
    residuals = model.resid

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Residuals over time
    axes[0, 0].plot(residuals)
    axes[0, 0].set_title('Residuals Over Time')
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].set_ylabel('Residuals')
    axes[0, 0].grid(True, alpha=0.3)

    # Residuals histogram
    axes[0, 1].hist(residuals, bins=30, edgecolor='black')
    axes[0, 1].set_title('Residuals Distribution')
    axes[0, 1].set_xlabel('Residuals')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].grid(True, alpha=0.3)

    # ACF of residuals
    plot_acf(residuals, lags=40, ax=axes[1, 0])
    axes[1, 0].set_title('ACF of Residuals')

    # Q-Q plot
    from scipy import stats
    stats.probplot(residuals, dist="norm", plot=axes[1, 1])
    axes[1, 1].set_title('Q-Q Plot')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('residuals_diagnostics.png', dpi=300, bbox_inches='tight')
    print(f'\nResiduals diagnostics saved as "residuals_diagnostics.png"')
    plt.show()


def generate_sample_data():
    """
    Generate sample time series data for demonstration

    Returns:
        pandas Series with datetime index
    """
    print('Generating sample time series data...')

    # Create date range
    dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='D')

    # Generate synthetic data with trend, seasonality, and noise
    np.random.seed(42)
    trend = np.linspace(100, 150, len(dates))
    seasonality = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
    noise = np.random.normal(0, 5, len(dates))

    values = trend + seasonality + noise

    series = pd.Series(values, index=dates)

    print(f'Generated {len(series)} data points from {series.index[0]} to {series.index[-1]}')

    return series


def main():
    """
    Main execution function
    """
    print('='*70)
    print('ARIMA TIME SERIES FORECASTING')
    print('='*70)

    # Step 1: Load or generate data
    series = generate_sample_data()

    # Step 2: Check stationarity
    print('\n--- STEP 1: Stationarity Test ---')
    is_stationary = adf_test(series, 'Original Series')

    # Step 3: Make stationary if needed
    if not is_stationary:
        print('\n--- STEP 2: Making Series Stationary ---')
        stationary_series, d = make_stationary(series)
    else:
        d = 0
        stationary_series = series

    # Step 4: Plot diagnostics
    print('\n--- STEP 3: Plotting ACF/PACF ---')
    plot_diagnostics(stationary_series, 'Stationary Series')

    # Step 5: Find best parameters (optional - comment out for manual selection)
    print('\n--- STEP 4: Parameter Selection ---')
    best_params = find_best_arima_params(series, p_range=(0, 3), q_range=(0, 3), d=d)

    # Step 6: Train model
    print('\n--- STEP 5: Model Training ---')
    model = train_arima_model(series, order=best_params)

    # Step 7: Generate forecast
    print('\n--- STEP 6: Forecasting ---')
    forecast_df = generate_forecast(model, steps=90)

    # Step 8: Visualize results
    print('\n--- STEP 7: Visualization ---')
    plot_forecast(series, forecast_df, f'ARIMA{best_params} Forecast')

    # Step 9: Residual diagnostics
    print('\n--- STEP 8: Residual Diagnostics ---')
    plot_residuals(model)

    # Save forecast to CSV
    forecast_df.to_csv('forecast_results.csv')
    print(f'\nForecast results saved to "forecast_results.csv"')

    print('\n' + '='*70)
    print('FORECASTING COMPLETED SUCCESSFULLY!')
    print('='*70)


if __name__ == '__main__':
    main()
