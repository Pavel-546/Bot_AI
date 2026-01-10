import os
from perplexity import Perplexity
from dotenv import load_dotenv
load_dotenv()

# Или явно указываем API ключ
client = Perplexity(api_key=os.environ.get('AI_TOKEN'))

# Пример запроса к Chat API
response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Расскажи о последних новостях в AI"
        }
    ],
    model="sonar"
)

print(response)
