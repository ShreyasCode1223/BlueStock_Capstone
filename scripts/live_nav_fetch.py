import os
import requests
import pandas as pd

RAW_DATA_DIR = os.path.join("..", "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# AMFI target schema codes defined by project requirements
SCHEMES = {
    "125497": "HDFC_Top_100_Direct",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip"
}

def pull_and_serialize_nav():
    print("=== Extracting Live Telemetry via mfapi.in REST Endpoints ===")
    for code, name in SCHEMES.items():
        url = f"https://api.mfapi.in/mf/{code}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            json_payload = response.json()
            
            nav_records = json_payload.get("data", [])
            if not nav_records:
                print(f"[Warning] Payload empty for scheme code: {code}")
                continue
                
            df = pd.DataFrame(nav_records)
            df["amfi_code"] = code
            df = df[["amfi_code", "date", "nav"]]
            
            output_file = os.path.join(RAW_DATA_DIR, f"live_nav_{code}.csv")
            df.to_csv(output_file, index=False)
            print(f"[SUCCESS] Serialized {len(df)} rows for target: {name}")
        except Exception as e:
            print(f"[HTTP/Parsing Error] Target {code} failed: {e}")

if __name__ == "__main__":
    pull_and_serialize_nav()