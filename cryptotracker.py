from tkinter import *
from PIL import ImageTk, Image
import requests
import time
import webbrowser  

#Colors
COLOR_PRIMARY = "#7d9a9e"
COLOR_SECONDARY = "#2e4053"
COLOR_TEXT = "#cacfd2"


window = Tk()
window.title("Crypto Tracker")
window.geometry("320x700")  
window.configure(bg=COLOR_PRIMARY)
window.resizable(False, False)  # Bawal iresize


current_crypto = "bitcoin"  # Bitcoin lagi unang lalabas

# Caching temp storage para lang ma access natin ng mabilsi yung data and maiwasan nadin yung request ng request sa API
price_cache = {} # Pag valid pa yung price within 3 mins hindi mag papalit ng price
news_cache = {} # Basahin nalng yung price cache
cache_expiry = 180  # Pag na expire within 3 minutes mag rerequest sa API then mag uupdate yung price and news natin
last_request_time = {}
last_news_request_time = {}

# Ki-nocontrol yung delay bago mag fetch ng news pag katapos ma hit yung 1 min bago mag retry
retry_delay = 60  

# Debouncing control para maiwasan yung frequent API calls
last_switch_time = 0 # Na rerecord dito yung kung ilang seconds na switch yung app like btc to sol vice versa
debounce_duration = 30  # Debouncing para sa mga tangang mag spam click mahihit yung rate limit pag wala nito

# Fetch current price for the selected cryptocurrency
def fetch_price():
    global current_crypto # Global para ma access kahit saan

    # Check if cached data exists and is still valid
    if current_crypto in price_cache and time.time() - last_request_time.get(current_crypto, 0) < cache_expiry:
        display_prices(price_cache[current_crypto])
    else:
        api_link = f"https://api.coingecko.com/api/v3/simple/price?ids={current_crypto}&vs_currencies=usd,php,cad,eur"

        try:
            res = requests.get(api_link)
            res.raise_for_status()
            data = res.json()

            # Cache the data and record the request time
            price_cache[current_crypto] = data[current_crypto]
            last_request_time[current_crypto] = time.time()

            # Display fetched prices
            display_prices(data[current_crypto])
        except requests.exceptions.HTTPError as e:
            handle_http_error(e, current_crypto)

    # Mag refresh yung frame body exp nakakuha na ng bagong data si cache sa api after 40 seconds pa mababago
    frame_body.after(40000, fetch_price) 

# Nag didisplay ng prices sa UI
def display_prices(data):
    usd_value = data['usd']
    usd["text"] = "${:,.3f}".format(usd_value)
    php["text"] = f"Philippines : ₱ {data['php']:,.3f}"
    cad["text"] = f"Canada : CAD {data['cad']:,.3f}"
    euro["text"] = f"Europe : € {data['eur']:,.3f}"

# Fetch news related to the selected cryptocurrency
# Itong Kupal na to 
def fetch_news(retry=False):
    global current_crypto

    if current_crypto in news_cache and time.time() - last_news_request_time.get(current_crypto, 0) < cache_expiry:
        display_news(news_cache[current_crypto])
    else:
        news_api_key = "19fb694453ac4a40bf5b6bf1779c4c49"  
        api_link = f"https://newsapi.org/v2/everything?q={current_crypto}&apiKey={news_api_key}&pageSize=10&sortBy=publishedAt&language=en"

        try:
            res = requests.get(api_link)
            res.raise_for_status()
            news_data = res.json()


            news_cache[current_crypto] = news_data['articles']
            last_news_request_time[current_crypto] = time.time()

            # Display fetched news
            display_news(news_data['articles'])
        except requests.exceptions.HTTPError as e:
            handle_http_error(e, current_crypto, retry)

    news_1.after(180000, fetch_news)

# Handle HTTP errors
def handle_http_error(e, crypto, retry=False):
    if e.response.status_code == 429:  # Handle Too Many Requests
        if not retry:
            print(f"Rate limit exceeded for {crypto}. Retrying in 1 minute...")
            news_1.after(retry_delay * 1000, lambda: fetch_news(retry=True))  # Retry after 1 minute
    else:
        print(f"Error fetching data for {crypto}: {e}")


def display_news(news_data):
    # Clear previous news
    for widget in news_1.winfo_children():
        widget.destroy()


    for i, item in enumerate(news_data[:5]):
        title = item.get('title', 'No Title')
        url = item.get('url', '#')  # Extract URL


        title_label = Label(news_1, text=f"{i + 1}. {title}", bg=COLOR_SECONDARY, fg=COLOR_TEXT, wraplength=280, justify="left", font=("Lato 12"))
        title_label.pack(pady=2)

        
        title_label.bind("<Button-1>", lambda e, url=url: webbrowser.open(url))

# Toggle 
def toggle_crypto():
    global current_crypto, last_switch_time

    current_time = time.time()
    
    if current_time - last_switch_time >= debounce_duration:  
        last_switch_time = current_time
        
        current_crypto = "solana" if current_crypto == "bitcoin" else "bitcoin"
        name.config(text=f"{current_crypto.capitalize()} Price")
        
       
        fetch_price()
        fetch_news()

# Frame and Label setup 
frame_head = Frame(window, width=320, height=50, bg=COLOR_PRIMARY)
frame_head.grid(row=1, column=0)

frame_body = Frame(window, width=320, height=700, bg=COLOR_SECONDARY)
frame_body.grid(row=2, column=0)

image_path = 'images/bitcoin.png'  
image_1 = Image.open(image_path).resize((30, 30))
icon_image = ImageTk.PhotoImage(image_1)

icon_1 = Label(frame_head, image=icon_image, bg=COLOR_PRIMARY)
icon_1.place(x=10, y=10)


name = Label(frame_head, padx=0, text="Bitcoin Price", fg=COLOR_TEXT, width=14, height=1, anchor="center", font=("Lato 20"), cursor="hand2", bg=COLOR_PRIMARY)
name.place(x=50, y=10)
name.bind("<Button-1>", lambda e: toggle_crypto())  

# Labels for displaying prices
usd = Label(frame_body, text="$00000", width=14, height=1, font=("Lato 30 bold"), bg=COLOR_SECONDARY, fg=COLOR_TEXT, anchor="center")
usd.place(x=0, y=28)

php = Label(frame_body, text="00000", height=1, font=("Lato 15 bold"), bg=COLOR_SECONDARY, fg=COLOR_TEXT, anchor="center")
php.place(x=0, y=108)

cad = Label(frame_body, text="00000", height=1, font=("Lato 15 bold"), bg=COLOR_SECONDARY, fg=COLOR_TEXT, anchor="center")
cad.place(x=0, y=168)

euro = Label(frame_body, text="00000", height=1, font=("Lato 15 bold"), bg=COLOR_SECONDARY, fg=COLOR_TEXT, anchor="center")
euro.place(x=0, y=230)


news_1 = Frame(frame_body, width=320, height=300, bg=COLOR_SECONDARY)
news_1.place(x=0, y=280)


fetch_price()
fetch_news()

window.mainloop()


#### PS: Tangina sumobra sa hirap