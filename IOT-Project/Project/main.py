import serial
import time
from langchain_openai import ChatOpenAI

last_request_time = 0
request_interval = 5


def initialize_llm():
    """Initialize connection to AI model"""
    return ChatOpenAI(
        model="gpt-4o-mini",
        base_url="https://api.avalai.ir/v1",
        api_key="aa-JSJpQSzR0ZH8qMrAg4DGgeUYXorCUoO8C0YM5G7ABvJxDGJ6",
    )


def initialize_serial(port, baud_rate):
    """Initialize Serial communication with ESP32"""
    try:
        esp = serial.Serial(port, baud_rate, dsrdtr=False, rtscts=False, timeout=1)
        esp.dtr = False
        esp.rts = False
        time.sleep(1)  # Delay to ensure a stable connection
        return esp
    except serial.SerialException as e:
        print(f"❌ Error opening serial port: {e}")
        return None


def read_response_from_esp(esp):
    """Read data from ESP32 with flush()"""
    if esp and esp.is_open:
        try:
            esp.flushInput()
            response = esp.readline().decode('utf-8').strip()
            if response:
                print(f"📥 Received from ESP32: {response}")
                return response
        except Exception as e:
            print(f"❌ Error reading from ESP32: {e}")
    return None


def send_command_to_esp(esp, command):
    """Send command to ESP32 with flush()"""
    if esp and esp.is_open:
        try:
            esp.write(command.encode())
            esp.flushOutput()
            print(f"📤 Sent to ESP32: {command}")
        except serial.SerialTimeoutException:
            print("❌ Serial write timeout.")


def process_user_input(llm, user_input):
    """Process user input and send it to AI"""
    global last_request_time

    if time.time() - last_request_time < request_interval:
        print("⏳ Please wait a moment before sending another request.")
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
        Respond with a string like 'AC' to turn on both Kitchen and Room LEDs.  
        """},
        {"role": "user", "content": user_input},
    ]

    try:
        result = llm.invoke(message)
        commands = result.content.strip()
        # print(commands)
        valid_commands = ["A", "B", "C", "D", "E", "F"]
        if all(command in valid_commands for command in commands):
            last_request_time = time.time()  # Update last request time
            return commands
        else:
            print("❌ AI returned an invalid response. Please try again.")
    except Exception as e:
        print(f"❌ Error communicating with AI: {e}")

    return None


def main():
    """Main program execution"""
    llm = initialize_llm()
    esp_port = "COM7"  
    baud_rate = 115200
    esp32 = initialize_serial(esp_port, baud_rate)

    if not esp32:
        return

    while True:
        user_input = read_response_from_esp(esp32)
        if not user_input:
            continue

        if user_input.lower() == "exit":
            break

        command = process_user_input(llm, user_input)
        if command:
            send_command_to_esp(esp32, command)

        time.sleep(0.1)

    esp32.close()
    print("Serial connection closed.")


if __name__ == "__main__":
    main()
