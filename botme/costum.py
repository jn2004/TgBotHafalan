import telegram as tg

class KeyboardMarkup(tg.ReplyKeyboardMarkup):
    
    def __init__(self, array, resize_keyboard=True, **kwargs):
        super().__init__(array, resize_keyboard=resize_keyboard, **kwargs)

class Button(tg.InlineKeyboardButton):
    
    def __init__(self, array, callback_data):
        super().__init__(array, callback_data=callback_data)
