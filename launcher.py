import subprocess
import time
import os
import sys

# Path to your bot directory
BOT_DIR = os.path.expanduser("~/Desktop/projects/python/eventsub")

def start_flask():
    print("⚙️ Launching Flask server...")
    return subprocess.Popen(["python", "flask_server.py"], cwd=BOT_DIR)

def start_ngrok():
    print("🌐 Launching ngrok tunnel...")
    subprocess.Popen(["start", "cmd", "/k", "ngrok http 3000"], shell=True)

def run_payload():
    print("📡 Sending Twitch subscription request...")
    result = subprocess.run(["python", "payload.py"], cwd=BOT_DIR)
    if result.returncode == 0:
        print("✅ Subscription sent successfully!")
    else:
        print("❌ Subscription failed.")

def main():
    os.chdir(BOT_DIR)

    flask_process = start_flask()
    start_ngrok()

    print("⏳ Waiting for services to warm up...")
    time.sleep(3)  # Give Flask and ngrok time to bind

    run_payload()

    print("\n🟢 All systems go. Leave this window open while your bot runs.")
    print("Press Ctrl+C to shut down Flask server when you're done.")

    try:
        flask_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Flask server...")
        flask_process.terminate()
        sys.exit()

if __name__ == "__main__":
    main()