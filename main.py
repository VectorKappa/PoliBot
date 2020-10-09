from __future__ import unicode_literals
import asyncio
import discord
import youtube_dl
import credentials
import re
from urllib.request import urlopen
from json import load
from discord.ext import tasks, commands
import datetime
import time
import random
import subprocess

# Wyciszenie błędów youtube_dl
youtube_dl.utils.bug_reports_message = lambda: ''

# Import poufnych danych
token = credentials.getToken()
id_serwera = credentials.getServerId()
lista_roli = credentials.getRole()


# Wariacje zmiennych
wariacje_nauczycieli = ("nauczyciel", "teacher", "nauczycielka")

# Komunikaty
wiadomosc_info = u"To jest bot przeznaczony dla Zespołu Szkół Poligraficzno-Mechanicznych im. Armii Krajowej w Katowicach. \n Aby uzyskać listę komend, wpisz $komendy \n Więcej info: https://github.com/VectorKappa/PoliBot"
lista_komend = u"```Lista komend bota: \n $komendy - wysyła tę listę komend \n $radio - kontroluje radio, aby uzyskać pomoc dotyczącą subkomend użyj $komendy radio \n $ping - sprawdź ping bota \n $czas - wyświetla aktualny czas \n $nie - NIE \n $tak - TAK \n $kostka - rzuć kostką```"
radio_komendy = u"```Komendy dotyczące sterowania radiem: \n $radio - kontroluje radio```"
admin_komendy = u"```Komendy dostępne dla administracji: \n $aresztuj - aresztuje użytkownika \n $przypomnij [przypomnienie] [czas] - przypomina wiadomość po ustalonym czasie \n $test_nicku - sprawdza nazwy użytkowników wszystkich użytkowników na serwerze i wysyła im wiadomość o zmianie```"
wybor_klasy = u"Witamy na szkolnym serwerze ZSPM! Podaj nam klasę, do której uczęszczasz: \n1ATPD\n1ATGPC\n1ATM\n1BTGPC\n1CTI"
ostrzezenie_autoryzacji = u"Próbowałeś, ale nie. Incydent zgłoszono. \n Chyba że naprawdę jesteś nauczycielem. Wtedy napisz do kogoś z administracji :)."
blad_klasy = u"Podaj klasę z listy!"
tak = (r"""```
        ,----,                     
      ,/   .`|                     
    ,`   .'  :                ,-.  
  ;    ;     /            ,--/ /|  
.'___,/    ,'           ,--. :/ |  
|    :     |            :  : ' /   
;    |.';  ;  ,--.--.   |  '  /    
`----'  |  | /       \  '  |  :    
    '   :  ;.--.  .-. | |  |   \   
    |   |  ' \__\/: . . '  : |. \  
    '   :  | ," .--.; | |  | ' \ \ 
    ;   |.' /  /  ,.  | '  : |--'  
    '---'  ;  :   .'   \;  |,'     
           |  ,     .-./'--'       
            `--`---'                                       
        ```""", r"""```
 /$$$$$$$$        /$$      
|__  $$__/       | $$      
   | $$  /$$$$$$ | $$   /$$
   | $$ |____  $$| $$  /$$/
   | $$  /$$$$$$$| $$$$$$/ 
   | $$ /$$__  $$| $$_  $$ 
   | $$|  $$$$$$$| $$ \  $$
   |__/ \_______/|__/  \__/              
        ```""", r"""```
  _______    _    
 |__   __|  | |   
    | | __ _| | __
    | |/ _` | |/ /
    | | (_| |   < 
    |_|\__,_|_|\_\
        ```""", r"""```
.------..------..------.
|T.--. ||A.--. ||K.--. |
| :/\: || (\/) || :/\: |
| (__) || :\/: || :\/: |
| '--'T|| '--'A|| '--'K|
`------'`------'`------'
        ```""", r"""```
ooooooooooooo           oooo        
8'   888   `8           `888        
     888       .oooo.    888  oooo  
     888      `P  )88b   888 .8P'   
     888       .oP"888   888888.    
     888      d8(  888   888 `88b.  
    o888o     `Y888""8o o888o o888o                 
        ```""", r"""```
▄▄▄█████▓ ▄▄▄       ██ ▄█▀
▓  ██▒ ▓▒▒████▄     ██▄█▒ 
▒ ▓██░ ▒░▒██  ▀█▄  ▓███▄░ 
░ ▓██▓ ░ ░██▄▄▄▄██ ▓██ █▄ 
  ▒██▒ ░  ▓█   ▓██▒▒██▒ █▄
  ▒ ░░    ▒▒   ▓▒█░▒ ▒▒ ▓▒
    ░      ▒   ▒▒ ░░ ░▒ ▒░
  ░        ░   ▒   ░ ░░ ░ 
               ░  ░░  ░   
        ```""", r"""```
 ____ ____ ____ 
||T |||a |||k ||
||__|||__|||__||
|/__\|/__\|/__\|
        ```""",)
nie = (r"""```
         ,--.                   
       ,--.'|   ,---,    ,---,. 
   ,--,:  : |,`--.' |  ,'  .' | 
,`--.'`|  ' :|   :  :,---.'   | 
|   :  :  | |:   |  '|   |   .' 
:   |   \ | :|   :  |:   :  |-, 
|   : '  '; |'   '  ;:   |  ;/| 
'   ' ;.    ;|   |  ||   :   .' 
|   | | \   |'   :  ;|   |  |-, 
'   : |  ; .'|   |  ''   :  ;/| 
|   | '`--'  '   :  ||   |    \ 
'   : |      ;   |.' |   :   .' 
;   |.'      '---'   |   | ,'   
'---'                `----'                                            
        ```""", r"""```
 /$$   /$$ /$$          
| $$$ | $$|__/          
| $$$$| $$ /$$  /$$$$$$ 
| $$ $$ $$| $$ /$$__  $$
| $$  $$$$| $$| $$$$$$$$
| $$\  $$$| $$| $$_____/
| $$ \  $$| $$|  $$$$$$$
|__/  \__/|__/ \_______/         
        ```""", r"""```
  _   _ _      
 | \ | (_) ___ 
 |  \| | |/ _ \
 | |\  | |  __/
 |_| \_|_|\___|
        ```""", r"""```
.------..------..------.
|N.--. ||I.--. ||E.--. |
| :(): || (\/) || (\/) |
| ()() || :\/: || :\/: |
| '--'N|| '--'I|| '--'E|
`------'`------'`------'
        ```""", r"""```
ooooo      ooo  o8o            
`888b.     `8'  `"'            
 8 `88b.    8  oooo   .ooooo.  
 8   `88b.  8  `888  d88' `88b 
 8     `88b.8   888  888ooo888 
 8       `888   888  888    .o 
o8o        `8  o888o `Y8bod8P'                                     
        ```""", r"""```
 ███▄    █  ██▓▓█████ 
 ██ ▀█   █ ▓██▒▓█   ▀ 
▓██  ▀█ ██▒▒██▒▒███   
▓██▒  ▐▌██▒░██░▒▓█  ▄ 
▒██░   ▓██░░██░░▒████▒
░ ▒░   ▒ ▒ ░▓  ░░ ▒░ ░
░ ░░   ░ ▒░ ▒ ░ ░ ░  ░
   ░   ░ ░  ▒ ░   ░   
         ░  ░     ░  ░
        ```""", r"""```
 ____ ____ ____ 
||N |||i |||e ||
||__|||__|||__||
|/__\|/__\|/__\|
        ```""",)

# Opcje youtube_dl
opcje_ytdl = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# Opcje ffmpeg
opcje_ffmpeg = {
    'options': '-vn'
}

# Skrócenie zmiennych
ytdl = youtube_dl.YoutubeDL(opcje_ytdl)

class YTDLSource(discord.PCMVolumeTransformer):
    """Ukradzione z wbudowanych przykładów discord.py"""

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **opcje_ffmpeg), data=data)

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        await ctx.send(wiadomosc_info)

    @commands.command()
    async def komendy(self, ctx, komenda="wszystkie"):
        if (komenda == "wszystkie"):
            await ctx.send('Wysłałem ci listę komend na PM')
            await ctx.author.send(lista_komend)
        elif (komenda == "radio"):
            await ctx.send('Pomoc dotyczącą radia wysłałem ci na PM')
            await ctx.author.send(radio_komendy)
        elif (komenda == "admin"):
            await ctx.send('Pomoc dotyczącą administrowania wysłałem ci na PM')
            await ctx.author.send(admin_komendy)
        else: # Aktualny Fallback, może byćz zmieniony później
            await ctx.send('Wysłałem ci listę komend na PM')
            await ctx.author.send(lista_komend)

class Muzyka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['dołącz'])
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Dołącza do kanału głosowego"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command(aliases=['graj', 'odtwórz'])
    async def play(self, ctx, *, url):
        """Odtwarza utwór z URLa"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(
                'Błąd odtwarzacza: %s' % e) if e else None)

        await ctx.send('Teraz leci: {}'.format(player.title))

    @commands.command(aliases=['transmituj'])
    async def stream(self, ctx, *, url):
        """Odtwarza na żywo z URLa"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(
                'Błąd odtwarzacza: %s' % e) if e else None)

        await ctx.send('Teraz leci: {}'.format(player.title))

    @commands.command(aliases=['głośność'])
    async def volume(self, ctx, volume: int):
        """Zmienia głośność odtwarzania"""

        if ctx.voice_client is None:
            return await ctx.send("Nie podłączono do żadnego kanału.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Zmieniono głośność na {}%".format(volume))

    @commands.command(aliases=['zatrzymaj'])
    async def stop(self, ctx):
        """Zatrzymuje bota i rozłącza go"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                # blad_dolaczania
                await ctx.send("Nie jesteś podłączony do żadnego kanału głosowego.")
                raise commands.CommandError(
                    "Autor wiadomości nie jest podpięty do serwera.")  # leave as is
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == bot.user:
            return
        else:
            print(f"[{datetime.datetime.now()}]  {ctx.author} napisał {ctx.content} na {ctx.channel}")

class Przydzielaczka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rola(self, ctx):
        await ctx.author.send(wybor_klasy)

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        await ctx.send(wybor_klasy)
        print(f"{ctx} dołączył(-a) na serwer.")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.guild is None:
            serwer = bot.get_guild(id_serwera)
            if str(ctx.content).lower() in wariacje_nauczycieli:
                await ctx.author.send(ostrzezenie_autoryzacji)
                print(f"{ctx.author} usiłował się zalogować jako nauczyciel")
            elif ctx.content.upper() == "1ATPD":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1ATPD"]), serwer.get_role(689119435151114345),))
                print(f"Przydzielono rolę 1ATPD dla {ctx.author}")
                await ctx.author.send(f"Przydzielono rolę 1ATPD dla {ctx.author}")
            elif ctx.content.upper() == "1ATGPC":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1ATGPC"]), serwer.get_role(689119435151114345),))
                print(f"Przydzielono rolę 1ATGPC dla {ctx.author}")
                await ctx.author.send(f"Przydzielono rolę 1ATGPC dla {ctx.author}")
            elif ctx.content.upper() == "1ATM":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1ATM"]), serwer.get_role(689119435151114345),))
                print(f"Przydzielono rolę 1ATM dla {ctx.author}")
                await ctx.author.send(f"Przydzielono rolę 1ATM dla {ctx.author}")
            elif ctx.content.upper() == "1BTGPC":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1BTGPC"]), serwer.get_role(689119435151114345),))
                print(f"Przydzielono rolę 1BTGPC dla {ctx.author}")
                await ctx.author.send(f"Przydzielono rolę 1BTGPC dla {ctx.author}")
            elif ctx.content.upper() == "1CTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1CTI"]), serwer.get_role(689119435151114345),))
                print(f"Przydzielono rolę 1CTI dla {ctx.author}")
                await ctx.author.send(f"Przydzielono rolę 1CTI dla {ctx.author}")
            else:
                try:                                    # TIL That Python doesn't have switch statement
                    await ctx.author.send(blad_klasy)   # Przepraszam, ale to jedyny sposób żeby nie wywalało błędu w konsoli
                except:                                 # Znaczy, jakimś cudem działa pomimo błędu
                    pass                                # Python jest dziwny.


class Policjant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot       

    @commands.command()
    @commands.has_any_role("Administracja")
    async def aresztuj(self, ctx, użytkownik):
        try:
            osoba = ctx.message.mentions[0]
            kanał = bot.get_channel(672189523471630337)
            try:
                await osoba.move_to(kanał)
            except:
                await ctx.send(f"{użytkownik} nie jest podłączony(-a) do kanału głosowego.")

            await ctx.send(f"Aresztowano {użytkownik}")
        except:
            await ctx.send(f"Nie udało się aresztować {użytkownik}")

    @commands.command()
    @commands.has_any_role("Administracja")
    async def przypomnij(self, ctx, czas, *, wiadomość):
        await ctx.send(f"Przypomnę ci \"{wiadomość}\" za {czas}s")
        await asyncio.sleep(int(czas))
        await ctx.author.send(f"Przypominam o {wiadomość}")

    @commands.command()
    @commands.has_any_role("Administracja")
    async def test_nicku(self, ctx):
        wzór = re.compile(r"[A-ZĄ-Ż]{1}[a-zą-ż]*\s[A-ZĄ-Ż]{1}[a-zą-ż]*(\-)?(?(1)[A-ZĄ-Ż]{1}[a-zą-ż]*)") # Wielka Litera, Małe Litery, Spacja, Wielka Litera, Małe litery, opcjonalnie Myślnik, Wielka Litera, Małe litery
        niepoprawni_użytkownicy = []
        sprawdzanie = "Sprawdzanie zgodności ze wzorem..."
        zmien_nick = "Zmień swój nick na **swoje** Imię i Nazwisko(Zaczynając od wielkich liter!)\nBrak zmiany oznacza wyrzucenie z serwera w związku z pogwałceniem 6 punktu regulaminu. Masz 12 godzin na reakcję."
        await ctx.send(sprawdzanie)
        try:
            for użytkownik in ctx.guild.members: 
                await asyncio.sleep(0.5)
                if str(użytkownik.nick) == "None":
                    nazwa = str(str(użytkownik)[:-5])
                    rezultat = re.match(wzór, nazwa)
                    if not rezultat:
                        try:
                            await użytkownik.send(zmien_nick)
                            print(f"Użytkownik {użytkownik} został powiadomiony o zmianie nicku")
                            niepoprawni_użytkownicy.append(str(użytkownik))
                        except:
                            print(f"Użytkownik {użytkownik} NIE został powiadomiony o zmianie nicku")
                else:    
                    rezultat = re.match(wzór, str(użytkownik.nick))
                    if not rezultat:
                        try:
                            await użytkownik.send(zmien_nick)
                            print(f"Użytkownik {użytkownik} został powiadomiony o zmianie nicku")
                            niepoprawni_użytkownicy.append(str(użytkownik))
                        except:
                            print(f"Użytkownik {użytkownik} NIE został powiadomiony o zmianie nicku")
            await ctx.send("Polecenie wykonano pomyślnie!")
            await ctx.send(f"Powiadomionych zostało {len(niepoprawni_użytkownicy)} użytkowników")
        except:
            await ctx.send("Wystąpił Krytyczny Błąd!")

    @commands.command(aliases=['wyrzuć_niewłaściwe_nicki'])
    @commands.has_any_role("Administracja")
    async def kick_invalid_nicknames(self, ctx):
        wzór = re.compile(r"[A-ZĄ-Ż]{1}[a-zą-ż]*\s[A-ZĄ-Ż]{1}[a-zą-ż]*(\-)?(?(1)[A-ZĄ-Ż]{1}[a-zą-ż]*)") # Wielka Litera, Małe Litery, Spacja, Wielka Litera, Małe litery, opcjonalnie Myślnik, Wielka Litera, Małe litery
        niepoprawni_użytkownicy = []
        sprawdzanie = "Sprawdzanie zgodności ze wzorem..."
        await ctx.send(sprawdzanie)
        try:
            for użytkownik in ctx.guild.members: 
                await asyncio.sleep(0.5)
                if str(użytkownik.nick) == "None":
                    nazwa = str(str(użytkownik)[:-5])
                    rezultat = re.match(wzór, nazwa)
                    if not rezultat:
                        try:
                            await bot.kick(użytkownik)
                            print(f"Użytkownik {użytkownik} został(-a) wyrzucony(-a) z serwera")
                            niepoprawni_użytkownicy.append(str(użytkownik))
                        except:
                            print(f"Użytkownik {użytkownik} NIE został(-a) wyrzucony(-a) z serwera")
                else:    
                    rezultat = re.match(wzór, str(użytkownik.nick))
                    if not rezultat:
                        try:
                            await bot.kick(użytkownik)
                            print(f"Użytkownik {użytkownik} został(-a) wyrzucony(-a) z serwera")
                            niepoprawni_użytkownicy.append(str(użytkownik))
                        except:
                            print(f"Użytkownik {użytkownik} NIE został(-a) wyrzucony(-a) z serwera")
            await ctx.send("Polecenie wykonano pomyślnie!")
            await ctx.send(f"Wyrzuconych zostało {len(niepoprawni_użytkownicy)} użytkowników")
        except:
            await ctx.send("Wystąpił Krytyczny Błąd!")
    
    @commands.command()
    @commands.has_any_role("Administracja")
    async def dm(self, ctx, wiadomość, *, cel):
        serwer = bot.get_guild(id_serwera)
        await serwer.get_member(int(cel.strip("<@!>"))).send(wiadomość)
        await ctx.send(f"Wysłano wiadomość do {cel}")
        print(f"Wysłano wiadomość do {cel}")

    @commands.command()
    @commands.has_any_role("Administracja")
    async def warn(self, ctx, cel, powód=""):
        ilość_ostrzeżeń=1
        serwer = bot.get_guild(id_serwera)
        await serwer.get_member(int(cel.strip("<@!>"))).send(f"Otrzymujesz ostrzeżenie za: {powód}. Ilość twoich ostrzeżeń to: **{ilość_ostrzeżeń}**")
        await ctx.send(f"Ostrzeżono {cel}")
        print(f"Ostrzeżono {cel}")
        
class Zabawa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def czas(self, ctx):
        await ctx.send(f"Aktualny czas to: {time.time()}s (od 1/1/1970)")

    @commands.command()
    async def tak(self, ctx):
        await ctx.send(tak[random.randint(0, len(tak)-1)])

    @commands.command()
    async def nie(self, ctx):
        await ctx.send(nie[random.randint(0, len(nie)-1)])
    
    @commands.command()
    async def kostka(self, ctx, params = 'd20', amount = 1,):
        for i in range(amount):
            regExp = re.compile(r"d([\d]*)(\+)?(?(2)([\d]*))")
            res = regExp.match(params)
            sides = int(res.group(1))
            modifier = int(res.group(3)) if str(res.group(3)).isnumeric() else 0
            await ctx.send(f"Losuje d{sides}+{modifier}: **{str(random.randint(1,sides)+modifier)}**")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {int(bot.latency*1000)}ms")

class Aktualizator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if str(ctx.author)=="GitHub#0000":
            if ctx.channel.id==694079178005282826:
                await subprocess.Popen(["sh", "./udpater.sh"])

bot = commands.Bot(command_prefix=commands.when_mentioned_or("$"), description=wiadomosc_info, help_command=None)

@bot.event
async def on_ready():
    print('Zalogowano jako {0} ({0.id})'.format(bot.user))
    print('-------------------------------------------------')

# Przełączanie funkcjonalności (Wykomentować niechciane linijki)
bot.add_cog(Info(bot))
bot.add_cog(Muzyka(bot))
bot.add_cog(Przydzielaczka(bot))
bot.add_cog(Logger(bot))
bot.add_cog(Policjant(bot))
bot.add_cog(Zabawa(bot))
bot.add_cog(Aktualizator(bot))

bot.run(token)