# Crypto Tracker Documentation
Overview
Crypto Tracker is a Python-based desktop application developed using Tkinter. It allows users to track cryptocurrency prices, analyze historical trends, and view sentiment from news articles related to specific cryptocurrencies.

APIs Integrated
The application integrates the following APIs to provide its functionalities:

CoinGecko API:

Purpose: Fetch current and historical price data for cryptocurrencies.
Endpoints Used:
Current Price:
  https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd,php,cad,eur
Historical Market Chart:
  https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=7

NewsAPI:

  Purpose: Fetch news articles related to cryptocurrencies to analyze sentiment.
  Endpoints Used:
    Everything:
      https://newsapi.org/v2/everything?q={crypto}&apiKey={apiKey}&pageSize=100&sortBy=publishedAt&language=en

User Interaction
The application provides an interactive GUI with the following features:

Main Window: Displays the current price of the selected cryptocurrency in various currencies (USD, PHP, CAD, EUR).
Cryptocurrency Selection: Users can select different cryptocurrencies (Bitcoin, Solana) via buttons to view their prices.
Market Trends: Users can view historical price trends and sentiment analysis over the past week by selecting "Market Trends."
News Sentiment: Users can read the latest news articles about the selected cryptocurrency, with sentiment scores displayed for each article.

Button Functions
Quit: Exits the application.
Bitcoin: Switches the view to track Bitcoin.
Solana: Switches the view to track Solana.
Market Trends: Displays historical data and sentiment analysis for the selected cryptocurrency.

Setup/Configuration Instructions
To set up and run the Crypto Tracker application, follow these steps:

Environment Setup:

Ensure you have Python installed (version 3.6 or higher).
Install the required packages using pip:
  "pip install requests Pillow matplotlib textblob numpy"

API Key Configuration:

Sign up for an account at NewsAPI and obtain an API key.
Replace the placeholder in the code with your API key:

Additional Notes
The application is configured to cache data for 180 seconds to minimize API calls. If the cache is still valid, it uses cached data instead of making a new API call.
Error handling is implemented for HTTP requests to handle rate limiting and other potential issues.

