from aiogram import Bot, Dispatcher, Router
from redis.asyncio import Redis
from bot_app.config import BOT_TOKEN

router = Router()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

redis = Redis(host="localhost", port=6379, decode_responses=True)
