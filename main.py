import asyncio
import discord
import youtube_dl
import credentials
import datetime
import time
from discord.ext import commands

# Wyciszenie błędów youtube_dl
youtube_dl.utils.bug_reports_message = lambda: ''

# Import poufnych danych
token = credentials.getToken()
id_serwera = credentials.getServerId()
lista_roli = credentials.getRole()

# Wariacje zmiennych
wariacje_nauczycieli = ("nauczyciel", "teacher", "maestro", "professeur", "lehrer", "nauczycielka", "lehrerin", "profesor", "profesorka")

# Komunikaty
wiadomosc_info = "To jest bot przeznaczony dla Zespołu Szkół Poligraficzno-Mechanicznych im. Armii Krajowej w Katowicach. \n Aby uzyskać listę komend, wpisz $komendy \n Więcej info: https://github.com/VectorKappa/PoliBot"
lista_komend = "```Lista komend bota: \n $komendy - wysyła tę listę komend \n $radio - kontroluje radio, aby uzyskać pomoc dotyczącą subkomend użyj $komendy radio \n $pierwsze-slowa - pierwsza wiadomość gracza na serwerze \n $ping - sprawdź ping bota \n $czas - wyświetla aktualny czas \n $spanko - mówi ci czy możesz spać czy nie \n $zglos - zgłoś kogoś moderatorom za łamanie zasad \n $zasady - wyświetla zasady serwera \n $nie - NIE \n $tak - TAK \n $ip - sprawdź lokalizację i isp podanego adresu lub domeny \n $dox - znajdź kogoś adres ip \n $t/n - tak lub nie \n $kostka - rzuć kostką \n $zainfekuj - zainfekuj kogoś Koronawirusem \n $zapytajboga / $zapytajallaha - zapytaj \n $zabij - zabij kogoś \n $op - daj komuś opa \n $pobłogosław - pobłogosław kogoś. Jesteś dobrym człowiekiem.```"
wybor_klasy = "Witamy na szkolnym serwerze ZSPM! Podaj nam klasę, do której uczęszczasz: \n1ATPDPI\n1ATGPC\n1BTGPC\n1CTI\n1DTI\n1DTM\n1ETGPC\n1FTI\n1FTM\n1GTI\n2ATPD\n2ATGPC\n2CTI\n2DTI\n2DTM\n3ATPD\n3ATGPC\n3BTGPC\n3CTI\n3DTI\n3DTM\n4ATPD\n4ATM\n4BTCPG\n4CTI\n4DTI"
ostrzezenie_autoryzacji = "Próbowałeś, ale nie. Incydent zgłoszono. \n Chyba że naprawdę jesteś nauczycielem. Wtedy napisz do kogoś z administracji."
blad_klasy = "Podaj klasę z listy!"

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
            print(f"{ctx.author} napisał {ctx.content} na {ctx.channel}")

class Przydzielaczka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            elif ctx.content == "1ATPDPI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1ATPDPI"]),))
                print(f"Przydzielono rolę 1ATPDPI dla {ctx.author}")
            elif ctx.content == "1ATGPC":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1ATGPC"]),))
                print(f"Przydzielono rolę 1ATGPC dla {ctx.author}")
            elif ctx.content == "1BTGPC":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1BTGPC"]),))
                print(f"Przydzielono rolę 1BTGPC dla {ctx.author}")
            elif ctx.content == "1CTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1CTI"]),))
                print(f"Przydzielono rolę 1CTI dla {ctx.author}")
            elif ctx.content == "1DTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1DTI"]),))
                print(f"Przydzielono rolę 1DTI dla {ctx.author}")
            elif ctx.content == "1DTM":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1DTM"]),))
                print(f"Przydzielono rolę 1DTM dla {ctx.author}")
            elif ctx.content == "1ETGPC":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1ETGPC"]),))
                print(f"Przydzielono rolę 1ETGPC dla {ctx.author}")
            elif ctx.content == "1FTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1FTI"]),))
                print(f"Przydzielono rolę 1FTI dla {ctx.author}")
            elif ctx.content == "1FTM":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1FTM"]),))
                print(f"Przydzielono rolę 1FTM dla {ctx.author}")
            elif ctx.content == "1GTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["1GTI"]),))
                print(f"Przydzielono rolę 1GTI dla {ctx.author}")
            elif ctx.content == "2ATPD":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2ATPD"]),))
                print(f"Przydzielono rolę 2ATPD dla {ctx.author}")
            elif ctx.content == "2ATGPC":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2ATGPC"]),))
                print(f"Przydzielono rolę 2ATGPC dla {ctx.author}")
            elif ctx.content == "2CTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2CTI"]),))
                print(f"Przydzielono rolę 2CTI dla {ctx.author}")
            elif ctx.content == "2DTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2DTI"]),))
                print(f"Przydzielono rolę 2DTI dla {ctx.author}")
            elif ctx.content == "2DTM":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["2DTM"]),))
                print(f"Przydzielono rolę 2DTM dla {ctx.author}")
            elif ctx.content == "3ATPD":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3ATPD"]),))
                print(f"Przydzielono rolę 3ATPD dla {ctx.author}")
            elif ctx.content == "3ATGPC":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3ATGPC"]),))
                print(f"Przydzielono rolę 3ATGPC dla {ctx.author}")
            elif ctx.content == "3BTGPC":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3BTGPC"]),))
                print(f"Przydzielono rolę 3BTGPC dla {ctx.author}")
            elif ctx.content == "3CTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3CTI"]),))
                print(f"Przydzielono rolę 3CTI dla {ctx.author}")
            elif ctx.content == "3DTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3DTI"]),))
                print(f"Przydzielono rolę 3DTI dla {ctx.author}")
            elif ctx.content == "3DTM":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["3DTM"]),))
                print(f"Przydzielono rolę 3DTM dla {ctx.author}")
            elif ctx.content == "4ATPD":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4ATPD"]),))
                print(f"Przydzielono rolę 4ATPD dla {ctx.author}")
            elif ctx.content == "4ATM":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4ATM"]),))
                print(f"Przydzielono rolę 4ATM dla {ctx.author}")
            elif ctx.content == "4BTCPG":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4BTCPG"]),))
                print(f"Przydzielono rolę 4BTCPG dla {ctx.author}")
            elif ctx.content == "4CTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4CTI"]),))
                print(f"Przydzielono rolę 4CTI dla {ctx.author}")
            elif ctx.content == "4DTI":
                await serwer.get_member(ctx.author.id).edit(roles=(serwer.get_role(lista_roli["4DTI"]),))
                print(f"Przydzielono rolę 4DTI dla {ctx.author}")
            else:
                try:
                    await ctx.author.send(blad_klasy)   # Przepraszam, ale to jedyny sposób żeby nie wywalało błędu w konsoli
                except:                                 # Znaczy, jakimś cudem działa pomimo błędu
                    pass                                # Python jest dziwny.

class Policjant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def aresztuj(self, ctx, member):
        await ctx.send(f"Aresztowano {ctx.member}")

class Zabawa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def czas(self, ctx):
        await ctx.send(f"Aktualny czas to: {time.mktime(datetime.datetime.now().timetuple())}")

    @commands.command()
    async def zainfekuj(self, ctx, member):
        await ctx.send(f"{ctx.author} zainfekował {ctx.member} Koronawirusem")

    # $firstwords - First message the bot has saved from player
    # $ping - Get ping of yourself or someone else.
    # $sleep - Tells you if you can sleep or not
    # $report - Report someone to server moderators for breaking the rules.
    # $rules - Rules of the server
    # $no - NO
    # $yes - YES
    # $ip - find location and isp of an ip or domain.
    # $dox - find someones ip
    # $nwordcount - !nwordcount PLAYER - check how many nwords the player has said. Added for black history month.
    # $y/n - Yes or no
    # $dice - Roll a die
    # $askgod / !askallah / !askrusher - ask
    # $kill - kill someone
    # $op - Op yourself or someone else
    # $bless - bless someone. You are a good person.

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
# bot.add_cog(Policjant(bot))
bot.add_cog(Zabawa(bot))

bot.run(token)
