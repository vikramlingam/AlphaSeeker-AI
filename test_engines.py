from finance_engine import FinanceEngine
from agent_engine import AgentEngine
import json

def test_finance_engine():
    print("Testing FinanceEngine...")
    fe = FinanceEngine()
    ticker = "AAPL"
    data, stock = fe.get_stock_data(ticker)
    
    if data:
        print(f"Successfully fetched data for {ticker}")
        print(f"Price: {data['currentPrice']}")
        print(f"PE: {data['trailingPE']}")
        
        # Test Reverse DCF
        # Mocking some values if they are missing for the test
        fcf = data.get('freeCashflow', 100000000000)
        shares = stock.info.get('sharesOutstanding', 15000000000)
        price = data['currentPrice']
        
        if fcf and shares and price:
            implied_growth = fe.calculate_reverse_dcf(price, fcf, 0.10, 0.03, shares)
            print(f"Implied Growth (Reverse DCF): {implied_growth:.2f}%")
        else:
            print("Skipping Reverse DCF test due to missing data")
            
    else:
        print("Failed to fetch stock data")

def test_agent_engine():
    print("\nTesting AgentEngine...")
    ae = AgentEngine()
    
    # Test Competitor Analysis
    ticker = "TSLA"
    summary = "Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems in the United States, China, and internationally."
    print(f"Getting competitors for {ticker}...")
    competitors = ae.analyze_competitors(ticker, summary)
    print(f"Competitors: {competitors}")
    
    # Test CFO Chat
    print(f"\nTesting CFO Chat for {ticker}...")
    context = {"revenue": "100B", "profit_margin": "15%", "debt": "5B"}
    response = ae.cfo_chat("Why are margins compressing?", ticker, context)
    print(f"CFO Response: {response}")

if __name__ == "__main__":
    test_finance_engine()
    test_agent_engine()
