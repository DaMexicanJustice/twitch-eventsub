import os
from dotenv import load_dotenv
from twitchio.ext import commands

# Load environment variables from .env
load_dotenv()

# Configuration
CHANNEL = 'DaMexicanJustice'
TOKEN = os.getenv('bot_oauth_token')
CLIENT_ID = os.getenv('bot_client_id')
CLIENT_SECRET = os.getenv('bot_client_secret')
BOT_USER_ID = os.getenv('bot_user_id')

class TwitchBot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=BOT_USER_ID,
            prefix='!',
            initial_channels=[CHANNEL]
        )

    async def event_ready(self):
        print('✅ Bot is ready and connected')

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    @commands.command(name='hi')
    async def greet(self, ctx):
        await ctx.send(f'👋 Hello {ctx.author.name}, welcome to #{CHANNEL}!')

    async def send_custom_message(self, message):
        chan = self.get_channel(CHANNEL)
        if chan:
            await chan.send(message)

if __name__ == '__main__':
    bot = TwitchBot()
    bot.run()