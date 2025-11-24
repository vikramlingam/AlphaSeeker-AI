import yfinance as yf
import pandas as pd
import numpy as np

class FinanceEngine:
    def __init__(self):
        pass

    def get_stock_data(self, ticker):
        """Fetches stock data from yfinance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Basic info
            data = {
                "symbol": info.get("symbol", ticker),
                "longName": info.get("longName", ticker),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "currentPrice": info.get("currentPrice", info.get("regularMarketPrice", np.nan)),
                "marketCap": info.get("marketCap", np.nan),
                "trailingPE": info.get("trailingPE", np.nan),
                "forwardPE": info.get("forwardPE", np.nan),
                "evToEbitda": info.get("enterpriseToEbitda", np.nan),
                "beta": info.get("beta", np.nan),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", np.nan),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", np.nan),
                "averageVolume": info.get("averageVolume", np.nan),
                "profitMargins": info.get("profitMargins", np.nan),
                "revenueGrowth": info.get("revenueGrowth", np.nan),
                "operatingMargins": info.get("operatingMargins", np.nan),
                "debtToEquity": info.get("debtToEquity", np.nan),
                "freeCashflow": info.get("freeCashflow", np.nan),
                "earningsGrowth": info.get("earningsGrowth", np.nan),
                "longBusinessSummary": info.get("longBusinessSummary", "No description available."),
            }
            
            # Get financials for growth calculation
            financials = stock.financials
            if not financials.empty:
                 # Try to calculate 5y revenue growth if possible, else use info
                 pass

            return data, stock
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None, None

    def get_insider_trades(self, stock_obj):
        """Fetches recent insider trading activity."""
        try:
            # yfinance often has 'insider_transactions' or 'insider_purchases'
            # Let's try to get the dataframe
            insider = stock_obj.insider_transactions
            if insider is not None and not insider.empty:
                return insider.head(10) # Return top 10 recent
            return None
        except:
            return None

    def get_institutional_holders(self, stock_obj):
        """Fetches top institutional holders."""
        try:
            holders = stock_obj.institutional_holders
            if holders is not None and not holders.empty:
                return holders.head(10)
            return None
        except:
            return None

    def get_price_history(self, ticker):
        """Fetches 1 year of price history and calculates technicals."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            if hist.empty:
                return None
                
            # Calculate SMA
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
            
            # Calculate RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))
            
            return hist
        except Exception as e:
            print(f"Error fetching history: {e}")
            return None


    def calculate_reverse_dcf(self, current_price, free_cash_flow, discount_rate, terminal_growth_rate, shares_outstanding):
        """
        Back-solves for the implied growth rate over the next 10 years.
        
        This is a simplified iterative approach.
        DCF = Sum(FCF / (1+r)^t) + TerminalValue / (1+r)^10
        We want to find 'g' such that DCF / Shares = Current Price.
        """
        if not all([current_price, free_cash_flow, shares_outstanding]) or \
           pd.isna(current_price) or pd.isna(free_cash_flow) or pd.isna(shares_outstanding) or \
           free_cash_flow <= 0:
            return np.nan

        target_value = current_price * shares_outstanding
        
        # Binary search for growth rate
        low = -0.50 # -50%
        high = 1.00 # 100%
        tolerance = 0.001
        
        for _ in range(100):
            mid = (low + high) / 2
            dcf_val = self._calculate_dcf_value(free_cash_flow, mid, discount_rate, terminal_growth_rate)
            
            if abs(dcf_val - target_value) < (target_value * tolerance):
                return mid * 100 # Return as percentage
            
            if dcf_val > target_value:
                high = mid
            else:
                low = mid
                
        return mid * 100

    def _calculate_dcf_value(self, fcf, growth_rate, discount_rate, terminal_growth_rate):
        """Helper to calculate DCF value given a growth rate."""
        total_value = 0
        current_fcf = fcf
        
        # 10 Year Projection
        for i in range(1, 11):
            current_fcf *= (1 + growth_rate)
            discounted_fcf = current_fcf / ((1 + discount_rate) ** i)
            total_value += discounted_fcf
            
        # Terminal Value
        terminal_value = (current_fcf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        discounted_terminal_value = terminal_value / ((1 + discount_rate) ** 10)
        
        total_value += discounted_terminal_value
        return total_value

    def get_peers(self, ticker):
        """Fetches peer tickers. This is tricky with yfinance free. 
        We will try to get sector peers or use a hardcoded list for demo if needed.
        Actually, yfinance often doesn't give direct peers easily in the new API.
        We might need to search for same sector/industry.
        For this 'Novel' feature, we will try to find stocks in the same industry.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            sector = info.get('sector')
            industry = info.get('industry')
            
            # This is a bit of a hack since yfinance doesn't have a direct 'get_peers' anymore
            # We can't scan the whole market. 
            # For the purpose of this agent, we might need to rely on the LLM to suggest peers 
            # OR we can just return a few popular ones if we can't find them.
            # BUT, let's try to be smart. 
            # We will return a placeholder list that the Agent Engine can expand or refine, 
            # or we can use a small static map for major sectors for reliability.
            
            # For now, return None so the Agent can handle it or we prompt the user.
            # Actually, let's return a few common ones if possible or just empty.
            return [] 
        except:
            return []

    def get_historical_growth(self, ticker_obj):
        """Calculates historical revenue growth (CAGR) over available years (up to 5)."""
        try:
            financials = ticker_obj.financials
            if financials.empty:
                return np.nan
            
            revenues = financials.loc['Total Revenue']
            if len(revenues) < 2:
                return np.nan
            
            # Sort by date ascending
            revenues = revenues.sort_index()
            
            start_rev = revenues.iloc[0]
            end_rev = revenues.iloc[-1]
            years = len(revenues) - 1
            
            if start_rev <= 0 or years <= 0:
                return np.nan
                
            cagr = (end_rev / start_rev) ** (1 / years) - 1
            return cagr * 100
        except Exception as e:
            return np.nan
