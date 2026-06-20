import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")

КАТЕГОРИИ = ["завтрак", "обед", "ужин", "перекус"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для подсчёта калорий.\n\nИспользуй:\nзавтрак 300\n/setnorm 2500\n/total")

async def setnorm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            норма = int(context.args[0])
            if норма <= 0:
                await update.message.reply_text("Норма должна быть больше нуля.")
                return
            context.user_data["норма"] = норма
            await update.message.reply_text(f"✅ Норма: {норма} ккал")
        except:
            await update.message.reply_text("Введи число.")
    else:
        context.user_data["ожидание_нормы"] = True
        await update.message.reply_text("Введи дневную норму калорий:")

async def mynorm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    норма = context.user_data.get("норма")
    if норма:
        await update.message.reply_text(f"Твоя норма: {норма} ккал")
    else:
        await update.message.reply_text("Норма не задана. /setnorm")

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    дневник = context.user_data.get("дневник", {})
    if not дневник:
        await update.message.reply_text("Дневник пуст.")
        return
    общая = sum(sum(v) for v in дневник.values())
    await update.message.reply_text(f"Общий калораж: {общая} ккал")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["дневник"] = {"завтрак": [], "обед": [], "ужин": [], "перекус": []}
    await update.message.reply_text("Дневник очищен.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    текст = update.message.text.lower().strip()
    слова = текст.split()

    if context.user_data.get("ожидание_нормы"):
        try:
            норма = int(слова[0])
            if норма <= 0:
                await update.message.reply_text("Норма > 0.")
                return
            context.user_data["норма"] = норма
            context.user_data["ожидание_нормы"] = False
            await update.message.reply_text(f"✅ Норма: {норма} ккал")
        except:
            await update.message.reply_text("Это не число.")
        return

    if len(слова) >= 2 and слова[0] in КАТЕГОРИИ:
        категория = слова[0]
        try:
            калории = int(слова[1])
        except:
            await update.message.reply_text("Не понял число.")
            return
        
        if "дневник" not in context.user_data:
            context.user_data["дневник"] = {к: [] for к in КАТЕГОРИИ}
        
        context.user_data["дневник"][категория].append(калории)
        сумма_кат = sum(context.user_data["дневник"][категория])
        общая = sum(sum(v) for v in context.user_data["дневник"].values())
        
        ответ = f"{категория}: +{калории} ккал\nВсего за {категория}: {сумма_кат}\nОбщий итог: {общая}"
        норма = context.user_data.get("норма")
        if норма:
            разница = норма - общая
            if разница > 0: ответ += f"\n🟢 Осталось: {разница}"
            elif разница < 0: ответ += f"\n🔴 Лишнее: {abs(разница)}"
            else: ответ += "\n⚪ Норма!"
        await update.message.reply_text(ответ)
    else:
        await update.message.reply_text("Формат: завтрак 300")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setnorm", setnorm))
    app.add_handler(CommandHandler("mynorm", mynorm))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run_polling()

if __name__ == "__main__":
    main()
