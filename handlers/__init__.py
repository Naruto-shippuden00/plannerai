# Handlers package

# Dispatcher reference - bot.py dan import qilinadi
dp = None

def set_dispatcher(dispatcher):
    """Dispatcher'ni o'rnatish - bot.py dan chaqiriladi"""
    global dp
    dp = dispatcher
