import os
import asyncio
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from twitchio.ext import commands
from sqlalchemy import create_engine, Column, String, Integer, DateTime, select
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, UTC
from sqlalchemy import func

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

# MateriaInventory table with timestamp
class MateriaInventory(Base):
    __tablename__ = 'inventory'
    user_name = Column(String, primary_key=True)
    materia_name = Column(String, primary_key=True)
    count = Column(Integer, default=1)
    redeemed_at = Column(DateTime(timezone=True), server_default=func.now())

Base.metadata.create_all(engine)

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
        asyncio.create_task(self.poll_recent_redemptions())

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    @commands.command(name='hi')
    async def greet(self, ctx):
        await ctx.send(f'👋 Hello {ctx.author.name}, welcome to #{CHANNEL}!')

    from datetime import datetime, timedelta, timezone

    async def poll_recent_redemptions(self):
        cooldown_window = timedelta(minutes=10)
        announced = {}  # Track last announced timestamps by key

        while True:
            try:
                session = Session()
                cutoff = datetime.now(timezone.utc) - cooldown_window

                result = session.execute(
                    select(MateriaInventory).where(MateriaInventory.redeemed_at >= cutoff)
                ).scalars().all()

                for entry in result:
                    key = (entry.user_name, entry.materia_name)
                    redeemed_time = entry.redeemed_at.replace(tzinfo=timezone.utc)

                    # Announce only if never announced OR timestamp is newer
                    last_announced = announced.get(key)
                    if not last_announced or redeemed_time > last_announced:
                        msg = f"🎁 @{entry.user_name} received {entry.materia_name} — now owns x{entry.count}!"
                        await self.send_custom_message(msg)
                        announced[key] = redeemed_time
                        print(f"✅ Announced: {msg}")

                session.close()
            except Exception as e:
                print(f"❌ Error polling: {e}")

            await asyncio.sleep(10)

    async def send_custom_message(self, message):
        if self.connected_channels:
            await self.connected_channels[0].send(message)

def run():
    bot = TwitchBot()
    bot.run()

if __name__ == '__main__':
    run()