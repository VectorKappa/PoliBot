import asyncio
import discord
import youtube_dl
import credentials
import re
from discord.ext import tasks, commands
import datetime
import time
import random

# Wyciszenie błędów youtube_dl
youtube_dl.utils.bug_reports_message = lambda: ''

# Import poufnych danych
token = credentials.getToken()
id_serwera = credentials.getServerId()
lista_roli = credentials.getRole()
blocklista = credentials.getBlocklist()

# Wariacje zmiennych
wariacje_nauczycieli = ("nauczyciel", "teacher", "maestro", "professeur", "lehrer", "nauczycielka", "lehrerin", "profesor", "profesorka")

# Komunikaty
wiadomosc_info = "To jest bot przeznaczony dla Zespołu Szkół Poligraficzno-Mechanicznych im. Armii Krajowej w Katowicach. \n Aby uzyskać listę komend, wpisz $komendy \n Więcej info: https://github.com/VectorKappa/PoliBot"
lista_komend = "```Lista komend bota: \n $komendy - wysyła tę listę komend \n $radio - kontroluje radio, aby uzyskać pomoc dotyczącą subkomend użyj $komendy radio \n $pierwsze-slowa - pierwsza wiadomość gracza na serwerze \n $ping - sprawdź ping bota \n $czas - wyświetla aktualny czas \n $spanko - mówi ci czy możesz spać czy nie \n $zgłos - zgłoś kogoś moderatorom za łamanie zasad \n $zasady - wyświetla zasady serwera \n $nie - NIE \n $tak - TAK \n $ip - sprawdź lokalizację i isp podanego adresu lub domeny \n $dox - znajdź kogoś adres ip \n $tn - tak lub nie \n $kostka - rzuć kostką \n $zainfekuj - zainfekuj kogoś Koronawirusem \n $zapytajboga - zapytaj \n $zabij - zabij kogoś \n $op - daj komuś opa \n $pobłogosław - pobłogosław kogoś. Jesteś dobrym człowiekiem.```"
wybor_klasy = "Witamy na szkolnym serwerze ZSPM! Podaj nam klasę, do której uczęszczasz: \n1ATPDPI\n1ATGPC\n1BTGPC\n1CTI\n1DTI\n1DTM\n1ETGPC\n1FTI\n1FTM\n1GTI\n2ATPD\n2ATGPC\n2CTI\n2DTI\n2DTM\n3ATPD\n3ATGPC\n3BTGPC\n3CTI\n3DTI\n3DTM\n4ATPD\n4ATM\n4BTCPG\n4CTI\n4DTI"
ostrzezenie_autoryzacji = "Próbowałeś, ale nie. Incydent zgłoszono. \n Chyba że naprawdę jesteś nauczycielem. Wtedy napisz do kogoś z administracji."
blad_klasy = "Podaj klasę z listy!"
tak = ("""```
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
        ```""", """```
 /$$$$$$$$        /$$      
|__  $$__/       | $$      
   | $$  /$$$$$$ | $$   /$$
   | $$ |____  $$| $$  /$$/
   | $$  /$$$$$$$| $$$$$$/ 
   | $$ /$$__  $$| $$_  $$ 
   | $$|  $$$$$$$| $$ \  $$
   |__/ \_______/|__/  \__/              
        ```""", """```
  _______    _    
 |__   __|  | |   
    | | __ _| | __
    | |/ _` | |/ /
    | | (_| |   < 
    |_|\__,_|_|\_\\
        ```""", """```
.------..------..------.
|T.--. ||A.--. ||K.--. |
| :/\: || (\/) || :/\: |
| (__) || :\/: || :\/: |
| '--'T|| '--'A|| '--'K|
`------'`------'`------'
        ```""", """```
ooooooooooooo           oooo        
8'   888   `8           `888        
     888       .oooo.    888  oooo  
     888      `P  )88b   888 .8P'   
     888       .oP"888   888888.    
     888      d8(  888   888 `88b.  
    o888o     `Y888""8o o888o o888o                 
        ```""", """```
▄▄▄█████▓ ▄▄▄       ██ ▄█▀
▓  ██▒ ▓▒▒████▄     ██▄█▒ 
▒ ▓██░ ▒░▒██  ▀█▄  ▓███▄░ 
░ ▓██▓ ░ ░██▄▄▄▄██ ▓██ █▄ 
  ▒██▒ ░  ▓█   ▓██▒▒██▒ █▄
  ▒ ░░    ▒▒   ▓▒█░▒ ▒▒ ▓▒
    ░      ▒   ▒▒ ░░ ░▒ ▒░
  ░        ░   ▒   ░ ░░ ░ 
               ░  ░░  ░   
        ```""", """```
 ____ ____ ____ 
||T |||a |||k ||
||__|||__|||__||
|/__\|/__\|/__\|
        ```""",)
nie = ("""```
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
        ```""", """```
 /$$   /$$ /$$          
| $$$ | $$|__/          
| $$$$| $$ /$$  /$$$$$$ 
| $$ $$ $$| $$ /$$__  $$
| $$  $$$$| $$| $$$$$$$$
| $$\  $$$| $$| $$_____/
| $$ \  $$| $$|  $$$$$$$
|__/  \__/|__/ \_______/         
        ```""", """```
  _   _ _      
 | \ | (_) ___ 
 |  \| | |/ _ \\
 | |\  | |  __/
 |_| \_|_|\___|
        ```""", """```
.------..------..------.
|N.--. ||I.--. ||E.--. |
| :(): || (\/) || (\/) |
| ()() || :\/: || :\/: |
| '--'N|| '--'I|| '--'E|
`------'`------'`------'
        ```""", """```
ooooo      ooo  o8o            
`888b.     `8'  `"'            
 8 `88b.    8  oooo   .ooooo.  
 8   `88b.  8  `888  d88' `88b 
 8     `88b.8   888  888ooo888 
 8       `888   888  888    .o 
o8o        `8  o888o `Y8bod8P'                                     
        ```""", """```
 ███▄    █  ██▓▓█████ 
 ██ ▀█   █ ▓██▒▓█   ▀ 
▓██  ▀█ ██▒▒██▒▒███   
▓██▒  ▐▌██▒░██░▒▓█  ▄ 
▒██░   ▓██░░██░░▒████▒
░ ▒░   ▒ ▒ ░▓  ░░ ▒░ ░
░ ░░   ░ ▒░ ▒ ░ ░ ░  ░
   ░   ░ ░  ▒ ░   ░   
         ░  ░     ░  ░
        ```""", """```
 ____ ____ ____ 
||N |||i |||e ||
||__|||__|||__||
|/__\|/__\|/__\|
        ```""",)

tn = ["Tak.", "Nie."]
god = ["Lepiej żebyś tego jeszcze nie wiedział", "To jest pewne, może?", "Nie mogę tego teraz przewidzieć", "Czemu miałbym ci mówić?"]
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
    # bind to ipv4 since ipv6 addresses cause issues sometimes
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
    async def komendy(self, ctx):
        await ctx.send('Wysłałem ci listę komend na PM')
        await ctx.author.send(lista_komend)

class Muzyka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Dołącza do kanału głosowego"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, url):
        """Odtwarza utwór z URLa"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(
                'Błąd odtwarzacza: %s' % e) if e else None)

        await ctx.send('Teraz leci: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Odtwarza na żywo z URLa"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(
                'Błąd odtwarzacza: %s' % e) if e else None)

        await ctx.send('Teraz leci: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Zmienia głośność odtwarzania"""

        if ctx.voice_client is None:
            return await ctx.send("Nie podłączono do żadnego kanału.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Zmieniono głośność na {}%".format(volume))

    @commands.command()
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
            if ctx.author.id not in blocklista:
                serwer = bot.get_guild(id_serwera)
                if str(ctx.content).lower() in wariacje_nauczycieli:
                    await ctx.author.send(ostrzezenie_autoryzacji)
                    print(f"{ctx.author} usiłował się zalogować jako nauczyciel")
                elif ctx.content.upper() == "1ATPDPI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1ATPDPI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1ATPDPI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1ATPDPI dla {ctx.author}")
                elif ctx.content.upper() == "1ATGPC":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1ATGPC"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1ATGPC dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1ATGPC dla {ctx.author}")
                elif ctx.content.upper() == "1BTGPC":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1BTGPC"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1BTGPC dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1BTGPC dla {ctx.author}")
                elif ctx.content.upper() == "1CTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1CTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1CTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1CTI dla {ctx.author}")
                elif ctx.content.upper() == "1DTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1DTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1DTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1DTI dla {ctx.author}")
                elif ctx.content.upper() == "1DTM":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1DTM"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1DTM dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1DTM dla {ctx.author}")
                elif ctx.content.upper() == "1ETGPC":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1ETGPC"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1ETGPC dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1ETGPC dla {ctx.author}")
                elif ctx.content.upper() == "1FTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1FTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1FTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1FTI dla {ctx.author}")
                elif ctx.content.upper() == "1FTM":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1FTM"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1FTM dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1FTM dla {ctx.author}")
                elif ctx.content.upper() == "1GTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1GTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 1GTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 1GTI dla {ctx.author}")
                elif ctx.content.upper() == "2ATPD":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2ATPD"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 2ATPD dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 2ATPD dla {ctx.author}")
                elif ctx.content.upper() == "2ATGPC":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2ATGPC"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 2ATGPC dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 2ATGPC dla {ctx.author}")
                elif ctx.content.upper() == "2CTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2CTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 2CTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 2CTI dla {ctx.author}")
                elif ctx.content.upper() == "2DTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2DTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 2DTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 2DTI dla {ctx.author}")
                elif ctx.content.upper() == "2DTM":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2DTM"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 2DTM dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 2DTM dla {ctx.author}")
                elif ctx.content.upper() == "3ATPD":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3ATPD"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 3ATPD dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 3ATPD dla {ctx.author}")
                elif ctx.content.upper() == "3ATGPC":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3ATGPC"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 3ATGPC dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 3ATGPC dla {ctx.author}")
                elif ctx.content.upper() == "3BTGPC":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3BTGPC"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 3BTGPC dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 3BTGPC dla {ctx.author}")
                elif ctx.content.upper() == "3CTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3CTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 3CTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 3CTI dla {ctx.author}")
                elif ctx.content.upper() == "3DTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3DTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 3DTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 3DTI dla {ctx.author}")
                elif ctx.content.upper() == "3DTM":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3DTM"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 3DTM dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 3DTM dla {ctx.author}")
                elif ctx.content.upper() == "4ATPD":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4ATPD"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 4ATPD dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 4ATPD dla {ctx.author}")
                elif ctx.content.upper() == "4ATM":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4ATM"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 4ATM dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 4ATM dla {ctx.author}")
                elif ctx.content.upper() == "4BTCPG":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4BTCPG"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 4BTCPG dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 4BTCPG dla {ctx.author}")
                elif ctx.content.upper() == "4CTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4CTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 4CTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 4CTI dla {ctx.author}")
                elif ctx.content.upper() == "4DTI":
                    await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4DTI"]), serwer.get_role(689119435151114345),))
                    print(f"Przydzielono rolę 4DTI dla {ctx.author}")
                    await ctx.author.send(f"Przydzielono rolę 4DTI dla {ctx.author}")
                else:
                    try:
                        await ctx.author.send(blad_klasy)   # Przepraszam, ale to jedyny sposób żeby nie wywalało błędu w konsoli
                    except:                                 # Znaczy, jakimś cudem działa pomimo błędu
                        pass                                # Python jest dziwny.
            else:
                pass
            

class Policjant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def aresztuj(self, ctx, użytkownik):
        await ctx.send(f"Aresztowano {użytkownik}")

    @commands.command()
    async def przypomnij(self, ctx, czas, *, wiadomość):
        await ctx.send(f"Przypomnę ci \"{wiadomość}\" za {czas}s")
        await asyncio.sleep(int(czas))
        await ctx.author.send(f"Przypominam o {wiadomość}")

class Zabawa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def czas(self, ctx):
        await ctx.send(f"Aktualny czas to: {time.time()}s (od 1/1/1970)")

    @commands.command()
    async def spanko(self, ctx):
        if datetime.datetime.now().hour >= 23 or datetime.datetime.now().hour <= 6:
            await ctx.send("Spać! A nie nocki jakieś :crescent_moon:")
        else:
            await ctx.send("Trza było spać w nocy :sunny:")

    @commands.command()
    async def zgłoś(self, ctx, uzytkownik):
        await ctx.send(f"{ctx.author.mention} zgłosił {uzytkownik} administracji. Miej się na baczności!")

    @commands.command()
    async def zainfekuj(self, ctx, uzytkownik):
        await ctx.send(f"{ctx.author.mention} zainfekował {uzytkownik} koronawirusem")

    @commands.command()
    async def tak(self, ctx):
        await ctx.send(tak[random.randint(0, len(tak)-1)])

    @commands.command()
    async def nie(self, ctx):
        await ctx.send(nie[random.randint(0, len(nie)-1)])
    
    @commands.command()
    async def tn(self, ctx):
        await ctx.send(tn[random.randint(0, 1)])

    @commands.command()
    async def dox(self, ctx, uzytkownik):
        await ctx.send(f"Adres IP {uzytkownik} to {random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}")

    @commands.command()
    async def kostka(self, ctx, ilosc_scianek = 6):
        await ctx.send(str(random.randint(1, ilosc_scianek)))
    
    @commands.command()
    async def op(self, ctx, uzytkownik):
        await ctx.send(f"{uzytkownik} otrzymał uprawnienia Administratora.")

    @commands.command()
    async def pobłogosław(self, ctx, uzytkownik):
        await ctx.send(f"{ctx.author.mention} pobłogosławił {uzytkownik}. Ale dobra osoba.") 

    @commands.command()
    async def zapytajboga(self, ctx):
        await ctx.send(god[random.randint(0, len(god)-1)]) 
    
    @commands.command()
    async def zabij(self, ctx, uzytkownik):
        await ctx.send(f"{ctx.author.mention} zabił {uzytkownik}") 

    # TO DO
    # $pierwsze-slowa - pierwsza wiadomość gracza na serwerze
    # $ping - sprawdź ping bota
    # $ip - sprawdź lokalizację i isp podanego adresu lub domeny
bot = commands.Bot(command_prefix=commands.when_mentioned_or("$"),
                   description=wiadomosc_info, help_command=None)

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

bot.run(token)

# Spis wszystkich komend na serwerze.
# $komendy - wysyła tę listę komend
# $radio - kontroluje radio, aby uzyskać pomoc dotyczącą subkomend użyj $komendy radio
# $pierwsze-slowa - pierwsza wiadomość gracza na serwerze
# $ping - sprawdź ping bota
# $czas - wyświetla aktualny czas
# $spanko - mówi ci czy możesz spać czy nie
# $zgłos - zgłoś kogoś moderatorom za łamanie zasad
# $nie - NIE
# $tak - TAK
# $ip - sprawdź lokalizację i isp podanego adresu lub domeny
# $dox - znajdź kogoś adres ip
# $tn - tak lub nie
# $kostka - rzuć kostką
# $zainfekuj - zainfekuj kogoś Koronawirusem
# $zapytajboga - zapytaj
# $zabij - zabij kogoś
# $op - daj komuś opa
# $pobłogosław - pobłogosław kogoś. Jesteś dobrym człowiekiem.