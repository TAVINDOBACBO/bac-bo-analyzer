from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from collections import Counter
import os
import csv

ARQUIVO = "historico.csv"


def carregar_resultados():
    resultados = []
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            leitor = csv.DictReader(f)
            for linha in leitor:
                r = linha.get("resultado", "").upper().strip()
                if r in ["B", "P", "T"]:
                    resultados.append(r)
    return resultados


def salvar_resultado(resultado):
    existe = os.path.exists(ARQUIVO)

    with open(ARQUIVO, "a", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)

        if not existe:
            escritor.writerow(["resultado"])

        escritor.writerow([resultado])


def analisar():
    resultados = carregar_resultados()

    if not resultados:
        return "Ainda não tenho resultados para analisar."

    ultimos = resultados[-20:]
    contagem = Counter(ultimos)
    total = len(ultimos)

    prob_b = contagem.get("B", 0) / total * 100
    prob_p = contagem.get("P", 0) / total * 100
    prob_t = contagem.get("T", 0) / total * 100

    probs = {
        "B": prob_b,
        "P": prob_p,
        "T": prob_t
    }

    mais_provavel = max(probs, key=probs.get)

    return f"""
📊 Análise dos últimos {total} resultados:

🔴 B: {prob_b:.1f}%
🔵 P: {prob_p:.1f}%
🟡 T: {prob_t:.1f}%

➡️ Mais provável pelo histórico: {mais_provavel}

🧾 Últimos resultados:
{ultimos}

⚠️ Isso é análise estatística, não previsão garantida.
"""


def teclado():
    botoes = [
        [
            InlineKeyboardButton("🔴 B", callback_data="B"),
            InlineKeyboardButton("🔵 P", callback_data="P"),
            InlineKeyboardButton("🟡 T", callback_data="T"),
        ],
        [
            InlineKeyboardButton("📊 Analisar", callback_data="ANALISAR")
        ]
    ]

    return InlineKeyboardMarkup(botoes)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Clique no resultado que saiu:",
        reply_markup=teclado()
    )


async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    escolha = query.data

    if escolha in ["B", "P", "T"]:
        salvar_resultado(escolha)
        resposta = f"Resultado salvo: {escolha}\n\n" + analisar()

    elif escolha == "ANALISAR":
        resposta = analisar()

    else:
        resposta = "Opção inválida."

    await query.edit_message_text(
        resposta,
        reply_markup=teclado()
    )


async def analise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        analisar(),
        reply_markup=teclado()
    )


app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analise", analise))
app.add_handler(CallbackQueryHandler(botoes))

app.run_polling()
