# AlphaSeeker AI

**Author:** Vikram Lingam

## Overview
AlphaSeeker AI is a Streamlit‑based web application that helps investors perform deep‑dive stock research. It combines financial data from **yfinance** with large‑language‑model (LLM) insights from OpenRouter to provide:
- Reverse DCF valuation (market‑implied growth)
- Autonomous competitor matrix with a "Better Alternative" recommendation
- Ownership & activity view (insider trades, institutional holders) with concise AI summaries
- Technical analysis chart (candlesticks, SMA 50/200, RSI) and an AI mentor that explains the signals in plain language
- Key risk identification for the business

## Core Architecture
- **`app.py`**: The main Streamlit application handling the UI and state.
- **`finance_engine.py`**: Handles data fetching from `yfinance` and complex calculations like the Reverse DCF.
- **`agent_engine.py`**: Manages LLM interactions via OpenRouter for competitor analysis and the explanations.

## Key Features Verified

### ✅ Market Implied Reverse DCF
- **Logic**: The app correctly back-solves for the implied growth rate based on current price and user assumptions (Discount Rate, Terminal Growth).
- **Visualization**: Displays a bar chart of implied future cash flows.
- **Insight**: Compares Implied Growth vs. Historical Growth to flag potential under/overvaluation.

### ✅ Autonomous Competitor Matrix
- **Agentic Discovery**: The LLM reads the business summary and identifies true peers (e.g., for TSLA, it found NIO, XPEV, RIVN, etc.).
- **Scatter Plot**: Plots "Revenue Growth" vs. "EV/EBITDA" to visualize the valuation gap.
- **Better Alternative**: The Agent analyzes the peer group and pitches a "Better Alternative" if one exists (e.g., "Switch to X for higher growth at a lower multiple").

### ✅ Ownership & Activity
- **Insider Trading**: Fetches recent insider transactions.
- **Institutional Holders**: Lists top institutional holders.
- **AI Summary**: Generates a concise summary of ownership sentiment.

### ✅ Technical Analysis & Education
- **Interactive Chart**: Displays 1Y price history with SMA 50/200.
- **RSI Indicator**: Shows current RSI with Overbought/Oversold flags.
- **AI Mentor**: Explains the chart patterns in simple English for beginners.

### ✅ Enhanced Insights
- **Key Risks**: AI identifies top 3 specific risks for the business.
- **Better Alternative**: Now includes a "Why this matters for beginners" section to explain valuation metrics simply.

## How to Run
1.  Ensure `.env` has your `OPENROUTER_API_KEY`.
2.  Run `streamlit run app.py`.

The UI follows a clean, professional **light theme** (white background, black font)
## Features
- **Reverse DCF** – Back‑solve market implied growth rate.
- **Competitor Matrix** – Scatter plot of revenue growth vs EV/EBITDA.
- **Better Alternative Engine** – Suggests a superior peer with a simple "Why" explanation.
- **Ownership & Activity** – Shows recent insider trades and top institutional holders, plus a 3‑bullet AI summary.
- **Technical Analysis** – 1‑year candlestick chart with SMA 50/200 and RSI indicator.
- **AI Risk Summary** – Highlights top 3 business risks.
- **Educational Explanations** – AI‑generated plain‑English insights for all advanced sections.

## Prerequisites
- Python 3.10+ (tested on 3.12)
- Git (optional, for cloning the repo)
- An OpenRouter API key – store it in a `.env` file as `OPENROUTER_API_KEY=your_key`

## Installation
```bash
# Clone the repository (or download the zip)
git clone https://github.com/vikramlingam/AlphaSeeker-AI.git
cd AlphaSeeker-AI

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # on macOS/Linux
# or
# venv\Scripts\activate   # on Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "OPENROUTER_API_KEY=YOUR_KEY_HERE" > .env
```

## Running the App
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`. You will see four tabs:
1. **Dashboard** – basic company info and valuation.
2. **Technical Analysis** – chart with SMA/RSI and AI explanation.
3. **Deep Dive Valuation** – Reverse DCF sliders.
4. **Competitor Matrix** – peer scatter plot and "Better Alternative".
5. **Ownership & Activity** – insider & institutional data with AI summary.

## Usage Tips for Beginners
- **Select a ticker** in the sidebar and press **Load Data**.
- Use the **Explain Chart** button to get a plain‑English description of the technical signals.
- Click **Analyze Risks** to see the top three risks identified by the AI.
- Adjust the DCF sliders to see how valuation changes with different assumptions.

## Project Structure
```
AlphaSeeker-AI/
├─ app.py                # Streamlit UI
├─ finance_engine.py    # Data fetching & calculations
├─ agent_engine.py      # LLM prompts & responses
├─ requirements.txt      # Python dependencies
├─ .env                 # API key (not committed)
└─ README.md            # This file
```

## Contributing
Feel free to open issues or submit pull requests. When adding new features, keep the UI consistent with the light theme and add educational explanations for any advanced analytics.

## License
This project is licensed under the MIT License.
---
