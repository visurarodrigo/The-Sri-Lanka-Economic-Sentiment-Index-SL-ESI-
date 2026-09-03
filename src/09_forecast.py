import os
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet
import warnings

warnings.filterwarnings('ignore')

# Define paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_merged_economic.csv'
ARTIFACTS_DIR = PROJECT_ROOT / 'artifacts'
FORECAST_OUTPUT = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_forecast_results.csv'

def calculate_metrics(y_true, y_pred):
    """Calculate MAE, RMSE, and SMAPE."""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))

    # SMAPE (Symmetric Mean Absolute Percentage Error)
    denominator = (np.abs(y_true) + np.abs(y_pred))
    smape = 100 * np.mean(2 * np.abs(y_pred - y_true) / (denominator + 1e-10))

    return {"MAE": mae, "RMSE": rmse, "SMAPE": smape}

def train_and_evaluate_sarima(train_data, test_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
    """Train SARIMA model and return predictions and MAPE."""
    print("   Training SARIMA model...")
    model = SARIMAX(train_data, order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
    sarima_model = model.fit(disp=False)
    
    # Predict on test set
    start = len(train_data)
    end = len(train_data) + len(test_data) - 1
    sarima_preds = sarima_model.predict(start=start, end=end)
    
    metrics = calculate_metrics(test_data, sarima_preds)
    print(f"   SARIMA Test Metrics: MAE={metrics['MAE']:.4f}, RMSE={metrics['RMSE']:.4f}, SMAPE={metrics['SMAPE']:.2f}%")
    
    return sarima_model, sarima_preds, metrics

def train_and_evaluate_prophet(train_data, test_data):
    """Train Prophet model and return predictions and MAPE."""
    print("   Training Prophet model...")
    # Prophet requires 'ds' and 'y'
    train_prophet = train_data.reset_index().rename(columns={'year_month': 'ds', 'sentiment_intensity': 'y'})
    test_prophet = test_data.reset_index().rename(columns={'year_month': 'ds', 'sentiment_intensity': 'y'})
    
    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False, interval_width=0.95)
    model.fit(train_prophet)
    
    # Predict on test set
    prophet_preds = model.predict(test_prophet)
    
    metrics = calculate_metrics(test_prophet['y'], prophet_preds['yhat'])
    print(f"   Prophet Test Metrics: MAE={metrics['MAE']:.4f}, RMSE={metrics['RMSE']:.4f}, SMAPE={metrics['SMAPE']:.2f}%")
    
    return model, prophet_preds['yhat'].values, metrics

def main():
    print(" Starting Phase 6: Time Series Forecasting...")
    
    # 1. Load Data
    print(f" Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH, parse_dates=['year_month'])
    df.set_index('year_month', inplace=True)
    
    # Focus on sentiment_intensity
    series = df['sentiment_intensity']
    
    # 2. Train/Test Split (Backtesting)
    # Use data up to Dec 2025 for training, and 2026 for testing
    train_data = series[series.index < '2026-01-01']
    test_data = series[series.index >= '2026-01-01']
    
    print(f"   Train size: {len(train_data)}, Test size: {len(test_data)}")
    
    # 3. Train and Evaluate Models
    _, _, sarima_metrics = train_and_evaluate_sarima(train_data, test_data)
    _, _, prophet_metrics = train_and_evaluate_prophet(train_data, test_data)
    
    # 4. Select Best Model
    best_model_name = "SARIMA" if sarima_metrics['MAE'] <= prophet_metrics['MAE'] else "Prophet"
    print(f"\n Best Model based on MAE: {best_model_name}")
    
    # 5. Retrain Best Model on Full Data for Final Forecast
    print(f"\n Retraining {best_model_name} on full dataset for final forecast...")
    if best_model_name == "SARIMA":
        final_model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12), enforce_stationarity=False, enforce_invertibility=False)
        final_fitted_model = final_model.fit(disp=False)
        final_preds = final_fitted_model.get_forecast(steps=12)
        final_yhat = final_preds.predicted_mean
        final_conf_int = final_preds.conf_int()
    else:
        final_prophet = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False, interval_width=0.95)
        full_prophet_data = series.reset_index().rename(columns={'year_month': 'ds', 'sentiment_intensity': 'y'})
        final_prophet.fit(full_prophet_data)
        future = final_prophet.make_future_dataframe(periods=12, freq='MS')
        forecast = final_prophet.predict(future)
        final_yhat = forecast['yhat'].iloc[-12:]
        final_conf_int = forecast[['yhat_lower', 'yhat_upper']].iloc[-12:]

    # 6. Save Artifacts
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    if best_model_name == "SARIMA":
        joblib.dump(final_fitted_model, ARTIFACTS_DIR / 'sarima_model.pkl')
    else:
        # Prophet doesn't have a direct joblib save, use its built-in method or joblib on the model object
        joblib.dump(final_prophet, ARTIFACTS_DIR / 'prophet_model.pkl') # Saving as pkl for consistency
        
    print(f" Saved {best_model_name} model to artifacts/")

    # 7. Save Final Forecast Results
    forecast_dates = pd.date_range(start=series.index[-1] + pd.DateOffset(months=1), periods=12, freq='MS')
    
    forecast_results = pd.DataFrame({
        'year_month': forecast_dates.strftime('%Y-%m'),
        'forecast_sentiment': final_yhat.values,
        'lower_bound': final_conf_int.iloc[:, 0].values if best_model_name == 'SARIMA' else final_conf_int['yhat_lower'].values,
        'upper_bound': final_conf_int.iloc[:, 1].values if best_model_name == 'SARIMA' else final_conf_int['yhat_upper'].values,
        'model_used': best_model_name
    })
    
    forecast_results.to_csv(FORECAST_OUTPUT, index=False)
    print(f" Saved final forecast to {FORECAST_OUTPUT}")
    
    print("\n Final 12-Month Forecast Preview:")
    print(forecast_results.to_string(index=False))

if __name__ == "__main__":
    main()