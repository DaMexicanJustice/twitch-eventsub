import os
import asyncio
from dotenv import load_dotenv
from twitchio.ext import commands
from sqlalchemy import create_engine, Column, String, Integer, select
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Load .env config
load_dotenv()

# Twitch config
CHANNEL = 'DaMexicanJustice'
TOKEN = os.getenv('bot_oauth_token')
CLIENT_ID = os.getenv('bot_client_id')
CLIENT_SECRET = os.getenv('bot_client_secret')
BOT_USER_ID = os.getenv('bot_user_id')

# DB config
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# MateriaInventory table
class MateriaInventory(Base):
    __tablename__ = 'inventory'
    user_name = Column(String, primary_key=True)
    materia_name = Column(String, primary_key=True)
    count = Column(Integer, default=1)

Base.metadata.create_all(engine)

# 🔄 Track which entries have already been announced
announced = set()

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
        asyncio.create_task(self.poll_redemptions())

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    @commands.command(name='hi')
    async def greet(self, ctx):
        await ctx.send(f'👋 Hello {ctx.author.name}, welcome to #{CHANNEL}!')

    async def poll_redemptions(self):
        while True:
            try:
                session = Session()
                result = session.execute(select(MateriaInventory)).scalars().all()
                for entry in result:
                    key = (entry.user_name, entry.materia_name, entry.count)
                    if key not in announced:
                        msg = f"🎁 @{entry.user_name} received {entry.materia_name} — now owns x{entry.count}!"
                        await self.send_custom_message(msg)
                        announced.add(key)
                session.close()
            except Exception as e:
                print(f"❌ Error polling: {e}")
            await asyncio.sleep(10)  # Poll every 10 seconds

    async def send_custom_message(self, message):
        chan = self.get_channel(CHANNEL)
        if chan:
            await chan.send(message)

def run():
    bot = TwitchBot()
    bot.run()

if __name__ == '__main__':
    run()