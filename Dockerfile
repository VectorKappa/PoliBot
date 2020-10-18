FROM gorialis/discord.py:3.9.0rc1-alpine-master-minimal
WORKDIR /PoliBot
COPY . .
RUN pip install youtube-dl asyncio discord.py urllib3
RUN git pull
CMD [ "python", "main.py" ]