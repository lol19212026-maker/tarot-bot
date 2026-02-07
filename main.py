import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import google.generativeai as genai

# ==========================================
# ⚙️ НАСТРОЙКИ (ВСТАВЬ СВОИ КЛЮЧИ СЮДА)
# ==========================================
TELEGRAM_TOKEN = "8324870349:AAFckwMflhHN9HUtA2WZC2bNu-N_iSwICjQ"
GEMINI_API_KEY = "AIzaSyBFmnkCEsxCMfbvnI5Cfzbhf4_VfAWAMO4"

# Настройка модели
genai.configure(api_key=GEMINI_API_KEY)
# Используем flash, она самая быстрая и стабильная сейчас
model = genai.GenerativeModel('gemini-3-flash-preview')

# ==========================================
# 🃏 БАЗА ДАННЫХ КАРТ (WIKIMEDIA LINKS - Надежные)
# ==========================================
TAROT_DATA = {
    # --- СТАРШИЕ АРКАНЫ ---
    "Шут (The Fool)": "https://upload.wikimedia.org/wikipedia/commons/9/90/RWS_Tarot_00_Fool.jpg",
    "Маг (The Magician)": "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_01_Magician.jpg",
    "Жрица (The High Priestess)": "https://upload.wikimedia.org/wikipedia/commons/8/88/RWS_Tarot_02_High_Priestess.jpg",
    "Императрица (The Empress)": "https://upload.wikimedia.org/wikipedia/commons/d/d2/RWS_Tarot_03_Empress.jpg",
    "Император (The Emperor)": "https://upload.wikimedia.org/wikipedia/commons/c/c3/RWS_Tarot_04_Emperor.jpg",
    "Иерофант (The Hierophant)": "https://upload.wikimedia.org/wikipedia/commons/8/8d/RWS_Tarot_05_Hierophant.jpg",
    "Влюбленные (The Lovers)": "https://upload.wikimedia.org/wikipedia/commons/3/3a/TheLovers.jpg",
    "Колесница (The Chariot)": "https://upload.wikimedia.org/wikipedia/commons/9/9b/RWS_Tarot_07_Chariot.jpg",
    "Сила (Strength)": "https://upload.wikimedia.org/wikipedia/commons/f/f5/RWS_Tarot_08_Strength.jpg",
    "Отшельник (The Hermit)": "https://upload.wikimedia.org/wikipedia/commons/4/4d/RWS_Tarot_09_Hermit.jpg",
    "Колесо Фортуны (Wheel of Fortune)": "https://upload.wikimedia.org/wikipedia/commons/3/3c/RWS_Tarot_10_Wheel_of_Fortune.jpg",
    "Справедливость (Justice)": "https://upload.wikimedia.org/wikipedia/commons/e/e0/RWS_Tarot_11_Justice.jpg",
    "Повешенный (The Hanged Man)": "https://upload.wikimedia.org/wikipedia/commons/2/2b/RWS_Tarot_12_Hanged_Man.jpg",
    "Смерть (Death)": "https://upload.wikimedia.org/wikipedia/commons/d/d7/RWS_Tarot_13_Death.jpg",
    "Умеренность (Temperance)": "https://upload.wikimedia.org/wikipedia/commons/f/f8/RWS_Tarot_14_Temperance.jpg",
    "Дьявол (The Devil)": "https://upload.wikimedia.org/wikipedia/commons/5/55/RWS_Tarot_15_Devil.jpg",
    "Башня (The Tower)": "https://upload.wikimedia.org/wikipedia/commons/5/53/RWS_Tarot_16_Tower.jpg",
    "Звезда (The Star)": "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_17_Star.jpg",
    "Луна (The Moon)": "https://upload.wikimedia.org/wikipedia/commons/7/7f/RWS_Tarot_18_Moon.jpg",
    "Солнце (The Sun)": "https://upload.wikimedia.org/wikipedia/commons/1/17/RWS_Tarot_19_Sun.jpg",
    "Страшный суд (Judgement)": "https://upload.wikimedia.org/wikipedia/commons/d/dd/RWS_Tarot_20_Judgement.jpg",
    "Мир (The World)": "https://upload.wikimedia.org/wikipedia/commons/f/ff/RWS_Tarot_21_World.jpg",

    # --- ЖЕЗЛЫ ---
    "Туз Жезлов": "https://upload.wikimedia.org/wikipedia/commons/1/11/Wands01.jpg",
    "Двойка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Wands02.jpg",
    "Тройка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Wands03.jpg",
    "Четверка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Wands04.jpg",
    "Пятерка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/9/9d/Wands05.jpg",
    "Шестерка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Wands06.jpg",
    "Семерка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Wands07.jpg",
    "Восьмерка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Wands08.jpg",
    "Девятка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Tarot_Nine_of_Wands.jpg",
    "Десятка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Wands10.jpg",
    "Паж Жезлов": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Wands11.jpg",
    "Рыцарь Жезлов": "https://upload.wikimedia.org/wikipedia/commons/1/16/Wands12.jpg",
    "Королева Жезлов": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Wands13.jpg",
    "Король Жезлов": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Wands14.jpg",

    # --- КУБКИ ---
    "Туз Кубков": "https://upload.wikimedia.org/wikipedia/commons/3/36/Cups01.jpg",
    "Двойка Кубков": "https://upload.wikimedia.org/wikipedia/commons/f/f8/Cups02.jpg",
    "Тройка Кубков": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Cups03.jpg",
    "Четверка Кубков": "https://upload.wikimedia.org/wikipedia/commons/3/35/Cups04.jpg",
    "Пятерка Кубков": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Cups05.jpg",
    "Шестерка Кубков": "https://upload.wikimedia.org/wikipedia/commons/1/17/Cups06.jpg",
    "Семерка Кубков": "https://upload.wikimedia.org/wikipedia/commons/a/ae/Cups07.jpg",
    "Восьмерка Кубков": "https://upload.wikimedia.org/wikipedia/commons/6/60/Cups08.jpg",
    "Девятка Кубков": "https://upload.wikimedia.org/wikipedia/commons/2/24/Cups09.jpg",
    "Десятка Кубков": "https://upload.wikimedia.org/wikipedia/commons/8/84/Cups10.jpg",
    "Паж Кубков": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Cups11.jpg",
    "Рыцарь Кубков": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Cups12.jpg",
    "Королева Кубков": "https://upload.wikimedia.org/wikipedia/commons/6/61/Cups13.jpg",
    "Король Кубков": "https://upload.wikimedia.org/wikipedia/commons/0/04/Cups14.jpg",

    # --- МЕЧИ ---
    "Туз Мечей": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Swords01.jpg",
    "Двойка Мечей": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Swords02.jpg",
    "Тройка Мечей": "https://upload.wikimedia.org/wikipedia/commons/0/02/Swords03.jpg",
    "Четверка Мечей": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Swords04.jpg",
    "Пятерка Мечей": "https://upload.wikimedia.org/wikipedia/commons/2/23/Swords05.jpg",
    "Шестерка Мечей": "https://upload.wikimedia.org/wikipedia/commons/2/29/Swords06.jpg",
    "Семерка Мечей": "https://upload.wikimedia.org/wikipedia/commons/3/34/Swords07.jpg",
    "Восьмерка Мечей": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Swords08.jpg",
    "Девятка Мечей": "https://upload.wikimedia.org/wikipedia/commons/2/20/Swords09.jpg",
    "Десятка Мечей": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Swords10.jpg",
    "Паж Мечей": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Swords11.jpg",
    "Рыцарь Мечей": "https://upload.wikimedia.org/wikipedia/commons/b/b0/Swords12.jpg",
    "Королева Мечей": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Swords13.jpg",
    "Король Мечей": "https://upload.wikimedia.org/wikipedia/commons/3/33/Swords14.jpg",

    # --- ПЕНТАКЛИ ---
    "Туз Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/f/fd/Pents01.jpg",
    "Двойка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Pents02.jpg",
    "Тройка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/4/42/Pents03.jpg",
    "Четверка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/3/35/Pents04.jpg",
    "Пятерка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/9/96/Pents05.jpg",
    "Шестерка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Pents06.jpg",
    "Семерка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Pents07.jpg",
    "Восьмерка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/4/49/Pents08.jpg",
    "Девятка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Pents09.jpg",
    "Десятка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/4/42/Pents10.jpg",
    "Паж Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Pents11.jpg",
    "Рыцарь Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/c/c6/Pents12.jpg",
    "Королева Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/8/88/Pents13.jpg",
    "Король Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/1/1c/Pents14.jpg",
}

# ==========================================
# 📝 ПРОМПТЫ (ЛИЧНОСТЬ БОТА)
# ==========================================
PROMPTS = {
    "question": """
    Ты — профессиональный таролог.
    1. Тон: глубокий, эмпатичный, мистический.
    2. Используй HTML теги:
       - <b>Жирный текст</b> для заголовков.
       - <i>Курсив</i> для важных мыслей.
    3. Структура ответа:
       - <b>Анализ ситуации</b> (1-я карта)
       - <b>Что влияет / Препятствия</b> (2-я карта)
       - <b>Совет / Итог</b> (3-я карта)
    """,
    "day": """
    Ты даешь прогноз "Карта дня". 
    Одна карта. Опиши её значение в 3-4 предложениях.
    Дай совет на сегодня.
    Используй HTML теги <b> и <i>.
    """
}

# ==========================================
# 🕹️ КЛАВИАТУРЫ И СОСТОЯНИЯ
# ==========================================
def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🔮 Расклад на вопрос", callback_data="read_question")],
        [InlineKeyboardButton(text="✨ Карта дня (с фото)", callback_data="read_day"), 
         InlineKeyboardButton(text="❤️ Отношения", callback_data="read_love")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard():
    buttons = [[InlineKeyboardButton(text="🔙 В главное меню", callback_data="menu")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

class TarotState(StatesGroup):
    waiting_for_question = State()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ==========================================
# 🎲 ФУНКЦИЯ: ВЫТЯГИВАЕМ КАРТЫ
# ==========================================
def draw_cards(count=1):
    hand = []
    deck_names = list(TAROT_DATA.keys())
    chosen_names = random.sample(deck_names, count)
    
    for name in chosen_names:
        is_reversed = random.random() < 0.3
        position = " (Перевернутая) 🔄" if is_reversed else ""
        
        # Защита: если карты нет в словаре, берем Шута
        image_url = TAROT_DATA.get(name, TAROT_DATA["Шут (The Fool)"])
        
        hand.append({
            "name": name,
            "full_name": f"{name}{position}",
            "image": image_url
        })
    return hand

# ==========================================
# 📩 ОБРАБОТЧИКИ (ЛОГИКА БОТА)
# ==========================================

# 1. СТАРТ
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Приветствую! Я вижу больше, чем скрыто в тени.\n"
        "Выбери расклад прямо здесь:",
        reply_markup=get_main_keyboard()
    )

# 2. КНОПКА "МЕНЮ"
@dp.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try: await callback.message.delete()
    except: pass
    await callback.message.answer("👋 Выбери расклад:", reply_markup=get_main_keyboard())
    await callback.answer()

# 3. КНОПКА "КАРТА ДНЯ" (С КАРТИНКОЙ!)
@dp.callback_query(F.data == "read_day")
async def day_callback(callback: CallbackQuery):
    await callback.message.edit_text("🌙 <i>Достаю карту из колоды...</i>", parse_mode="HTML")
    
    cards = draw_cards(1)
    card_data = cards[0]
    
    await callback.message.delete()
    
    try:
        response = await model.generate_content_async(
            f"{PROMPTS['day']}\nВыпала карта: {card_data['full_name']}"
        )
        caption_text = f"🎴 <b>Твоя карта:</b> {card_data['full_name']}\n\n{response.text}"
        if len(caption_text) > 1000: caption_text = caption_text[:1000] + "..."

        # ПОПЫТКА ОТПРАВИТЬ ФОТО
        try:
            await callback.message.answer_photo(
                photo=card_data['image'],
                caption=caption_text,
                parse_mode="HTML",
                reply_markup=get_back_keyboard()
            )
        except Exception as img_error:
            # ЗАЩИТНЫЙ МЕХАНИЗМ: Если фото не грузится, шлем текст
            await callback.message.answer(
                f"[Картинка не загрузилась, но вот толкование]\n\n{caption_text}", 
                parse_mode="HTML",
                reply_markup=get_back_keyboard()
            )

    except Exception as e:
        await callback.message.answer(f"Ошибка магии: {e}", reply_markup=get_back_keyboard())
    
    await callback.answer()

# 4. ЗАПРОС ВОПРОСА
@dp.callback_query(F.data.in_({"read_question", "read_love"}))
async def ask_question_callback(callback: CallbackQuery, state: FSMContext):
    theme = "Отношения" if callback.data == "read_love" else "Общий вопрос"
    await state.update_data(theme=theme)
    await state.set_state(TarotState.waiting_for_question)
    
    await callback.message.edit_text(
        f"Тема: <b>{theme}</b>.\n\n"
        "🧘‍♂️ Сконцентрируйся и напиши свой вопрос в чат:",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# 5. ОБРАБОТКА ВОПРОСА (3 КАРТЫ)
@dp.message(TarotState.waiting_for_question)
async def process_tarot_question(message: types.Message, state: FSMContext):
    user_question = message.text
    data = await state.get_data()
    theme = data.get("theme")
    
    msg = await message.answer("🃏 <i>Тасую колоду...</i>", parse_mode="HTML")
    await asyncio.sleep(1)
    
    cards = draw_cards(3)
    
    # Текст для промпта
    cards_list_text = (
        f"1️⃣ {cards[0]['full_name']}\n"
        f"2️⃣ {cards[1]['full_name']}\n"
        f"3️⃣ {cards[2]['full_name']}"
    )
    
    await msg.edit_text(
        f"🎴 <b>Расклад:</b>\n{cards_list_text}\n\n🔮 <i>Глубокий анализ...</i>", 
        parse_mode="HTML"
    )

    context_prompt = PROMPTS['question']
    if theme == "Отношения":
        context_prompt += "\nФОКУС: Чувства, мысли партнера, перспектива союза."

    try:
        full_prompt = f"{context_prompt}\n\nВопрос пользователя: '{user_question}'\nВыпали карты: {cards_list_text}. Дай трактовку."
        response = await model.generate_content_async(full_prompt)
        
        # Тут мы пока отправляем просто текст (без 3 картинок, чтобы не спамить)
        # Но если захочешь картинки - они есть в cards[0]['image']
        await message.answer(response.text, parse_mode="HTML", reply_markup=get_back_keyboard())
        
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=get_back_keyboard())
    
    await state.clear()

# ==========================================
# 🚀 ЗАПУСК
# ==========================================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())