import os
import csv
from datetime import datetime
import requests
import yfinance as yf
from google import genai

# 1. INITIALIZE API KEYS & CHANNELS
GEMINI_API_KEY = "AQ.Ab8RN6KhYLnqGSwC0RdzVR7Qb6fdhTXpZkJN5m7w1N-ckw9yjA"
client = genai.Client(api_key=GEMINI_API_KEY)

# Your active Discord channel webhook pipeline:
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1517801516260393080/qZI0eOvs_DQl1Ztw2BEaDDAq67OYSNiTkHAH1M2RnXGpmGr3ipeFPMIksfer7yd3NdZn"


def get_crypto_prices():
    """Fetches live cryptocurrency data from Coingecko API."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"Error fetching crypto data: {e}")
        return None


def get_stock_prices():
    """Fetches live stock data using yfinance."""
    tickers = ["PAH3.DE", "TSLA"]
    stock_data = {}
    try:
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            todays_data = stock.history(period='1d')
            if not todays_data.empty:
                price = todays_data['Close'].iloc[0]
                stock_data[ticker] = price
            else:
                stock_data[ticker] = 0.0
        return stock_data
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None


def log_data_to_csv(crypto, stocks):
    """Saves market prices into a local CSV database file."""
    file_name = "market_history.csv"
    file_exists = os.path.isfile(file_name)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    headers = ["Timestamp", "BTC_Price", "ETH_Price", "SOL_Price", "PORSCHE_Price", "TESLA_Price"]
    row = [
        current_time,
        round(crypto['bitcoin']['usd'], 2),
        round(crypto['ethereum']['usd'], 2),
        round(crypto['solana']['usd'], 2),
        round(stocks.get('PAH3.DE', 0), 2),
        round(stocks.get('TSLA', 0), 2)
    ]

    try:
        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(row)
        print(f"📝 SUCCESS: Data safely logged to local database.")
    except Exception as e:
        print(f"Database logging failed: {e}")


def generate_ai_report(crypto, stocks):
    """Feeds combined market data into Gemini for analysis."""
    market_summary = (
        f"--- CRYPTO ---\n"
        f"Bitcoin: ${crypto['bitcoin']['usd']} ({crypto['bitcoin']['usd_24h_change']:.2f}%)\n"
        f"Ethereum: ${crypto['ethereum']['usd']} ({crypto['ethereum']['usd_24h_change']:.2f}%)\n"
        f"Solana: ${crypto['solana']['usd']} ({crypto['solana']['usd_24h_change']:.2f}%)\n\n"
        f"--- STOCKS ---\n"
        f"Porsche AG (PAH3.DE): €{stocks.get('PAH3.DE', 0):.2f}\n"
        f"Tesla (TSLA): ${stocks.get('TSLA', 0):.2f}"
    )

    prompt = f"You are an elite financial asset manager. Analyze this live crypto and stock data and provide a 3-sentence aggressive trading brief for investors:\n\n{market_summary}"

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"AI Generation Failed. (Error: {e})"


def send_to_discord(crypto, stocks, ai_report):
    """Sends a formatted alert payload straight to a Discord channel webhook."""
    # Structure the message with Discord markdown for an elite layout
    message = (
        f"🛸 **VANTIX MARKET INTELLIGENCE ALERT** 🛸\n"
        f"_*Executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n"
        f"```md\n"
        f"[Bitcoin]:   ${crypto['bitcoin']['usd']:,.2f} ({crypto['bitcoin']['usd_24h_change']:.2f}%)\n"
        f"[Ethereum]:  ${crypto['ethereum']['usd']:,.2f} ({crypto['ethereum']['usd_24h_change']:.2f}%)\n"
        f"[Solana]:    ${crypto['solana']['usd']:,.2f} ({crypto['solana']['usd_24h_change']:.2f}%)\n"
        f"[Porsche]:   €{stocks.get('PAH3.DE', 0):,.2f}\n"
        f"[Tesla]:     ${stocks.get('TSLA', 0):,.2f}\n"
        f"```\n"
        f"🧠 **AI ANALYSIS BRIEF:**\n{ai_report}\n"
        f"=================================================="
    )

    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("🚀 SUCCESS: Alert dispatched directly to Discord server!")
        else:
            print(f"Discord dispatch failed with status: {response.status_code}")
    except Exception as e:
        print(f"Error sending payload to Discord: {e}")


# MAIN PIPELINE EXECUTION
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 VANTIX MASTER INTELLIGENCE SYSTEM RUNNING...")
    print("=" * 50)

    crypto_data = get_crypto_prices()
    stock_data = get_stock_prices()

    if crypto_data and stock_data:
        # 1. Log data into your local database
        log_data_to_csv(crypto_data, stock_data)

        # 2. Process data through the AI layer
        print("\n🧠 GENERATING AI MARKET ANALYSIS...")
        ai_brief = generate_ai_report(crypto_data, stock_data)

        # 3. Stream data and AI analysis to Discord channel
        print("\n📡 DISPATCHING WEBHOOK TELEMETRY...")
        send_to_discord(crypto_data, stock_data, ai_brief)
        print("=" * 50)