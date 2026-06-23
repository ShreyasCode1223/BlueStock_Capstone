import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

PROCESSED_DIR = os.path.join("..", "data", "processed")
DB_DIR = os.path.join("..", "data", "db")

# Ensure db target folder exists
os.makedirs(DB_DIR, exist_ok=True)
db_path = os.path.join(DB_DIR, "bluestock_mf.db")

def build_database():
    print("\n=== Starting SQL Schema Building & Data Loading ===")
    
    # Connect directly to SQLite to execute pure DDL (Data Definition Language) [cite: 153]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create Dimension Fund Table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_fund (
        amfi_code TEXT PRIMARY KEY,
        fund_house TEXT,
        scheme_name TEXT,
        category TEXT,
        sub_category TEXT,
        plan TEXT,
        expense_ratio_pct REAL,
        risk_category TEXT
    );
    """)
    
    # 2. Create Fact NAV Table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_nav (
        amfi_code TEXT,
        date TEXT,
        nav REAL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );
    """)

    # 3. Create Fact Transactions Table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_transactions (
        investor_id TEXT,
        transaction_date TEXT,
        amfi_code TEXT,
        transaction_type TEXT,
        amount_inr INTEGER,
        city_tier TEXT,
        state TEXT,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );
    """)
    
    conn.commit()
    conn.close()
    print("[SUCCESS] Relational Star Schema created inside SQLite database.")

    # --- POPULATE THE DATABASE TABLES ---
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Load mapped data from processed CSVs into SQL
    try:
        df_fund = pd.read_csv(os.path.join(PROCESSED_DIR, "01_fund_master.csv"))
        # Map exact columns to match our SQL schema structure
        df_fund[['amfi_code', 'fund_house', 'scheme_name', 'category', 'sub_category', 'plan', 'expense_ratio_pct', 'risk_category']].to_sql('dim_fund', engine, if_exists='append', index=False)
        
        df_nav = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_nav.csv"))
        df_nav[['amfi_code', 'date', 'nav']].to_sql('fact_nav', engine, if_exists='append', index=False)
        
        df_tx = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_transactions.csv"))
        df_tx[['investor_id', 'transaction_date', 'amfi_code', 'transaction_type', 'amount_inr', 'city_tier', 'state']].to_sql('fact_transactions', engine, if_exists='append', index=False)
        
        print("[SUCCESS] All cleaned data successfully pushed to SQL tables! [cite: 170]")
    except Exception as e:
        print(f"[INFO] Tables might already be populated: {e}")

if __name__ == "__main__":
    build_database()