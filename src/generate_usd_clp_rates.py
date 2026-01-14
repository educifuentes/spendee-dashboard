import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path

def generate_rates_csv():
    """
    Fetches USD to CLP exchange rates and generates a CSV with monthly rates.
    Uses the first available rate of each month.
    """
    # Define date range
    start_date = "2021-01-01"
    today = datetime.now()
    # Add 1 day to include today in the range (yfinance end is exclusive)
    end_date = (today + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"Fetching USD/CLP rates from {start_date} to {end_date}...")

    # Download daily data for USD/CLP (Ticker: CLP=X)
    # We download daily data to ensure we can find the first trading day of each month
    df = yf.download("CLP=X", start=start_date, end=end_date, progress=False)

    if df.empty:
        print("Error: No data downloaded. Please check your internet connection.")
        return

    # Handle yfinance data structure (extract Close price)
    if isinstance(df.columns, pd.MultiIndex):
        # For newer yfinance versions where columns are (Price, Ticker)
        try:
            series = df.xs('Close', axis=1, level=0).iloc[:, 0]
        except KeyError:
            series = df.iloc[:, 0]
    elif 'Close' in df.columns:
        series = df['Close']
    else:
        series = df.iloc[:, 0]

    # Resample to Month Start ('MS') and take the first valid observation of the month
    # This effectively gets the rate for the first trading day of the month
    monthly_rates = series.resample('MS').first()

    # Create output DataFrame
    output = pd.DataFrame({
        'month': monthly_rates.index.strftime('%Y-%m'),
        'rate': monthly_rates.values.round(2)
    })

    # Save to CSV
    output_filename = Path(__file__).parent / "constants" / "usd_clp_rates.csv"
    output.to_csv(output_filename, index=False)
    print(f"Successfully generated {output_filename} with {len(output)} records.")

if __name__ == "__main__":
    generate_rates_csv()