import yfinance as yf
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
from nsetools import Nse
import time
import os

# --- Configuration ---
TICKER_SYMBOL = "^NSEI"  # Nifty 50's symbol on Yahoo Finance
INDEX_SYMBOL = "NIFTY 50" # Nifty 50's symbol for nsetools (live data)
EMA_PERIOD = 10         # 10-day Exponential Moving Average
HISTORY_MONTHS = 6      # Download last 6 months of daily data
DELAY = 1               # Update frequency for live price in seconds
# ---------------------

# Initialize the NSE object for live data
nse = Nse()

def download_historical_data(ticker, months):
    """
    Downloads historical Nifty 50 daily data for the last 'months' period.
    We download 6 months + 10 extra days to ensure we have enough data to 
    initialize the 10 EMA accurately.
    """
    end_date = dt.date.today()
    # Go back 6 months plus an extra 10 days for EMA calculation buffer
    start_date = end_date - relativedelta(months=months, days=10)
    
    print(f"-> Downloading Nifty 50 data from {start_date} to {end_date}...")
    
    # yfinance fetches daily OHLCV data
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    if df.empty:
        raise ValueError("Could not download historical data. Check the ticker symbol or connection.")
        
    # We only need the 'Close' price for EMA calculation
    return df['Close'].rename('Price')


def calculate_baseline_ema(historical_prices):
    """
    Calculates the full EMA series on the historical data using Pandas ewm().
    Returns the last calculated historical EMA value.
    """
    # The adjust=False parameter is used for EMA calculation consistency
    ema_series = (
        historical_prices
        .ewm(span=EMA_PERIOD, adjust=False)
        .mean()
    )
    
    # The last value in the series is the EMA from the end of the historical period
    last_historical_ema = ema_series.iloc[-1]
    
    print(f"-> Baseline 10 EMA calculated from {len(historical_prices)} days of data.")
    print(f"-> Last Historical Close Price: {historical_prices.iloc[-1]:,.2f}")
    print(f"-> Last Historical 10 EMA (Baseline): {last_historical_ema:,.2f}")
    
    return last_historical_ema


def run_ema_tracker():
    """Main function to perform the calculation and real-time tracking."""
    global EMA_PERIOD
    
    try:
        # STEP 1: DOWNLOAD AND CALCULATE BASELINE EMA
        historical_df = download_historical_data(TICKER_SYMBOL, HISTORY_MONTHS)
        previous_ema = calculate_baseline_ema(historical_df)
        
    except ValueError as e:
        print(f"\nFATAL ERROR: {e}")
        return
    except Exception as e:
        print(f"\nAn error occurred during data download: {e}")
        return
    
    # STEP 2: REAL-TIME TRACKING AND RECALCULATION
    
    # Smoothing Factor (alpha) for the recursive EMA formula
    SMOOTHING_FACTOR = 2 / (EMA_PERIOD + 1)
    
    print("\n--- Starting Real-Time 10 EMA Update ---")
    print("Press Ctrl+C to stop.")
    
    while True:
        try:
            # Fetch the current live Nifty price
            nifty_quote = nse.get_index_quote(INDEX_SYMBOL)
            current_nifty_price = nifty_quote.get('last')
            current_time = time.strftime("%H:%M:%S")

            if current_nifty_price is None:
                print(f"Time: {current_time} - Market might be closed or data unavailable. Retrying...")
                time.sleep(DELAY)
                continue

            # Apply the recursive EMA formula
            # EMA_new = (Price_new * alpha) + (EMA_old * (1 - alpha))
            current_ema = (current_nifty_price * SMOOTHING_FACTOR) + \
                          (previous_ema * (1 - SMOOTHING_FACTOR))
                          
            # Update the previous_ema for the next iteration
            previous_ema = current_ema

            # Display results
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"📊 Nifty 50 Real-Time 10 EMA")
            print("---------------------------------------")
            print(f"Time:        {current_time}")
            print(f"Nifty Price: **{current_nifty_price:,.2f}**")
            print(f"10 EMA:      **{current_ema:,.2f}**")
            
            # 

            time.sleep(DELAY)
            
        except KeyboardInterrupt:
            print("\nTracker stopped by user.")
            break
        except Exception as e:
            # Handle non-critical errors like temporary connection loss
            print(f"Non-fatal error during live fetch: {e}")
            time.sleep(DELAY)

if __name__ == "__main__":
    run_ema_tracker()
