import discord
import youtube_dl
import sys
import io
import os
import urllib
import credentials
import asyncio

token = credentials.getToken()

wiadomosc_info = "```To jest bot przeznaczony dla Zespołu Szkół Poligraficzno-Mechanicznych im. Armii Krajowej w Katowicach. \n Aby uzyskać listę komend, wpisz $komendy \n Więcej info: https://github.com/VectorKappa/PoliBot```"
lista_komend = "```Lista komend bota: \n $komendy - wysyła tę listę komend \n $radio - kontroluje radio, aby uzyskać pomoc dotyczącą subkomend użyj $komendy radio \n ```"

class klient(discord.Client):
    async def commands(self, author):
        pass
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
    async def on_message(self, message):
        print('Message from {0.author}: \"{0.content}\" on {0.channel}'.format(message))
        if message.author == self.user:
            return
        if message.content.startswith('$hello'):
            await message.channel.send('Hello World!')
        if message.content.startswith('$info'):
            await message.channel.send(wiadomosc_info)
        if message.content.startswith('$komendy'):
            await message.channel.send('Wysłałem ci listę komend na PM')
            await message.author.send(lista_komend)
        if message.content.startswith('$radio') and message.channel == "muzyczna-złota-rybka" or message.channel == "zabawy-z-automatem" or message.channel == "przełożeni-polibota":
            if message.content.startswith('$radio dodaj'):
                like = '\N{THUMBS UP SIGN}'
                dislike = '\N{THUMBS DOWN SIGN}'
                await message.add_reaction(like)
                await message.add_reaction(dislike)
        if message.content.startswith('$happyturzyn'):
            await message.channel.send("Happy turzyn:")
            await channel.send(file=discord.File('.\\images\\happyturzyn.png'))
        if message.content.startswith('$happyzuber'):
            await message.channel.send("Happy Zuber:")
            await message.channel.send(file=discord.File('.\\images\\zuber_approves.jpeg'), )
klient = klient()
klient.run(token)
