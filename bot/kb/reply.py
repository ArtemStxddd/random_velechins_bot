from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

select_work_mode_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [(KeyboardButton(text="Первый"))],
        [(KeyboardButton(text="Второй"))],
    ],
    resize_keyboard=True,
)

def get_select_work_mode_for_second_keyboard(RUSSIAN_DISTRIBUTIONS): 
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=name.capitalize())] for name in RUSSIAN_DISTRIBUTIONS.keys()],
        resize_keyboard=True
    )


