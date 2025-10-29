import os
from aiogram import Router
from aiogram.types import Message, FSInputFile
from bot.utils.generate_random_velechins import pew
from aiogram.fsm.context import FSMContext
from bot.states.number_Input import NumberInput

router = Router()

@router.message()
async def send_graph(message: Message, k0, k1, arr, state: FSMContext):
    filename = pew(arr, k0, k1, message.from_user.id)
    
    caption=f"График распределения суммы случайных величин\n\n"
    
    if k0 != k1:
        caption += f"{k0} ≤ k ≤ {k1}\nВероятности: {arr}"
    else:  caption += f"k = {k1}\nВероятности: {arr}"
    
    photo = FSInputFile(filename)
    await message.bot.send_photo(
        chat_id=message.from_user.id,
        photo=photo,
        caption=caption
    )

    if os.path.exists(filename):
        os.remove(filename)
