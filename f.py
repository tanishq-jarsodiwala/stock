import yfinance as yf
import pandas as pd
import numpy as np
from tqdm import tqdm  # For progress bar

def fetch_financial_data(ticker):
    try:
        info = yf.Ticker(ticker).info

        # Extract the required financial metrics
        data = {
            "Ticker": ticker,
            "Company Name": info.get("longName"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "P/E Ratio": info.get("trailingPE"),
            "Forward P/E Ratio": info.get("forwardPE"),
            "P/B Ratio": info.get("priceToBook"),
            "P/S Ratio": info.get("priceToSalesTrailing12Months"),
            "Price/Cash Flow Ratio": info.get("priceToCashflow"),
            "EPS (TTM)": info.get("trailingEps"),
            "Forward EPS": info.get("forwardEps"),
            "ROE": info.get("returnOnEquity"),
            "ROA": info.get("returnOnAssets"),
            "Gross Margin": info.get("grossMargins"),
            "Net Profit Margin": info.get("profitMargins"),
            "Current Ratio": info.get("currentRatio"),
            "Quick Ratio": info.get("quickRatio"),
            "Debt-to-Equity Ratio": info.get("debtToEquity"),
            "Interest Coverage Ratio": info.get("earningsBeforeInterestAndTaxes"),
            "Asset Turnover Ratio": (
                info.get("revenuePerShare") / info.get("bookValue")
                if info.get("revenuePerShare") and info.get("bookValue") else None
            ),
            "Inventory Turnover Ratio": info.get("inventoryTurnover"),
            "Dividend Yield": info.get("dividendYield"),
            "Dividend Payout Ratio": info.get("payoutRatio"),
            "Market Cap": info.get("marketCap"),
            "52-Week High": info.get("fiftyTwoWeekHigh"),
            "52-Week Low": info.get("fiftyTwoWeekLow"),
        }

        return data

    except Exception as e:
        return {"Ticker": ticker, "Error": str(e)}

# Load the ticker list
tickers_df = pd.read_csv("Equity_ticker.csv")  # Replace with the path to your ticker file
tickers = tickers_df["Ticker"].tolist()

# Fetch data for all tickers
financial_data = []
for ticker in tqdm(tickers, desc="Fetching data for all companies"):
    data = fetch_financial_data(ticker)
    financial_data.append(data)

# Convert to a DataFrame
financial_data_df = pd.DataFrame(financial_data)

# Save to CSV
financial_data_df.to_csv("All_Companies_Financial_Data.csv", index=False)

print("Data fetching completed. Saved to 'All_Companies_Financial_Data.csv'")
