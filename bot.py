from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from collections import Counter
import os

resultados = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Envie B, P ou T para eu analisar os padrões."
    )

async def receber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.upper().strip()

    if texto not in ["B", "P", "T"]:
        await update.message.reply_text("Envie apenas B, P ou T.")
        return

    resultados.append(texto)
    ultimos = resultados[-20:]
    contagem = Counter(ultimos)
    total = len(ultimos)

    probs = {
        "B": contagem.get("B", 0) / total * 100,
        "P": contagem.get("P", 0) / total * 100,
        "T": contagem.get("T", 0) / total * 100
    }

    mais = max(probs, key=probs.get)

    resposta = f"""
📊 Últimos {total}: {ultimos}

🔴 B: {probs['B']:.1f}%
🔵 P: {probs['P']:.1f}%
🟡 T: {probs['T']:.1f}%

➡️ Mais forte pelo histórico: {mais}
⚠️ Análise estatística, não previsão garantida.
"""

    await update.message.reply_text(resposta)

app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber))

app.run_polling()
