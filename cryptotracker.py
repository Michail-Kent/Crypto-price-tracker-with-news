from tkinter import *  #all components from tkinter for GUI
from PIL import ImageTk, Image  # handling images
import requests  #making HTTP requests
import time  # for handling time-related tasks
import webbrowser  # open web pages in a browser
from textblob import TextBlob  #  performing text analysis
import matplotlib.pyplot as plt  #  plotting graphs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Embed matplotlib plots in tkinter
import numpy as np  # I numpy for numerical operations
from datetime import datetime, timezone  # for handling date and time


# Colors
COLOR_PRIMARY = "#7d9a9e"
COLOR_SECONDARY = "#2e4053"
COLOR_TEXT = "#cacfd2"

# Window configuration
window = Tk()
window.title("Crypto Tracker")
window.geometry("400x700")
window.configure(bg=COLOR_PRIMARY)
window.resizable(False, False)

# Global variables for cryptocurrency and caching
current_crypto = "bitcoin"  
price_cache = {}  
news_cache = {}  
cache_expiry = 180  
last_request_time = {} #track last price request times
last_news_request_time = {} #track last news request times
retry_delay = 60  
price_update_id = None #ID for scheduled price update tasks

# Initialize frames
frame_body = Frame(window, width=320, height=700, bg=COLOR_SECONDARY)
frame_body.pack(fill="both", expand=True)

# Create a separate frame for the buttons
button_frame = Frame(frame_body, bg=COLOR_SECONDARY)
button_frame.pack(pady=20)

quit_button = Button(button_frame, text="Quit", command=window.quit, bg=COLOR_PRIMARY, fg=COLOR_TEXT)
quit_button.pack(side=LEFT, padx=10)

# Function to create the Market Trend frame
def create_market_trend_frame():
    market_trend_frame = Frame(frame_body, bg=COLOR_SECONDARY)

    trend_label = Label(market_trend_frame, text="Market Trends", bg=COLOR_SECONDARY, fg=COLOR_TEXT, font=("Lato", 20))
    trend_label.pack(pady=10)

    # Fetch historical data and display it
    plot_historical_data(market_trend_frame)

    back_button = Button(market_trend_frame, text="Back", command=lambda: switch_to_frame(current_crypto), bg=COLOR_PRIMARY, fg=COLOR_TEXT)
    back_button.pack(pady=10)

    return market_trend_frame

def plot_historical_data(parent_frame):
    # Fetch historical price data for the current cryptocurrency
    price_data = fetch_historical_prices(current_crypto)
    # Fetch historical sentiment data for the current cryptocurrency
    sentiment_data = fetch_sentiment_data(current_crypto)

    # Check if the lengths of the fetched data are equal to 7 (for the last 7 days)
    if len(price_data) != 7 or len(sentiment_data) != 7:
        # Print an error message if there is a mismatch in data lengths
        print("Data length mismatch. Prices:", len(price_data), "Sentiments:", len(sentiment_data))
        return  # Exit the function if data lengths do not match

    # Create a plot with a specified size (4 inches by 3 inches)
    fig, ax1 = plt.subplots(figsize=(4, 3))

    # Clear any previous plots in the axes to avoid overplotting
    ax1.clear()

    # Create a list of days representing the last 7 days
    days = list(range(7))
    ax1.set_xlabel('Days')  # Set label for the x-axis
    ax1.set_ylabel('Price (USD)', color='tab:blue')  # Set label for the primary y-axis with a blue color
    # Plot the historical price data
    ax1.plot(days, price_data, color='tab:blue', label='Price (USD)')
    ax1.tick_params(axis='y', labelcolor='tab:blue')  # Set the color of the ticks on the primary y-axis

    # Create secondary y-axis for sentiment data
    ax2 = ax1.twinx()  
    ax2.set_ylabel('Average Sentiment', color='tab:red')  # S label for  secondary y-axis with  red color
    # Plot the historical sentiment data with a dashed line
    ax2.plot(days, sentiment_data, color='tab:red', label='Average Sentiment', linestyle='--')
    ax2.tick_params(axis='y', labelcolor='tab:red')  # Set the color of the ticks on the secondary y-axis

   #It will change dynamically based on the current cryptocurrency.
    plt.title(f"{current_crypto.capitalize()} Price and Sentiment Trend")
    fig.tight_layout()  # Adjust the layout to make room for labels and titles

    # Embed the plot into the Tkinter parent frame
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()  # Draw the plot on the canvas
    # Pack the canvas widget into the parent frame to make it visible
    canvas.get_tk_widget().pack(fill='both', expand=True)

    

def fetch_historical_prices(crypto):
    # Construct the API endpoint URL for fetching historical market chart data for the specified cryptocurrency
    api_link = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=7"
    max_retries = 5  # Maximum number of retries for the API request
    
    for attempt in range(max_retries):
        try:
            # Send a GET request to the API endpoint
            res = requests.get(api_link)
            # Raise an error if the response status code indicates an error
            res.raise_for_status()
            # Parse the JSON response data
            data = res.json()
            
            # Extract price data from the response; prices are in the format [timestamp, price]
            prices = data['prices']
            
            # Prepare a dictionary to store the closing prices for each day
            closing_prices = {}
            
            # Loop through the price data to find prices closest to the end of each day 
            for price_data in prices:
                timestamp, price = price_data
                # Convert the timestamp to a date and time object
                date = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).date()
                time_of_day = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).time()
                
                # Check if the date already exists in closing_prices or if the current price is closer to 23:59
                if date not in closing_prices or abs(datetime.combine(date, time_of_day) - datetime.combine(date, datetime.strptime("23:59", "%H:%M").time())) < abs(datetime.combine(date, closing_prices[date][1]) - datetime.combine(date, datetime.strptime("23:59", "%H:%M").time())):
                    # Update the closing price for that date
                    closing_prices[date] = (price, time_of_day)
            
            # Sort the dates in descending order and return only the prices
            sorted_closing_prices = [closing_prices[day][0] for day in sorted(closing_prices.keys(), reverse=True)]
            
            # If there are at least 7 closing prices, return the most recent 7
            if len(sorted_closing_prices) >= 7:
                return sorted_closing_prices[:7]
            else:
                # If there are fewer than 7 prices, fill the missing days with the last available price
                last_price = sorted_closing_prices[-1] if sorted_closing_prices else 0
                return sorted_closing_prices + [last_price] * (7 - len(sorted_closing_prices))
                
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors; specifically check for rate limit errors
            if res.status_code == 429:  # Rate limit exceeded
                print("Rate limit exceeded. Retrying...")
                time.sleep(60)  # Wait for 1 minute before retrying
            else:
                handle_http_error(e)  # Call error handling function for other HTTP errors
                return []  # Return an empty list on error
        except Exception as e:
            # Catch any other exceptions that occur and print an error message
            print(f"An error occurred: {e}")
            return []  # Return an empty list on error
    
    print("Max retries exceeded. Unable to fetch historical prices.")
    return []  # Return an empty list if maximum retries are reached without success



def fetch_sentiment_data(crypto):
    # Get news articles for the last 7 days and calculate average sentiment
    news_api_key = "19fb694453ac4a40bf5b6bf1779c4c49"
    api_link = f"https://newsapi.org/v2/everything?q={crypto}&apiKey={news_api_key}&from={time.strftime('%Y-%m-%d', time.gmtime(time.time() - 604800))}&to={time.strftime('%Y-%m-%d')}&pageSize=100&sortBy=publishedAt&language=en"
    
    try:
        # Send a GET request to the news API using the constructed URL
        res = requests.get(api_link)
        # Check if the response is successful
        res.raise_for_status()
        # Parse the JSON response to get the news articles data
        news_data = res.json()
        articles = news_data['articles']  # Extract the list of articles from the response

        # Analyze the sentiment of each article using the defined function
        sentiments = analyze_sentiment(articles)
        
        # Calculate and return the average sentiment score for the last 7 days
        return [np.mean(sentiments)] * 7  
    except requests.exceptions.HTTPError as e:
        # If an HTTP error occurs during the request handle it with the defined error handler
        handle_http_error(e)
        # Return a default value of zero for each day if there is an error in fetching data
        return [0] * 7  
def switch_to_frame(crypto):
    global current_crypto

    # Hide all existing children in frame_body except for button_frame
    for widget in frame_body.winfo_children():
        if widget != button_frame:  
            widget.pack_forget()

    if crypto == "market_trend":
        market_trend_frame = create_market_trend_frame()
        market_trend_frame.pack(fill="both", expand=True)
        window.geometry("400x800")  # Resize the window for market trends
    else:
        current_crypto = crypto
        create_frame()  # Recreate the main frame
        fetch_price()  # Fetch prices for the selected cryptocurrency
        fetch_news(current_crypto)  # Update news for the selected cryptocurrency
        window.geometry("400x700")  # Resize back to the original size


# Fetch current price for the selected cryptocurrency
def fetch_price():
    global current_crypto, price_update_id

    # Cancel any existing scheduled fetch_price calls to avoid overlapping requests
    if price_update_id is not None:
        try:
            frame_body.after_cancel(price_update_id)  # Cancel the previously scheduled fetch
        except TclError:
            # Handle case where the scheduled fetch ID is no longer valid
            print("Attempted to cancel a fetch that was no longer valid.")
            return
    
    # Check if we have cached price data and it is still valid
    if current_crypto in price_cache and time.time() - last_request_time.get(current_crypto, 0) < cache_expiry:
        display_prices(price_cache[current_crypto])  # Display cached prices
    else:
        # Construct the API link to fetch the current price for the selected cryptocurrency
        api_link = f"https://api.coingecko.com/api/v3/simple/price?ids={current_crypto}&vs_currencies=usd,php,cad,eur"
        try:
            # Make the API request to fetch the latest price
            res = requests.get(api_link)
            res.raise_for_status()  # Raise an error for HTTP error responses
            data = res.json()  # Parse the JSON response

            # Cache the data for future use
            price_cache[current_crypto] = data[current_crypto]
            last_request_time[current_crypto] = time.time()  # Update the request time

            display_prices(data[current_crypto])  # Display the fetched prices

        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors by calling the error handling function
            handle_http_error(e)
        except Exception as e:
            # Catch any other exceptions and print the error message
            print(f"An error occurred while fetching price: {e}")

    try:
        # Schedule the next price fetch only if the main window is still open
        if window.winfo_exists():
            price_update_id = frame_body.after(40000, fetch_price)  # Fetch price every 40 seconds
        else:
            # If the window is closed, stop further price updates
            print("The window has been closed; stopping further updates.")
    except TclError:
        # Handle case where the scheduled fetch cannot be set because the window is closed
        print("The scheduled fetch was not executed because the window has been closed.")


# Display prices in USD, PHP, CAD, and EUR
def display_prices(data):
    try:
        usd_value = data['usd']
        usd["text"] = "${:,.3f}".format(usd_value)
        php["text"] = f"Philippines : ₱ {data['php']:,.3f}"
        cad["text"] = f"Canada : CAD {data['cad']:,.3f}"
        euro["text"] = f"Europe : € {data['eur']:,.3f}"
    except Exception as e:
        print(f"An error occurred while displaying prices: {e}")

# Analyze sentiment of news articles
def analyze_sentiment(articles):
    sentiments = []
    for article in articles:
        # Extract the article content or description for sentiment analysis
        content = article.get('content', '') or article.get('description', '')
        if content:  
            analysis = TextBlob(content)
            sentiments.append(analysis.sentiment.polarity)  #Get polarity
        else:
            sentiments.append(0)  # Neutral if no content is available
    return sentiments

# Fetch latest news for the selected cryptocurrency
def fetch_news(query=None, category=None, retry_count=0, max_retries=3):
    global current_crypto

    # Use cached news if valid and not expired
    if current_crypto in news_cache and time.time() - last_news_request_time.get(current_crypto, 0) < cache_expiry:
        # Analyze sentiments from cached news articles
        sentiments = analyze_sentiment(news_cache[current_crypto])  
        # Display the cached news articles and their sentiments
        display_news(news_cache[current_crypto], sentiments)  
    else:

        news_api_key = "8c04af25426b41b0beaa1b3f3d00703d"
        query = query or current_crypto  

        api_link = f"https://newsapi.org/v2/everything?q={query}&apiKey={news_api_key}&pageSize=10&sortBy=publishedAt&language=en"

        try:
            #Make the API request to fetch news articles
            res = requests.get(api_link)
            res.raise_for_status()  #Raise an error for HTTP error responses
            news_data = res.json()  #Parse the JSON response

            #Cache the fetched news articles for future use
            news_cache[current_crypto] = news_data['articles']
            last_news_request_time[current_crypto] = time.time()  # Update the last request time

            #Analyze sentiment of the newly fetched news articles
            sentiments = analyze_sentiment(news_data['articles'])
            #Display the news articles along with their sentiments
            display_news(news_data['articles'], sentiments)  
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors allowing for retries if the maximum hasnt been reached
            handle_http_error(e, retry_count, max_retries) 

# Handle HTTP errors (rate limits)
def handle_http_error(e, retry_count, max_retries):
    if e.response.status_code == 429:  # Too Many Requests
        print("Rate limit exceeded. Retrying in 1 minute...")
        time.sleep(retry_delay)
        if retry_count < max_retries:
            fetch_news(retry_count=retry_count + 1, max_retries=max_retries)  # Increment retry count
        else:
            print("Max retries reached. Could not fetch news.")
    else:
        print(f"An error occurred: {e}")

# Display latest news in the frame
def display_news(news_data, sentiments):
    # Clear existing news
    for widget in news_1.winfo_children():
        widget.destroy()

    # Display up to 5 news articles with sentiment analysis
    for i, (item, sentiment) in enumerate(zip(news_data[:4], sentiments[:4])):  # Limit to 4 articles
        title = item.get('title', 'No Title')
        url = item.get('url', '#')  # Extract URL
        title_label = Label(news_1, text=f"{i + 1}. {title}", bg=COLOR_SECONDARY, fg=COLOR_TEXT, wraplength=280, justify="left", font=("Lato 12"))
        title_label.pack(pady=2)
        title_label.bind("<Button-1>", lambda e, url=url: webbrowser.open(url))  # Make clickable

        # Display sentiment score
        sentiment_label = Label(news_1, text=f"Sentiment: {'Positive' if sentiment > 0 else 'Negative' if sentiment < 0 else 'Neutral'}", bg=COLOR_SECONDARY, fg=COLOR_TEXT, wraplength=280, justify="left", font=("Lato 10"))
        sentiment_label.pack(pady=2)

# Create and pack main frame components
def create_frame():
    global usd, php, cad, euro, news_1

    # Clear existing children except for the button_frame
    for widget in frame_body.winfo_children():
        if widget != button_frame:  
            widget.destroy()

    # Header for dynamic cryptocurrency
    header = Label(frame_body, text=f"{current_crypto.capitalize()} Tracker", bg=COLOR_SECONDARY, fg=COLOR_TEXT, font=("Lato 24"))
    header.pack(pady=10)


    price_frame = Frame(frame_body, bg=COLOR_SECONDARY)
    price_frame.pack(pady=10)

    usd = Label(frame_body, bg=COLOR_SECONDARY, fg=COLOR_TEXT, font=("Lato", 14))
    usd.pack(pady=5)
    php = Label(frame_body, bg=COLOR_SECONDARY, fg=COLOR_TEXT, font=("Lato", 14))
    php.pack(pady=5)
    cad = Label(frame_body, bg=COLOR_SECONDARY, fg=COLOR_TEXT, font=("Lato", 14))
    cad.pack(pady=5)
    euro = Label(frame_body, bg=COLOR_SECONDARY, fg=COLOR_TEXT, font=("Lato", 14))
    euro.pack(pady=5)

    news_1 = Frame(frame_body, bg=COLOR_SECONDARY)
    news_1.pack(pady=10)


Button(button_frame, text="Bitcoin", command=lambda: switch_to_frame("bitcoin"), bg=COLOR_PRIMARY, fg=COLOR_TEXT).pack(side=LEFT, padx=10)
Button(button_frame, text="Solana", command=lambda: switch_to_frame("solana"), bg=COLOR_PRIMARY, fg=COLOR_TEXT).pack(side=LEFT, padx=10)
Button(button_frame, text="Market Trends", command=lambda: switch_to_frame("market_trend"), bg=COLOR_PRIMARY, fg=COLOR_TEXT).pack(side=LEFT, padx=10)


create_frame()
fetch_price()
fetch_news(current_crypto)

window.mainloop()