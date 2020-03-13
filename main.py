import asyncio
import discord
import youtube_dl
import credentials
from discord.ext import commands
# Wyciszenie błędów youtube_dl
youtube_dl.utils.bug_reports_message = lambda: ''
token = credentials.getToken()
# Komunikaty
lista_klas = ("1a Tpd/pi", "1a Tgpc", "1b Tgpc", "1cTi", "1d Ti", "1d Tm", "1eg Tgpc", "1fg Ti", "1fg Tm", "1gg Ti", "2a Tpd", "2a Tgpc",
              "2c Ti", "2d Ti", "2d Tm", "3a Tpd", "3a Tgpc", "3b Tgpc", "3c Ti", "3d Ti", "3d Tm", "4a Tpd", "4a Tm", "4b Tcpg", "4c Ti", "4d Ti")
wiadomosc_info = "To jest bot przeznaczony dla Zespołu Szkół Poligraficzno-Mechanicznych im. Armii Krajowej w Katowicach. \n Aby uzyskać listę komend, wpisz $komendy \n Więcej info: https://github.com/VectorKappa/PoliBot"
lista_komend = "```Lista komend bota: \n $komendy - wysyła tę listę komend \n $radio - kontroluje radio, aby uzyskać pomoc dotyczącą subkomend użyj $komendy radio \n ```"
wybor_klasy = "Witamy na szkolnym serwerze ZSPM! Podaj nam klasę, do której uczęszczasz: \n1ATPDPI\n1ATGPC\n1BTGPC\n1CTI\n1DTI\n1DTM\n1ETGPC\n1FTI\n1FTM\n1GTI\n2ATPD\n2ATGPC\n2CTI\n2DTI\n2DTM\n3ATPD\n3ATGPC\n3BTGPC\n3CTI\n3DTI\n3DTM\n4ATPD\n4ATM\n4BTCPG\n4CTI\n4DTI"
wariacje_nauczycieli = ("nauczyciel", "teacher")
ostrzezenie_autoryzacji = "Próbowałeś, ale nie. Incydent zgłoszono. \n Chyba że naprawdę jesteś nauczycielem. Wtedy napisz do kogoś z administracji."
blad_klasy = "Podaj klasę z listy!"
# Opcje youtube_dl
ytdl_format_options = {
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
#Opcje ffmpeg
ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


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
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


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

    async def ustaw_role(cel, rola):
        await guild.member(id=cel).add_roles(rola)

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        await ctx.send(wybor_klasy)
        print(f"{ctx} dołączył(-a) na serwer.")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.guild is None:
            if str(ctx.content).lower() in wariacje_nauczycieli:
                await ctx.author.send(ostrzezenie_autoryzacji)
                print(f"{ctx.author} usiłował się zalogować jako nauczyciel")
            elif ctx.content == "1ATPDPI":
                await ctx.guild.fetch_member(member_id=ctx.author.id).add_roles(687989513758572572)
            elif ctx.content == "1ATGPC":
                ustaw_role(ctx.author, "1ATGPC")
            elif ctx.content == "1BTGPC":
                ustaw_role(ctx.author, "1BTGPC")
            elif ctx.content == "1CTI":
                ustaw_role(ctx.author, "1CTI")
            elif ctx.content == "1DTI":
                ustaw_role(ctx.author, "1DTI")
            elif ctx.content == "1DTM":
                ustaw_role(ctx.author, "1DTM")
            elif ctx.content == "1ETGPC":
                ustaw_role(ctx.author, "1ETGPC")
            elif ctx.content == "1FTI":
                ustaw_role(ctx.author, "1FTI")
            elif ctx.content == "1FTM":
                ustaw_role(ctx.author, "1FTM")
            elif ctx.content == "1GTI":
                ustaw_role(ctx.author, "1GTI")
            elif ctx.content == "2ATPD":
                ustaw_role(ctx.author, "2ATPD")
            elif ctx.content == "2ATGPC":
                ustaw_role(ctx.author, "2ATGPC")
            elif ctx.content == "2CTI":
                ustaw_role(ctx.author, "2CTI")
            elif ctx.content == "2DTI":
                ustaw_role(ctx.author, "2DTI")
            elif ctx.content == "2DTM":
                ustaw_role(ctx.author, "2DTM")
            elif ctx.content == "3ATPD":
                ustaw_role(ctx.author, "3ATPD")
            elif ctx.content == "3ATGPC":
                ustaw_role(ctx.author, "3ATGPC")
            elif ctx.content == "3BTGPC":
                ustaw_role(ctx.author, "3BTGPC")
            elif ctx.content == "3CTI":
                ustaw_role(ctx.author, "3CTI")
            elif ctx.content == "3DTI":
                ustaw_role(ctx.author, "3DTI")
            elif ctx.content == "3DTM":
                ustaw_role(ctx.author, "3DTM")
            elif ctx.content == "4ATPD":
                ustaw_role(ctx.author, "4ATPD")
            elif ctx.content == "4ATM":
                ustaw_role(ctx.author, "4ATM")
            elif ctx.content == "4BTCPG":
                ustaw_role(ctx.author, "4BTCPG")
            elif ctx.content == "4CTI":
                ustaw_role(ctx.author, "4CTI")
            elif ctx.content == "4DTI":
                ustaw_role(ctx.author, "4DTI")
            else:
                await ctx.author.send(blad_klasy)


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

bot.run(token)
