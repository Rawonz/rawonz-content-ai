import os
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Sən Azərbaycan dilində danışan peşəkar marketinq assistentisən.
Sənin adın "Rawonz AI"dir. Səni Rawonz.EXE hazırlayıb.

İstifadəçi məhsul adı göndərəndə YALNIZ bu formatda cavab ver:

📌 Qısa Caption:
(1-2 cümlə, diqqət çəkən, Azərbaycanca)

💰 Satış Mətni:
(3-4 cümlə, məhsulun faydası, Azərbaycanca)

🎬 TikTok Hook:
(1 cümlə, maraqlı başlanğıc, Azərbaycanca)

#️⃣ Hashtaglar:
#birinci #ikinci #üçüncü #dördüncü #beşinci

Əgər istifadəçi salam, kimsen, nəsən kimi şeylər yazarsa — çox qısa cavab ver və məhsul adı göndərməyə yönləndir. Heç bir başqa mövzuda danışma."""


# Alt düymə klaviaturası
def main_keyboard():
    keyboard = [
        [KeyboardButton("🚀 Başla"), KeyboardButton("ℹ️ Haqqında")],
        [KeyboardButton("☕ Dəstək ol"), KeyboardButton("💸 Donate")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def ask_ai(user_text: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
    )
    return response.choices[0].message.content


async def send_welcome(update: Update):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"Salam, {user_name}! 👋\n\n"
        "Mən *Rawonz.EXE* tərəfindən hazırlanmış AI marketinq assistentiyəm 🤖\n\n"
        "Sənə aşağıdakıları hazırlayacağam:\n\n"
        "📌 Caption\n"
        "💰 Satış mətni\n"
        "🎬 TikTok hook\n"
        "#️⃣ Hashtaglar\n\n"
        "━━━━━━━━━━━━━━━\n"
        "👇 Məhsul adını göndər, başlayaq!\n\n"
        "Məsələn: *dubai şokoladı*, *iphone kabı*, *parfüm*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "☕ Dəstək ol: https://buymeacoffee.com/rawonzexe\n"
        "💸 Donate: https://donuter.org/rawonzexe",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_welcome(update)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()

    # Düymə cavabları
    if user_text == "🚀 Başla":
        await update.message.reply_text(
            "👇 Məhsul adını göndər, mən dərhal hazırlayım!\n\n"
            "Məsələn: *dubai şokoladı*, *iphone kabı*, *parfüm*",
            parse_mode="Markdown"
        )
        return

    if user_text == "ℹ️ Haqqında":
        await update.message.reply_text(
            "🤖 *Rawonz AI* haqqında:\n\n"
            "Bu bot *Rawonz.EXE* tərəfindən hazırlanıb.\n\n"
            "Məhsul adını göndər, sənin üçün:\n"
            "📌 Caption\n"
            "💰 Satış mətni\n"
            "🎬 TikTok hook\n"
            "#️⃣ Hashtaglar\n\n"
            "hazırlayıram! 🚀",
            parse_mode="Markdown"
        )
        return

    if user_text == "☕ Dəstək ol":
        await update.message.reply_text(
            "☕ Dəstək olmaq üçün:\n\nhttps://buymeacoffee.com/rawonzexe"
        )
        return

    if user_text == "💸 Donate":
        await update.message.reply_text(
            "💸 Donate üçün:\n\nhttps://donuter.org/rawonzexe"
        )
        return

    # Qısa salamlara cavab
    qisa_sozler = ["salam", "hi", "hello", "kimsen", "nəsən", "nesan", "ney", "?", "hə", "he"]
    if user_text.lower() in qisa_sozler:
        await update.message.reply_text(
            "Salam! 👋 Mən Rawonz AI-yəm.\n\n"
            "Məhsul adını göndər, sənə marketinq kontenti hazırlayım! 👇\n\n"
            "Məsələn: *dubai şokoladı*",
            parse_mode="Markdown"
        )
        return

    # AI cavabı
    await update.message.reply_text("⏳ Hazırlanır...")
    try:
        answer = ask_ai(user_text)
        await update.message.reply_text(answer)
    except Exception as e:
        print("FULL ERROR:", e)
        await update.message.reply_text("Xəta baş verdi. Terminal-ə bax.")


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot işləyir...")
app.run_polling()