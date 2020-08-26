import telebot, json, requests
import ToPng
from io import BytesIO


def load_config():
    with open('token.json') as json_file:
        return json.load(json_file)

config = load_config()

print(config['api']['token'])

bot = telebot.TeleBot(config['api']['token'])

@bot.message_handler(content_types=['document'])
def get_document(message):
    file_info = bot.get_file(message.document.file_id)
    if message.document.file_size > 2000000:
        bot.reply_to(message, 'maximum file size is 2MB')
        return
    print(message.document.file_size, file_info.file_path)
    print('https://api.telegram.org/file/bot{0}/{1}'.format(config['api']['token'], file_info.file_path))
    req = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config['api']['token'], file_info.file_path))
    print(req.status_code)
    if req.status_code == 200:
        print('kek')
        try:
            file2 = ToPng.convert_to_png(BytesIO(req.content))
            file2.name = 'image.png'
            bot.send_document(message.chat.id, file2)
        except:
            bot.reply_to(message, 'something went wrong, maybe file is not an image')
        #print(file.headers)
    else:
        bot.reply_to(message, 'something went wrong, please try again')

@bot.message_handler(commands=['start', 'help'])
def handle_help(message):
    bot.reply_to(message, 'send your image in file format, just like you do in @Stickers')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, 'send your image in file format, just like you do in @Stickers')

bot.polling()
