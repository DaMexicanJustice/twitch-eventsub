from flask import Flask, request, jsonify, Response
import hmac
import hashlib
import json
from dotenv import load_dotenv
import os
import materia_bot

load_dotenv()
TWITCH_SECRET = os.getenv('my_secret')

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    print("reached")
    # Verify signature
    message_id = request.headers.get('Twitch-Eventsub-Message-Id')
    timestamp = request.headers.get('Twitch-Eventsub-Message-Timestamp')
    message_signature = request.headers.get('Twitch-Eventsub-Message-Signature')
    body = request.data.decode('utf-8')
    hmac_message = message_id + timestamp + body
    if TWITCH_SECRET is None:
        print("⚠️ TWITCH_SECRET is not set! Check your .env file.")
        return 'Server misconfiguration', 500
    my_signature = 'sha256=' + hmac.new(
        TWITCH_SECRET.encode(), hmac_message.encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(my_signature, message_signature):
        return 'Invalid signature', 403

    payload = json.loads(body)

    # Handle challenge during subscription
    if payload['subscription']['type'] == 'channel.channel_points_custom_reward_redemption.add':
        if payload['subscription']['status'] == 'webhook_callback_verification_pending':
            if payload.get("challenge"):
                return Response(payload["challenge"], status=200, mimetype="text/plain")

    # Actual event
    if payload['subscription']['type'] == 'channel.channel_points_custom_reward_redemption.add':
        event = payload['event']
        user = event['user_name']
        reward = event['reward']['title']
        print(f"✅ {user} redeemed: {reward}")
        # Call your handle_redemption here:
        materia_bot.handle_redemption(user, reward)

    return '', 204


if __name__ == '__main__':
    import payload  # auto-register when deployed
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
