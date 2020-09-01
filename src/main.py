#To create SSL keys use:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out weebhook_cert.pem
#
# in "Common Name write the same value as in WEBHOOK_HOST"


import telebot, json, requests, time, ssl, logging
import ToPng
from io import BytesIO

from aiohttp import web



#load and set configs
def load_config():
    with open('token.json') as json_file:
        return json.load(json_file)

config = load_config()

API_TOKEN = config['api']['token']

WEBHOOK_HOST = config['webhook']['host']
WEBHOOK_PORT = int(config['webhook']['port'])
WEBHOOK_LISTEN = config['webhook']['listen']

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

logging.basicConfig(filename='logs.txt', filemode='a', 
        format='%(asctime)s,%(msecs) %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

telebot.apihelper.READ_TIMEOUT = 5

bot = telebot.TeleBot(API_TOKEN, threaded=False)

app = web.Application()

# webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle)


#download file from telegram
def download_file(file_path):
    req = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config['api']['token'], file_path))
    return req;


#reply to message

def replyto(message, text): 
    try:
        bot.reply_to(message, text)
    except Exception as e:
        logging.error(e)
        time.sleep(1)
        replyto(message, text)

#download photo, convert it and send as document
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
        replyto(message, 'something went wrong, please try again')

@bot.message_handler(content_types=['document'])
def get_document(message):
    file_info = bot.get_file(message.document.file_id)
    if message.document.file_size > 2000000:
        replyto(message, 'maximum file size is 2MB')
        return
    download_and_send_photo(message, file_info.file_path)

@bot.message_handler(commands=['start', 'help'])
def handle_help(message):
    replyto(message, 'send your image(as photo or document) or sticker to get its raw copy in png')

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
            replyto(message, 'just download your animated sticker with right-click. If you are using mobile version of telegram, accept my condolences.' )
        else:
            replyto('something went wrong, please try again')
        return
    download_and_send_photo(message, file_info.file_path)

#remove webhook cause previous may be set
bot.remove_webhook()


bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))
print('set webhook', WEBHOOK_URL_BASE, WEBHOOK_URL_PATH, sep=' ')

#build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

print('kek ' + str(WEBHOOK_LISTEN) + ' ' + str(WEBHOOK_PORT))

web.run_app(
        app,
        host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=context,
)
