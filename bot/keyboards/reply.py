from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

regions = [
    "Bektemir", "Chilonzor", "Mirobod", "Mirzo Ulug'bek", 
    "Olmazor", "Sergeli", "Shayxontohur", "Uchtepa", 
    "Yakkasaroy", "Yashnobod", "Yunusobod", "Yangihayot"
]

def get_regions_kb():
    buttons = []
    row = []
    for region in regions:
        row.append(KeyboardButton(text=region))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Sotib olish"), KeyboardButton(text="Ijaraga olish")],
        [KeyboardButton(text="Ikkisi ham")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Mening Balansim")],
        [KeyboardButton(text="📊 Statistika")] # Optional future feature
    ],
    resize_keyboard=True
)
