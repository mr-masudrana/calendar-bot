import requests

def handler(request):
    # Hit self to trigger /today command
    BOT_TOKEN = "YOUR_TOKEN"
    CHAT_ID = "YOUR_CHAT_ID"

    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                 params={"chat_id": CHAT_ID, "text": "Daily schedule test"})
    
    return {"statusCode": 200, "body": "OK"}
