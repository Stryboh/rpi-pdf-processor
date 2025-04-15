import credentials
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = credentials.token()

dp = Dispatcher()

async def process_pdf(filename):
    os.system(f"ocrmypdf -l rus  -f {filename} {filename}")
    return f"{filename}"

def ensure_tasks_dir():
    """Create tasks directory if it doesn't exist"""
    os.makedirs("tasks", exist_ok=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handle /start command"""
    await message.answer(f"Hello, {message.from_user.full_name}! Send me a pdf file to process.")

@dp.message(F.document)
async def file_handler(message: Message, bot: Bot) -> None:
    """Handle incoming documents"""
    ensure_tasks_dir()
    
    doc = message.document

    try:
        file = await bot.get_file(doc.file_id)
        original_path = os.path.join("tasks", doc.file_name)
        
        await bot.download_file(
            file_path=file.file_path,
            destination=original_path
        )
        
        name = await process_pdf(original_path)
        
        with open(f"{name}", "rb") as f:
            processed_file = f.read()
        
            await message.answer("Take that")
            await message.answer_document(
                BufferedInputFile(
                    processed_file,
                    filename=f"{original_path}"
                )
        os.remove(name)
            )
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await message.answer(f"❌ Error processing file: {e}")

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
