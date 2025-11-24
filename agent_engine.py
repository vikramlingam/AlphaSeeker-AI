import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentEngine:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            # Try to get from streamlit secrets if available (will handle in app.py usually, but good fallback)
            try:
                import streamlit as st
                api_key = st.secrets["OPENROUTER_API_KEY"]
            except:
                pass
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = "x-ai/grok-4.1-fast"

    def _get_completion(self, prompt, system_prompt="You are a helpful financial analyst AI."):
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {e}"

    def analyze_competitors(self, ticker, business_summary):
        """
        Uses LLM to analyze business description and suggest true competitors.
        Returns a JSON string or structured list.
        """
        system_prompt = "You are a Senior Equity Research Analyst. Your goal is to identify the most relevant publicly traded competitors for a given company."
        prompt = f"""
        Analyze the following business summary for {ticker}:
        "{business_summary}"

        Identify 5-7 direct publicly traded competitors that operate in the same specific niche or market segment. 
        Focus on companies with similar business models, not just broad sector peers.
        
        Return ONLY a valid JSON array of ticker symbols. Example: ["AAPL", "MSFT", "GOOGL"]
        Do not add markdown formatting or extra text.
        """
        response = self._get_completion(prompt, system_prompt)
        # Clean up response to ensure it's just the JSON array
        response = response.strip().replace("```json", "").replace("```", "")
        return response

    def find_better_alternatives(self, ticker, metrics, peers_metrics):
        """
        Analyzes metrics to find a 'Better Alternative'.
        """
        # This logic might be better handled deterministically in python, 
        # but we can use LLM to generate the "Pitch".
        
        # We will pass the data to the LLM to write a persuasive argument if a better peer exists.
        system_prompt = "You are a Hedge Fund Portfolio Manager looking for Alpha."
        
        peers_str = json.dumps(peers_metrics, indent=2)
        target_str = json.dumps(metrics, indent=2)
        
        prompt = f"""
        I am long {ticker}. Here are its metrics:
        {target_str}

        Here are the metrics for its peers:
        {peers_str}

        Identify if there is a clearly superior alternative among the peers based on:
        1. Higher Growth
        2. Better Valuation (Lower PE/EV-EBITDA)
        3. Stronger Margins
        
        If you find one, write a short, punchy "Alpha Trade" pitch (max 100 words) explaining why I should switch.
        
        CRITICAL: Add a section called "Why this matters for beginners:" where you explain the specific metric (e.g. EV/EBITDA) in very simple terms and why the alternative is safer or more profitable.
        
        If {ticker} is the best, say "HOLD: {ticker} remains the best in class." and explain why.
        """
        return self._get_completion(prompt, system_prompt)

    def explain_technical_analysis(self, ticker, current_price, sma_50, sma_200, rsi):
        """
        Explains technical indicators to a beginner.
        """
        system_prompt = "You are a helpful trading mentor. Explain technical charts to a beginner in simple, plain English."
        
        prompt = f"""
        Analyze the technical state of {ticker}:
        - Current Price: ${current_price:.2f}
        - 50-Day Moving Average: ${sma_50:.2f}
        - 200-Day Moving Average: ${sma_200:.2f}
        - RSI (14-day): {rsi:.2f}
        
        Explain what these signals mean. 
        - Is the trend bullish (Price > SMAs)? 
        - Is it overbought (RSI > 70) or oversold (RSI < 30)?
        - What should a beginner watch for?
        
        Keep it under 100 words.
        """
        return self._get_completion(prompt, system_prompt)

    def analyze_risks(self, ticker, business_summary):
        """
        Identifies key risks for the business.
        """
        system_prompt = "You are a Risk Manager. Identify the top 3 specific risks for this business."
        
        prompt = f"""
        Based on this business summary for {ticker}:
        "{business_summary}"
        
        List the top 3 biggest risks an investor should be aware of (e.g., regulatory, competition, supply chain).
        Be specific to the company.
        """
        return self._get_completion(prompt, system_prompt)

    def summarize_ownership_activity(self, ticker, insider_data, institutional_data):
        """
        Summarizes insider and institutional activity concisely.
        """
        system_prompt = "You are a concise financial news editor. Summarize the key takeaways from the provided data in 3 bullet points. Max 50 words total."
        
        insider_str = insider_data.to_string() if insider_data is not None else "No Data"
        inst_str = institutional_data.to_string() if institutional_data is not None else "No Data"
        
        prompt = f"""
        Ticker: {ticker}
        
        Insider Trading (Recent):
        {insider_str}
        
        Institutional Holders:
        {inst_str}
        
        Provide a very short summary of the sentiment (Buying/Selling) and key holders.
        """
        return self._get_completion(prompt, system_prompt)

