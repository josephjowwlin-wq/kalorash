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
        await update.message.reply_text("📭 Дневник пуст. Напиши что-нибудь, например: завтрак (твои данные)")
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


if name == "__main__":
    main()
