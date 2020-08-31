import telebot, json, requests, time
import ToPng
from io import BytesIO


def load_config():
    with open('token.json') as json_file:
        return json.load(json_file)

config = load_config()

print(config['api']['token'])

bot = telebot.TeleBot(config['api']['token'])

def download_file(file_path):
    req = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config['api']['token'], file_path))
    return req;

def download_and_send_photo(message, file_path):
    req = download_file(file_path)
    if req.status_code == 200:
        try:
            file2 = ToPng.convert_to_png(BytesIO(req.content))
            file2.name = 'image.png'
            bot.send_document(message.chat.id, file2)
        except:
            bot.reply_to(message, 'something went wrong, maybe file is not an image')
    else:
        bot.reply_to(message, 'something went wrong, please try again')

@bot.message_handler(content_types=['document'])
def get_document(message):
    file_info = bot.get_file(message.document.file_id)
    if message.document.file_size > 2000000:
        bot.reply_to(message, 'maximum file size is 2MB')
        return
    download_and_send_photo(message, file_info.file_path)

@bot.message_handler(commands=['start', 'help'])
def handle_help(message):
    bot.reply_to(message, 'send your image(as photo or document) or sticker to get its raw copy in png')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    print(len(message.photo))
    max_photo = message.photo[0]
    for photo in message.photo:
        if photo.file_size > max_photo.file_size:
            max_photo = photo
    file_info = bot.get_file(max_photo.file_id)
    download_and_send_photo(message, file_info.file_path)

@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    file_info = bot.get_file(message.sticker.file_id)
    if message.sticker.is_animated:
        req = download_file(file_info.file_path)
        if req.status_code == 200:
            file2 = BytesIO(req.content)
            file2.name = 'image.tgs'
            bot.send_document(message.chat.id, file2)
            bot.reply_to(message, 'just download your animated sticker with right-click. If you are using mobile version of telegram, accept my condolences.' )
        else:
            bot.reply_to('something went wrong, please try again')
        return
    download_and_send_photo(message, file_info.file_path)

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as err:
        time.sleep(5)
