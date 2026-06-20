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
            await update.message.reply_text("❌ Не понял число. Пример: завтрак 300")
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
                ответ += f"\n🔴 Превышение нормы на: {abs(разница)} ккал!"
            else:
                ответ += f"\n⚪ Ты точно в норме! {норма} ккал."

        await update.message.reply_text(ответ)

    else:
        await update.message.reply_text(
            "❌ Не понял. Пиши так:\n"
            "завтрак (твои данные)\nобед (твои данные)\nужин (твои данные)\nперекус (твои данные)"
        )


# ---------------------------------------------------
# /total
# ---------------------------------------------------
async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    дневник = context.user_data.get("дневник", {})

    if not дневник:
        await update.message.reply_text("📭 Дневник пуст. Напиши что-нибудь, например: завтрак 300")
        return

    общая = sum(sum(v) for v in дневник.values())
    ответ = f"📊 Общий калораж за день: {общая} ккал"

    норма = context.user_data.get("норма")
    if норма:
        разница = норма - общая
        if разница > 0:
            ответ += f"\n🟢 Осталось добрать: {разница} ккал"
        elif разница < 0:
            ответ += f"\n🔴 Превышение на: {abs(разница)} ккал!"
        else:
            ответ += f"\n⚪ Точно в норме!"

    await update.message.reply_text(ответ)


# ---------------------------------------------------
# /detail
# ---------------------------------------------------
async def detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    дневник = context.user_data.get("дневник", {})

    if not дневник:
        await update.message.reply_text("📭 Дневник пуст.")
        return

    эмодзи = {"завтрак": "🌅", "обед": "🍲", "ужин": "🌙", "перекус": "🍎"}

    ответ = "📋 Твой дневник за сегодня:\n\n"
    общая = 0

    for категория, список_ккал in дневник.items():
        if список_ккал:
            сумма = sum(список_ккал)
            общая += сумма
            блюда = " + ".join(str(x) for x in список_ккал)
            ответ += f"{эмодзи[категория]} {категория.upper()}: {блюда} = {сумма} ккал\n"

    ответ += f"\n📊 Общий итог: {общая} ккал"

    норма = context.user_data.get("норма")
    if норма:
        разница = норма - общая
        if разница > 0:
            ответ += f"\n🟢 Осталось добрать: {разница} ккал"
        elif разница < 0:
            ответ += f"\n🔴 Превышение на: {abs(разница)} ккал!"
        else:
            ответ += f"\n⚪ Точно в норме!"

    await update.message.reply_text(ответ)


# ---------------------------------------------------
# /reset
# ---------------------------------------------------
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["дневник"] = {к: [] for к in КАТЕГОРИИ}
    await update.message.reply_text("🔄 Дневник очищен. Начинаем новый день!")


# ---------------------------------------------------
# Запуск
# ---------------------------------------------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setnorm", setnorm))
    app.add_handler(CommandHandler("mynorm", mynorm))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("detail", detail))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен!")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run_polling()


if __name__ == "__main__":
    main()
