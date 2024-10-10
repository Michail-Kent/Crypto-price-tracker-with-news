from tkinter import *
from PIL import ImageTk, Image
import requests

# Colors na ginamit
co1 = "white"
co2 = "#d4ac0d"
co3 = "#000000"

window = Tk()
window.title(" ")
window.geometry("320x800")  
window.configure(bg=co1)

def fetch_price():
    api_link = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,php,cad,eur" #api ng coingecko mas stable
    
    try:
        res = requests.get(api_link)
        res.raise_for_status()  #raise ng error para sa bad response
        dic = res.json()#naka json kasi ang data kaya may .json

        # ito extract values
        #kung nag tataka kayo bat may {:,.3f} ewan ko kay google ganyan daw para lumabas yung decimals
        
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
        print(f"Error fetching price data: {e}")  #ito error handling pag na reach na yung rate limit

    frame_body.after(40000, fetch_price)  # mag rerefresh yung body ng UI kada 40 seconds

def fetch_news():
    news_api_key = "ed527df85fbd73c4f798279978a3201df3d1a346"  #api key galing sa crypto panic
    api_link = f"https://cryptopanic.com/api/v1/posts/?auth_token={news_api_key}&currencies=BTC" 

    try:
        res = requests.get(api_link)
        res.raise_for_status()  #same lang din to sa fetch price tignan nyo nalang don
        news_data = res.json()

        # Clear previous news pag nag lipat
        for widget in news_1.winfo_children():
            widget.destroy()#para hindi na lumabas yung btc news pag nilipat sa solana

        # Display ng kahit ilang news pero trip ko tatlo eh
        for item in news_data['results'][:3]:  
            title = item['title']
            title_label = Label(news_1, text=title, bg=co2, fg=co3, wraplength=280, justify="left", font=("Lato 12"))
            title_label.pack(pady=5)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")  

    news_1.after(120000, fetch_news)  # Refresh every 2 minuts pero gagawin kong 5 mins yan sa next version para maiwasan din natin ma hit yung rate limit
                                      # kasi isa lamang tayong hamak na hampas lupa walang pambili ng api na mataas rate limit

# Frame and Label setup #alam nyo na to guys
frame_head = Frame(window, width=320, height=50, bg=co1)
frame_head.grid(row=1, column=0)

frame_body = Frame(window, width=320, height=700, bg=co2) 
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
