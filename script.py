#!/usr/bin/envi python
import urllib2
import telepot
import bs4
import requests
import time
import schedule
from telepot.loop import MessageLoop
commands = {
            'help': 'Mostrar comandos disponibles',
            'libro': 'Obtener el libro gratuito del dia de PacktPub',
            'subscribe': 'Suscribirse para recibir el libro gratuito diariamente',
            'unsubscribe': 'Darse de baja y dejar de recibir el libro diariamente'
           }
token = "497843902:AAH1kQZhZs7LxEVtCHB5mCa8nNaTvdIC3dc"
TelegramBot = telepot.Bot(token)

class Client(object):
    def handle(self,msg):
        chat_id = msg['chat']['id']
        command = msg['text']
        print 'Comando recibido: %s' % command
        if command == '/subscribe':
            self.subscribe(chat_id)
        elif command == '/libro':
            client.send_libro(chat_id)
        elif command == '/unsubscribe':
            client.unsubscribe(chat_id)
        else:
            self.commands(chat_id)

    def waiting_command(self):
        MessageLoop(TelegramBot, self.handle).run_as_thread()
        
        print 'Esperando comando ...'
        while 1:
            schedule.run_pending()
            time.sleep(10)

    def subscribe(self,chat_id):
        found = False
        f=open("suscritos.txt","a+r")
        for line in f:
            if str(chat_id) in line:
                TelegramBot.sendMessage(chat_id, "Ya esta suscrito!")
                found = True
        if found==False:
            TelegramBot.sendMessage(chat_id, "Se ha suscrito correctamente!")
            f.write(str(chat_id)+"\n")
        f.close()
    def unsubscribe(self,chat_id):
        f = open("suscritos.txt","r")
        lines = f.readlines()
        f.close()
        f=open("suscritos.txt","w")
        suscrito = False
        for line in lines:
            if str(chat_id) not in line:
                f.write(line)
            else:
                suscrito = True
        f.close()
        if suscrito:
            TelegramBot.sendMessage(chat_id, "Se ha dado de baja correctamente!")
        else:
            TelegramBot.sendMessage(chat_id, "No podemos dar de baja ya que no esta suscrito!")

    def send_libro_list(self):
        f=open("suscritos.txt","r")
        for line in f:
            client.send_libro(line)
        f.close()

    def commands(self,chat_id):
        help_text = "Comandos disponibles: \n"
        for key in commands:
            help_text += "/" + key + ": "
            help_text += commands[key] + "\n"
        TelegramBot.sendMessage(chat_id, help_text)

    def get_web(self,url):
        # getweb
        f = urllib2.urlopen(url)
        html = f.read()
        f.close()
        return html
    def get_titol(self,html):
        #titol
        titol_html = html.find("div","dotd-title")
        titol_html = titol_html.find("h2")
        titol = titol_html.text.strip()
        return titol
    def get_resum(self,html):
        #extracte
        resum = html.find("div","dotd-main-book-summary")
        resum = resum.find_all("div")
        resum = resum[2].text.strip()
        return resum
    def get_objectius(self,html):
        #objectius
        objectius = html.find("div","dotd-main-book-summary")
        objectius = objectius.find_all("li")
        return objectius
    def get_imatge(self,html):
        #imatge llibre
        imatge = html.find("div","dotd-main-book-image")
        imatge = imatge.find('img')['src']
        imatge = "https:" + imatge
        return imatge
    def login_page(self):
        html = self.get_web("https://www.packtpub.com/packt/offers/free-learning?from=block")
        soup = bs4.BeautifulSoup(html,"lxml")
        buil_id = soup.find_all("form")
        buil_id = buil_id[1]
        buil_id = buil_id.find_all("input")
        buil_id = buil_id[3]['value']
        session = requests.Session()
        dades= {'email':'ori.jorge@gmail.com','password':'AA11dd22', 'op': 'Login', 'form_build_id' : buil_id, 'form_id' : 'packt_user_login_form'}
        url = "https://www.packtpub.com/packt/offers/free-learning?from=block"
        with requests.Session() as s:
            p = s.post(url, data=dades)
            print p.text
        print(dades)

        #test = session.post(url, data=dades)
        #print(test.status_code, test.reason)

        html = self.get_web("https://www.packtpub.com/account/my-ebooks")
        soup = bs4.BeautifulSoup(html,"lxml")
        link = soup.find("div", "download-container")
        #print(soup)
    def send_libro(self,chat_id):
        html = self.get_web("https://www.packtpub.com/packt/offers/free-learning?from=block")
        soup = bs4.BeautifulSoup(html,"lxml")
        titol = self.get_titol(soup)
        resum = self.get_resum(soup)
        objectius = self.get_objectius(soup)
        imatge = self.get_imatge(soup)
        tele_mens = "<b>"+titol+"</b>"+"\n"+"<i>"+resum+"</i>\n"
        print("***** Titol ******")
        print(titol)
        print("***** Resum ******")
        print(resum)
        print("***** Objectius ******")
        for objectiu in objectius:
            print(objectiu.text)
            tele_mens+="<pre>"+objectiu.text+"</pre>\n"
        TelegramBot.sendMessage(parse_mode='HTML', chat_id=chat_id, text=tele_mens)
        TelegramBot.sendPhoto(chat_id, imatge)

if __name__ == "__main__":
    client = Client()
    schedule.every().day.at("21:15").do(client.send_libro_list)
    client.waiting_command()
