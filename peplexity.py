import os
from dotenv import load_dotenv
import telebot
from telebot import types
from perplexity import Perplexity

load_dotenv()

bot = telebot.TeleBot(os.environ.get('BOT_TOKENn'))
client = Perplexity(api_key=os.environ.get('AI_TOKEN'))

user_models = {}

MODELS = {
    'sonar': 'Sonar (быстрый)',
    'sonar-pro': 'Sonar Pro (продвинутый)',
    'sonar-reasoning': 'Sonar Reasoning (с рассуждениями)',
}

def create_model_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for model_id, model_name in MODELS.items():
        button = types.InlineKeyboardButton(
            text=model_name,
            callback_data=f"model_{model_id}"
        )
        markup.add(button)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Дарова заебал я ничего не платил но у меня перплексити есть прошка! Я бот на базе Perplexity AI.\n\n"
        "Доступные команды:\n"
        "/model - Выбрать модель AI\n"
        "/current - Показать текущую модель\n\n"
        "Просто отправь мне любой вопрос, и я отвечу!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['model'])
def choose_model(message):
    """Обработчик команды выбора модели"""
    current_model = user_models.get(message.chat.id, 'sonar')
    text = f"Текущая модель: {MODELS[current_model]}\n\nВыбери модель:"
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=create_model_keyboard()
    )

@bot.message_handler(commands=['current'])
def show_current_model(message):
    """Показывает текущую выбранную модель"""
    current_model = user_models.get(message.chat.id, 'sonar')
    bot.reply_to(
        message,
        f"Текущая модель: {MODELS[current_model]}"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('model_'))
def callback_model_selection(call):
    """Обработчик выбора модели через кнопки"""
    model_id = call.data.replace('model_', '')
    user_models[call.message.chat.id] = model_id
    
    bot.answer_callback_query(
        call.id,
        f"Модель изменена на {MODELS[model_id]}"
    )
    bot.edit_message_text(
        f"Выбрана модель: {MODELS[model_id]}\n\nТеперь можешь задавать вопросы!",
        call.message.chat.id,
        call.message.message_id
    )

@bot.message_handler(func=lambda message: True)
def handle_question(message):
    """Обработчик всех текстовых сообщений"""
    user_id = message.chat.id
    user_question = message.text
    
    # Получаем выбранную модель или используем по умолчанию
    selected_model = user_models.get(user_id, 'sonar')
    
    # Отправляем уведомление о обработке
    processing_msg = bot.reply_to(
        message,
        f"⏳ Обрабатываю вопрос с помощью {MODELS[selected_model]}..."
    )
    
    try:
        # Запрос к Perplexity API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_question
                }
            ],
            model=selected_model
        )
        
        # Извлекаем ответ
        answer = response.choices[0].message.content
        
        # Удаляем сообщение о обработке
        bot.delete_message(user_id, processing_msg.message_id)
        
        # Отправляем ответ (разбиваем на части если слишком длинный)
        if len(answer) > 4096:
            for i in range(0, len(answer), 4096):
                bot.send_message(user_id, answer[i:i+4096])
        else:
            bot.reply_to(message, answer)
            
    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка при обработке запроса:\n{str(e)}",
            user_id,
            processing_msg.message_id
        )

# Запуск бота
if __name__ == '__main__':
    print("🤖 Бот запущен...")
    bot.infinity_polling()
