"""Generate an Excel list of the SCM donor indicators.

Columns: Indicator (code), Name (descriptive), Ticker, Group (asset class).
Sorted alphabetically by indicator code (case-insensitive).
Source of truth: docs/donor_catalog.md / notebooks/00_Data_Fetching.ipynb (TICKERS).
"""
from pathlib import Path
import pandas as pd

# (Indicator code, Descriptive name, Yahoo ticker, Group)
DONORS = [
    ("AUD",        "Australian Dollar (AUD/USD)",          "AUDUSD=X",  "FX"),
    ("BTC",        "Bitcoin",                              "BTC-USD",   "Crypto"),
    ("CHF",        "Swiss Franc (USD/CHF)",                "CHF=X",     "FX"),
    ("CNY",        "Chinese Yuan (USD/CNY)",               "CNY=X",     "FX"),
    ("Coffee",     "Coffee",                               "KC=F",      "Agricultural"),
    ("Copper",     "Copper",                               "HG=F",      "Metals"),
    ("Corn",       "Corn",                                 "ZC=F",      "Agricultural"),
    ("Cotton",     "Cotton",                               "CT=F",      "Agricultural"),
    ("DXY",        "US Dollar Index (trade-weighted)",     "DX-Y.NYB",  "FX"),
    ("EM_Eq",      "Emerging Markets Equities (EEM ETF)",  "EEM",       "Equities"),
    ("EUR",        "Euro (EUR/USD)",                       "EURUSD=X",  "FX"),
    ("GBP",        "British Pound (GBP/USD)",              "GBPUSD=X",  "FX"),
    ("Gold",       "Gold",                                 "GC=F",      "Metals"),
    ("HYG",        "US High-Yield Credit (HYG ETF)",       "HYG",       "Rates & credit"),
    ("INR",        "Indian Rupee (USD/INR)",               "INR=X",     "FX"),
    ("IronOre",    "Iron Ore",                             "TIO=F",     "Metals"),
    ("JPY",        "Japanese Yen (USD/JPY)",               "JPY=X",     "FX"),
    ("KRW",        "Korean Won (USD/KRW)",                 "KRW=X",     "FX"),
    ("LiveCattle", "Live Cattle",                          "LE=F",      "Agricultural"),
    ("MXN",        "Mexican Peso (USD/MXN)",               "MXN=X",     "FX"),
    ("Nikkei",     "Nikkei 225",                           "^N225",     "Equities"),
    ("Palladium",  "Palladium",                            "PA=F",      "Metals"),
    ("Platinum",   "Platinum",                             "PL=F",      "Metals"),
    ("SP500",      "S&P 500 (SPY ETF)",                    "SPY",       "Equities"),
    ("Silver",     "Silver",                               "SI=F",      "Metals"),
    ("Soybeans",   "Soybeans",                             "ZS=F",      "Agricultural"),
    ("Sugar",      "Sugar",                                "SB=F",      "Agricultural"),
    ("TLT",        "Long-Duration US Treasuries (TLT ETF)", "TLT",      "Rates & credit"),
    ("US10Y",      "US 10-Year Treasury Yield",            "^TNX",      "Rates & credit"),
    ("VIX",        "CBOE Volatility Index",                "^VIX",      "Volatility"),
    ("Wheat",      "Wheat",                                "ZW=F",      "Agricultural"),
    ("ZAR",        "South African Rand (USD/ZAR)",         "ZAR=X",     "FX"),
]

df = pd.DataFrame(DONORS, columns=["Indicator", "Name", "Ticker", "Group"])
df = df.sort_values("Indicator", key=lambda s: s.str.lower()).reset_index(drop=True)
df.insert(0, "#", range(1, len(df) + 1))

assert len(df) == 32, f"expected 32 donors, got {len(df)}"

out = Path(__file__).resolve().parents[1] / "data" / "indicator_list.xlsx"
with pd.ExcelWriter(out, engine="openpyxl") as xw:
    df.to_excel(xw, index=False, sheet_name="Indicators")
    ws = xw.sheets["Indicators"]
    widths = {"A": 5, "B": 13, "C": 40, "D": 12, "E": 16}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"

print(f"Wrote {out}")
print(df.to_string(index=False))
print("\nGroup counts:")
print(df["Group"].value_counts().to_string())
