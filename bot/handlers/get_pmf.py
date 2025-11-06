import os
import numpy as np

from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot.utils.generate_random_velechins import pew
from bot.states.number_Input import NumberInput

router = Router()

async def send_graph(message: Message, k0, k1, arr):
    filename = pew(arr, k0, k1, message.from_user.id)
    
    caption=f"График распределения суммы случайных величин\n\n"
    
    if k0 != k1:
        caption += f"{k0} <= k <= {k1}\nВероятности: {arr}"
    else:  caption += f"k = {k1}\nВероятности: {arr}"
    
    photo = FSInputFile(filename)
    await message.bot.send_photo(
        chat_id=message.from_user.id,
        photo=photo,
        caption=caption
    )

    await message.answer("Вы можете выбрать новые вероятности, введя команду /pmf или выбрать другой режим работы, введя команду /start")
    await message.answer("Также, вы можете указать новые значения k для текущих вероятностей.")
    
    if os.path.exists(filename):
        os.remove(filename)


@router.message(F.text.lower() == "/pmf")
@router.message(F.text.lower() == "первый")
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(NumberInput.waiting_for_array)
    await message.answer(
        "Алгоритм рассчитывает распределение вероятностей для суммы нескольких независимых одинаково распределённых дискретных случайных величин." ,
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "Введите вероятности через пробел;\n"
        "Сумма должна быть равна 1, не более 20 чисел;\n"
        "Не более 20 чисел;\n\n"
        "Пример ввода: 0.2 0.3 0.5\n"
        )

@router.message(NumberInput.waiting_for_array)
async def get_array(message: Message, state: FSMContext):
    try:
        arr = [float(x) for x in message.text.split()]
    except ValueError:
        await message.answer("Пожалуйста, вводите корректные значения вероятностей. Отправьте вероятности снова.")
        return

    if len(arr) == 0 or len(arr) > 20:
        await message.answer("Вероятностей должно быть от 1 до 20. Отправьте вероятности снова.")
        return

    if not np.isclose(sum(arr), 1.0):
        await message.answer(
            f"Сумма вероятностей должна быть равна 1, а текущее значение = {sum(arr)}. Отправьте вероятности снова."
        )
        return

    await state.update_data(array=arr)
    await state.set_state(NumberInput.waiting_for_k)
    await message.answer(
        f"Вероятности: {arr}\n\n"
        f"Теперь укажите число k (1 ≤ k ≤ {len(arr)}).\n\n"
        "Примеры ввода:\n"
        f" - Одно число: {len(arr)}\n"
        f" - Диапазон: 1 {len(arr)}"
    )

@router.message(NumberInput.waiting_for_k)
async def get_k(message: Message, state: FSMContext):
    data = await state.get_data()
    arr = data['array']
    tokens = message.text.split()
    try:
        if len(tokens) == 1:
            k = int(tokens[0])
            if k < 1 or k > len(arr):
                await message.answer(f"Число k должно быть в диапазоне от 1 до {len(arr)}.")
                return
            await send_graph(message, k, k, arr)
            await state.set_state(NumberInput.waiting_for_k)
           

        elif len(tokens) == 2:
            k0, k1 = int(tokens[0]), int(tokens[1])
            if k0 < 1 or k1 > len(arr) or k0 > k1:
                await message.answer(f"Диапазон должен быть в пределах от 1 до {len(arr)}. Укажите k снова.")
                return
            
            await send_graph(message, k0, k1, arr)
            await state.set_state(NumberInput.waiting_for_k)
            

        else:
            await message.answer(
                "Введите либо одно число, либо два числа через пробел для диапазона.\n"
                "Примеры ввода:\n\n"
                f" - Одно число: {len(arr)}\n"
                f" - Диапазон: 1 {len(arr)}\n\n"
                "Укажите k снова."
            )
            return

    except ValueError:
        await message.answer(
            "Пожалуйста, вводите корректные целые числа для k или диапазона.\n"
            "Примеры:\n"
            f" - Одно число: {len(arr)}\n"
            f" - Диапазон: 1 {len(arr)}\n\n"
            "Укажите k снова."
        )


