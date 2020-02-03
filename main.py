import discord
import youtube_dl
import sys
import io
import os
import urllib
import credentials
import asyncio

token = credentials.getToken()

info_message = "```To jest bot przeznaczony dla Zespołu Szkół Poligraficzno-Mechanicznych im. Armii Krajowej w Katowicach. \n Aby uzyskać listę komend, wpisz $komendy \n Więcej info: https://github.com/VectorKappa/PoliBot```"
command_list = "```Lista komend bota: \n $komendy - wysyła tę listę komend \n $radio - kontroluje radio, aby uzyskać pomoc dotyczącą subkomend użyj $komendy radio \n ```"

class MyClient(discord.Client):
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
            await message.channel.send(info_message)
        if message.content.startswith('$komendy'):
            await message.channel.send('Wysłałem ci listę komend na PM')
            await message.author.send(command_list)
        for allowed_channel in message.guild.channels:
            if str(allowed_channel) == "muzyczna-zlota-rybka" or str(allowed_channel) == "zabawy-z-automatem" or str(allowed_channel) == "przelozeni-polibota":
                if message.content.startswith('$radio play'):
                    print("Stop")
                    thumbsup = '\N{THUMBS UP SIGN}'
                    thumbsdown = '\N{THUMBS DOWN SIGN}'
                    await message.add_reaction(thumbsup)
                    await message.add_reaction(thumbsdown)
        if message.content.startswith('$happyturzyn'):
            await message.channel.send("Happy turzyn:")
            await channel.send(file=discord.File('.\\images\\happyturzyn.png'))
        if message.content.startswith('$happyzuber'):
            await message.channel.send("Happy Zuber:")
            await channel.send(file=discord.File('.\\images\\zuber_approves.jpeg'), )
#if message.content.startswith('$radio'):
            #await message.channel.send('a')
client = MyClient()
client.run(token)
