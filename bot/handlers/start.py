from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.kb.reply import select_work_mode_keyboard

router = Router()

@router.message(F.text.lower() == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выбери, какой режим работы использовать:\n\n"
        "1) рассчитывать распределение вероятностей для суммы нескольких независимых одинаково распределённых дискретных случайных величин.\n\n"
        "2) находить сумму случайных величин, и проверять, является ли она нормально распределенной.",
        reply_markup=select_work_mode_keyboard
    )
