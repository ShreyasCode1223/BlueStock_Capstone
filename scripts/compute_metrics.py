import os
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = os.path.join("..", "data", "db", "bluestock_mf.db")
PROCESSED_DIR = os.path.join("..", "data", "processed")

def run_analytics_pipeline():
    print("=== Starting Day 3 & 4: Performance Metrics & Risk Computation ===")
    
    # 1. Connect to our freshly minted SQLite Database
    conn = sqlite3.connect(DB_PATH)
    
    # Extract raw historical NAV records into a Pandas DataFrame
    query = "SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date"
    df_nav = pd.read_sql_query(query, conn)
    conn.close()
    
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    
    # --- 2. COMPUTE DAILY RETURNS ---
    # Formula: daily_return = (NAV_t / NAV_t-1) - 1
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()
    
    print("[SUCCESS] Computed daily percent changes across chronological timelines.")

    # --- 3. AGGREGATE RISK AND RETURN METRICS PER SCHEME ---
    risk_free_rate = 0.065 # 6.5% RBI repo rate proxy 
    trading_days = 252     # Standardized annual trading window benchmark 
    
    summary_data = []
    
    for amfi_code, group in df_nav.groupby('amfi_code'):
        # Filter drops initial NaN values from pct_change computation
        clean_returns = group['daily_return'].dropna()
        
        if len(clean_returns) < 10:
            continue
            
        # Standard Annualized Return Framework
        mean_return = clean_returns.mean()
        annualized_return = mean_return * trading_days
        
        # Standard Annualized Volatility Framework
        annualized_std = clean_returns.std() * np.sqrt(trading_days)
        
        # --- 4. SHARPE RATIO FORMULA ---
        # Sharpe = (Portfolio Return - Risk Free Rate) / Standard Deviation
        if annualized_std > 0:
            sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std
        else:
            sharpe_ratio = 0
            
        # --- 5. SORTINO RATIO FORMULA ---
        # Sortino only penalizes downside volatility (negative return periods)
        downside_returns = clean_returns[clean_returns < 0]
        if len(downside_returns) > 0:
            downside_std = downside_returns.std() * np.sqrt(trading_days)
            sortino_ratio = (annualized_return - risk_free_rate) / downside_std
        else:
            sortino_ratio = 0
            
        # --- 6. MAXIMUM DRAWDOWN COMPUTATION ---
        # Tracks peak-to-trough extreme asset valuation drops
        rolling_max = group['nav'].cummax()
        drawdowns = (group['nav'] - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        summary_data.append({
            "amfi_code": amfi_code,
            "annualized_return_pct": round(annualized_return * 100, 2),
            "annualized_volatility_pct": round(annualized_std * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "sortino_ratio": round(sortino_ratio, 2),
            "max_drawdown_pct": round(max_drawdown * 100, 2)
        })

    # Save calculated datasets down into CSV files for easy dashboard importing
    df_metrics = pd.DataFrame(summary_data)
    metrics_csv_path = os.path.join(PROCESSED_DIR, "computed_fund_analytics.csv")
    df_metrics.to_csv(metrics_csv_path, index=False)
    
    print(f"[SUCCESS] Calculated advanced risk statistics profile saved to: {metrics_csv_path}")

if __name__ == "__main__":
    run_analytics_pipeline()