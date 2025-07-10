import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.twitch.tv/helix/eventsub/subscriptions"

headers = {
    "Client-Id": os.getenv("client_id"),
    "Authorization": f"Bearer {os.getenv('access_token')}",
    "Content-Type": "application/json"
}

payload = {
    "type": "channel.channel_points_custom_reward_redemption.add",
    "version": "1",
    "condition": {
        "broadcaster_user_id": os.getenv("user_id")
    },
    "transport": {
        "method": "webhook",
        "callback": "https://9376248c37d7.ngrok-free.app/webhook",
        "secret": os.getenv("my_secret")
    }
}

# print(os.getenv("client_id"), os.getenv('access_token'), os.getenv("user_id"), os.getenv("my_secret"))
response = requests.post(url, json=payload, headers=headers)
print(response.status_code)
print(response.text)