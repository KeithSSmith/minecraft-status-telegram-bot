import argparse
from datetime import timedelta
import logging
import minecraft_status
from telegram.ext import Updater, CommandHandler


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class MinecraftStatusTelegramBot(object):
    
    def __init__(self, host='localhost', port=25565, server_name='Minecraft Server'):
        self.minestats = minecraft_status.MinecraftStatus(host=host, port=int(port))
        self.server_name = server_name
        self.downs = 0
        self.player_count = 0
        self.previous_player_count = 0
        self.previous_player_list = []


    def simple_server_check(self):
        self.minestats.get_status()
        if self.minestats.online:
            self.downs = 0
            self.player_count = self.minestats.current_player_count
            self.previous_player_list = self.minestats.current_player_list
            return "✅✅✅ {} is Online ✅✅✅".format(self.server_name)
        else:
            self.downs += 1
            return "🛑🛑🛑 {} is DOWN 🛑🛑🛑".format(self.server_name)


    def server_check(self, context):
        self.minestats.get_status()
        job = context.job
        if self.minestats.online:
            if self.downs > 0:
                context.bot.send_message(
                    job.context,
                    text="✅✅✅ {} is Online ✅✅✅".format(self.server_name)
                )
            self.downs = 0
            self.player_count = self.minestats.current_player_count
            if self.player_count != self.previous_player_count:
                for player in self.minestats.current_player_list:
                    if player not in self.previous_player_list:
                        context.bot.send_message(
                            job.context,
                            text='🎉 ' + player + ' joined the server'
                        )
                for player in self.previous_player_list:
                    if player not in self.minestats.current_player_list:
                        context.bot.send_message(
                            job.context,
                            text='🚪 ' + player + ' left the server'
                        )
            self.previous_player_count = self.minestats.current_player_count
            self.previous_player_list = self.minestats.current_player_list
        else:
            self.downs += 1
            if self.downs % 10 == 1:
                context.bot.send_message(
                    job.context,
                    text="🛑🛑🛑 {} is DOWN  🛑🛑🛑".format(self.server_name)
                )


    def help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text(
            "Use /start to initiate server monitoring.\n"
            + "Use /player_list to view players currently on the server."
        )


    def start(self, update, context):
        context.job_queue.run_repeating(
            callback=self.server_check,
            interval=timedelta(minutes=1),
            first=1,
            context=update.message.chat_id,
        )


    def player_list(self, update, context):
        """Send a message when the command /player_list is issued."""
        self.minestats.get_status()
        if self.minestats.current_player_count > 0:
            text = "Current Players on the Server:\n"
            for player in self.minestats.current_player_list:
                text += player + "\n"
        else:
            text = "No Players Currently Logged On"
        update.message.reply_text(text)


def main(args):
    mc_status_bot = MinecraftStatusTelegramBot(host=args.server, port=args.port, server_name=args.server_name)
    mc_status_bot.simple_server_check()
    bot_token = args.token
    
    # Send an initial message to a specific Chat ID
    # bot_chat_id = ""
    # send_text = 'https://api.telegram.org/bot' + bot_token + \
    #             '/sendMessage?chat_id=' + str(bot_chat_id) + \
    #             '&parse_mode=Markdown&text=' + simple_server_check()
    # response = requests.get(send_text)
    # logger.info(response.json())

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        token=bot_token,
        use_context=True
    )

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", mc_status_bot.help))
    dp.add_handler(CommandHandler("start", mc_status_bot.start))
    dp.add_handler(CommandHandler("player_list", mc_status_bot.player_list))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", help="Minecraft Servers Hostname or IP", required=True)
    parser.add_argument("-p", "--port", help="Minecraft Servers Port", required=True)
    parser.add_argument("-t", "--token", help="Telegram Bot Token", required=True)
    parser.add_argument("-n", "--server_name", help="Minecraft Server Name", required=True)
    args = parser.parse_args()
    main(args)
