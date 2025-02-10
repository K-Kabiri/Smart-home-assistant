import logging
import time
import serial
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from langchain_openai import ChatOpenAI

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

ESP_PORT = "COM7"
BAUD_RATE = 115200

esp32 = None

last_request_time = 0
request_interval = 5


def initialize_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        base_url="https://api.avalai.ir/v1",
        api_key="aa-JSJpQSzR0ZH8qMrAg4DGgeUYXorCUoO8C0YM5G7ABvJxDGJ6",
    )


def initialize_serial():
    global esp32
    try:
        esp32 = serial.Serial(ESP_PORT, BAUD_RATE, dsrdtr=False, rtscts=False, timeout=1)
        esp32.dtr = False
        esp32.rts = False
        time.sleep(1)
        print("✅ Serial connected to ESP32.")
    except serial.SerialException as e:
        print(f"❌ Serial connection error: {e}")


def send_command_to_esp(command):
    if esp32 and esp32.is_open:
        try:
            esp32.write(command.encode())
            esp32.flush()
            print(f"📤 Sent to ESP32: {command}")
        except serial.SerialTimeoutException:
            print("❌ Serial write timeout.")


def read_response_from_esp():
    if esp32 and esp32.is_open:
        try:
            response = esp32.readline().decode('utf-8').strip()
            if response:
                print(f"📥 Received from ESP32: {response}")
                return response
        except Exception as e:
            print(f"❌ Error reading from ESP32: {e}")
    return None


def process_user_input(llm, user_input):
    global last_request_time

    if time.time() - last_request_time < request_interval:
        print("⏳ waiting ...")
        return None

    message = [
        {"role": "system", "content": """    
        You are an AI assistant for an IoT system that controls LED lights.    
        Based on the user's input, return a string of commands:   
        A: Turn on kitchen LED    
        B: Turn off kitchen LED    
        C: Turn on room LED    
        D: Turn off room LED    
        E: Turn on parking LED   
        F: Turn off parking LED   
        Respond ONLY with a string like 'AC' or 'DF'. Do not include spaces or explanations.    
        """},
        {"role": "user", "content": user_input},
    ]

    try:
        result = llm.invoke(message)
        commands = result.content.strip().upper()

        valid_commands = {"A", "B", "C", "D", "E", "F"}
        filtered_commands = "".join([c for c in commands if c in valid_commands])

        if filtered_commands:
            last_request_time = time.time()
            return filtered_commands
        else:
            print(f"❌ AI returned invalid response: {commands}")
    except Exception as e:
        print(f"❌ Error communicating with AI: {e}")

    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    print(f"💬 Telegram message: {user_input}")

    llm = initialize_llm()
    command = process_user_input(llm, user_input)

    if command:
        send_command_to_esp(command)
        await update.message.reply_text(f"✅ Command sent to ESP32: {command}")
    else:
        await update.message.reply_text("❌ Invalid command. Please try again.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"hello {user.mention_html()}! send your command.",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("help")


def start_bot():
    token = "7970797900:AAGL6AsnwyYpCYs64tVZR0mgMyIayb3z7Hk"
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    initialize_serial()

    application.run_polling()


if __name__ == "__main__":
    start_bot()
