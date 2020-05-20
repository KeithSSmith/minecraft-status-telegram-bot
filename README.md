# Minecraft Status Telegram Bot

This is a bot designed to monitor the status of your Minecraft Server via a Docker container and send status updates via a Telegram Bot.

Example Usage:
```
docker build --tag minecraft-stats https://github.com/KeithSSmith/minecraft-status-telegram-bot.git

docker create \
  --name=minecraft-status \
  -e HOSTNAME=example.com \
  -e PORT=25565 \
  -e BOT_TOKEN=ABCD...1234 \
  -e SERVER_NAME='Minecraft Server' \
  --restart unless-stopped \
  minecraft-stats

docker start minecraft-status
```