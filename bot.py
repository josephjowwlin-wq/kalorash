import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")

КАТЕГОРИИ = ["завтрак", "обед", "ужин", "перекус"]

# ---------------------------------------------------
# /start
# ---------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    приветствие = """
Привет! Я бот для подсчёта калорий.

📝 Как меня использовать:
  завтрак (твои данные)
  обед (твои данные)
  ужин (твои данные)
  перекус (твои данные)

⚙️ Настройки:
  /setnorm — установить дневную норму калорий
  /mynorm — посмотреть свою норму

📊 Команды:
  /total — посмотреть сумму за день
  /reset — очистить дневник
  /detail — показать все приёмы пищи
"""
    await update.message.reply_text(приветствие)


# ---------------------------------------------------
# /setnorm
# ---------------------------------------------------
async def setnorm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            норма = int(context.args[0])
            if норма <= 0:
                await update.message.reply_text("❌ Норма должна быть больше нуля.")
                return
            context.user_data["норма"] = норма
            await update.message.reply_text(f"✅ Дневная норма установлена: {норма} ккал")
            return
        except:
            pass

    context.user_data["ожидание_нормы"] = True
    await update.message.reply_text("📝 Введи число — твою дневную норму калорий:")


# ---------------------------------------------------
# /mynorm
# ---------------------------------------------------
async def mynorm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    норма = context.user_data.get("норма")
    if норма:
        await update.message.reply_text(f"🎯 Твоя дневная норма: {норма} ккал")
    else:
        await update.message.reply_text("⚠️ Норма не установлена. Установи командой /setnorm")


# ---------------------------------------------------
# Обработка сообщений
# ---------------------------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    текст = update.message.text.lower().strip()
    слова = текст.split()

    # Ждём ввода нормы
    if context.user_data.get("ожидание_нормы"):
        try:
            норма = int(слова[0])
            if норма <= 0:
                await update.message.reply_text("❌ Норма должна быть больше нуля. Попробуй ещё раз.")
                return
            context.user_data["норма"] = норма
            context.user_data["ожидание_нормы"] = False
            await update.message.reply_text(f"✅ Дневная норма установлена: {норма} ккал")
            return
        except:
            await update.message.reply_text("❌ Это не похоже на число. Введи число, например: 2500")
            return

    # Категории еды
    if len(слова) >= 2 and слова[0] in КАТЕГОРИИ:
        категория = слова[0]
        try:
            калории = int(слова[1])
        except:
            await update.message.reply_text("❌ Не понял число. Пример: завтрак (твои данные)")
            return

        if "дневник" not in context.user_data:
            context.user_data["дневник"] = {к: [] for к in КАТЕГОРИИ}

        context.user_data["дневник"][категория].append(калории)

        сумма_категории = sum(context.user_data["дневник"][категория])
        общая_сумма = sum(sum(v) for v in context.user_data["дневник"].values())

        эмодзи = {"завтрак": "🌅", "обед": "🍲", "ужин": "🌙", "перекус": "🍎"}

        ответ = (
            f"{эмодзи[категория]} {категория.upper()}: +{калории} ккал\n"
            f"📌 Всего за {категория}: {сумма_категории} ккал\n"
            f"📊 Общий калораж за день: {общая_сумма} ккал"
        )

        норма = context.user_data.get("норма")
        if норма:
            разница = норма - общая_сумма
            if разница > 0:
                ответ += f"\n🟢 Осталось добрать до нормы: {разница} ккал"
            elif разница < 0:
