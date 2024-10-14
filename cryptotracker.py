from tkinter import *
from PIL import ImageTk, Image
import requests

# Colors
co1 = "white"
co2 = "#d4ac0d"
co3 = "#000000"

window = Tk()
window.title(" ")
window.geometry("320x800")  
window.configure(bg=co1)

def fetch_price():
    api_link = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,php,cad,eur"
    
    try:
        res = requests.get(api_link)
        res.raise_for_status()  # Raise an error for bad respons3es
        dic = res.json()

        # Extract values
        usd_value = dic['bitcoin']['usd']
        usd_formatted_value = "${:,.3f}".format(usd_value)
        usd["text"] = usd_formatted_value

        php_value = dic['bitcoin']['php']
        php_formatted_value = "Philippines : ₱ {:,.3f}".format(php_value)
        php["text"] = php_formatted_value

        cad_value = dic['bitcoin']['cad']
        cad_formatted_value = "Canada : CAD {:,.3f}".format(cad_value)
        cad["text"] = cad_formatted_value

        eur_value = dic['bitcoin']['eur']
        eur_formatted_value = "Europe : € {:,.3f}".format(eur_value)
        euro["text"] = eur_formatted_value

    except requests.exceptions.RequestException as e:
        print(f"Error fetching price data: {e}")  

    frame_body.after(40000, fetch_price)  # Refresh every 15 seconds

def fetch_news():
    news_api_key = "ed527df85fbd73c4f798279978a3201df3d1a346"  
    api_link = f"https://cryptopanic.com/api/v1/posts/?auth_token={news_api_key}&currencies=BTC"

    try:
        res = requests.get(api_link)
        res.raise_for_status()  # Raise an error for bad responses
        news_data = res.json()

        # Clear previous news
        for widget in news_1.winfo_children():
            widget.destroy()

        # Display only the top 5 news items
        for item in news_data['results'][:5]:  
            title = item['title']
            title_label = Label(news_1, text=title, bg=co2, fg=co3, wraplength=280, justify="left", font=("Lato 12"))
            title_label.pack(pady=5)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")  

    news_1.after(100000, fetch_news)  # Refresh every minute
 

# Frame and Label setup 
frame_head = Frame(window, width=320, height=50, bg=co1)
frame_head.grid(row=1, column=0)

frame_body = Frame(window, width=320, height=700, bg=co2)  # Adjusted height for news
frame_body.grid(row=2, column=0)

image_1 = Image.open('images/bitcoin.png')
image_1 = image_1.resize((30, 30))
image_1 = ImageTk.PhotoImage(image_1)

icon_1 = Label(frame_head, image=image_1, bg=co1)
icon_1.place(x=10, y=10)

name = Label(frame_head, padx=0, text="Bitcoin Price", fg=co3, width=14, height=1, anchor="center", font=("Lato 20"))
name.place(x=50, y=10)

usd = Label(frame_body, text="$00000", width=14, height=1, font=("Lato 30 bold"), bg=co2, fg=co3, anchor="center")
usd.place(x=0, y=28)

php = Label(frame_body, text="00000", height=1, font=("Lato 15 bold"), bg=co2, fg=co3, anchor="center")
php.place(x=10, y=130)

cad = Label(frame_body, text="00000", height=1, font=("Lato 15 bold"), bg=co2, fg=co3, anchor="center")
cad.place(x=10, y=170)

euro = Label(frame_body, text="00000", height=1, font=("Lato 15 bold"), bg=co2, fg=co3, anchor="center")
euro.place(x=10, y=210)

news_1 = Label(frame_body, text="blablabla", height=1, bg=co2, font=("Lato 15 bold"), fg=co3, anchor="center")
news_1.place(x=10, y=300)


fetch_price()  # Fetch Bitcoin price
fetch_news()   # Fetch news

window.mainloop()