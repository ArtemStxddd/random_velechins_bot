from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import numpy as np
from bot.handlers.process_data import send_graph
from bot.states.number_Input import NumberInput

router = Router()


@router.message(F.text.lower() == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(NumberInput.waiting_for_array)
    await message.answer(
        "Введите массив дробных чисел через пробел (пример ввода: 0.2 0.3 0.5)\n\n"
        "Сумма должна быть равна 1, не более 20 чисел.\n"
    )

@router.message(NumberInput.waiting_for_array)
async def get_array(message: Message, state: FSMContext):
    try:
        arr = [float(x) for x in message.text.split()]
    except ValueError:
        await message.answer("Пожалуйста, вводите корректные дробные числа через пробел.")
        return

    if len(arr) == 0 or len(arr) > 20:
        await message.answer("Массив должен содержать от 1 до 20 чисел. Попробуйте снова.")
        return

    if not np.isclose(sum(arr), 1.0):
        await message.answer(
            f"Сумма вероятностей должна быть равна 1 (текущее значение = {sum(arr)})"
        )
        return

    await state.update_data(array=arr)
    await state.set_state(NumberInput.waiting_for_k)
    await message.answer(
        f"Массив: {arr}\n\n"
        f"Теперь укажите число k (1 ≤ k ≤ {len(arr)}).\n"
        "Примеры ввода:\n"
        " - Одно число: 2\n"
        " - Диапазон: 1 3"
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
            await send_graph(message, k, k, arr, state)
            await message.answer(f"Укажите новое(ые) значение k. Если хотите обработать новый массив напишите /start")
            await state.set_state(NumberInput.waiting_for_k)

        elif len(tokens) == 2:
            k0, k1 = int(tokens[0]), int(tokens[1])
            if k0 < 1 or k1 > len(arr) or k0 > k1:
                await message.answer(f"Диапазон должен быть в пределах от 1 до {len(arr)}, min ≤ max.")
                return
            
            await send_graph(message, k0, k1, arr, state)
            await message.answer(f"Укажите новое(ые) значение k. Если хотите обработать новый массив напишите /start")
            await state.set_state(NumberInput.waiting_for_k)

        else:
            await message.answer(
                "Введите либо одно число, либо два числа через пробел для диапазона.\n"
                "Примеры:\n"
                " - Одно число: 2\n"
                " - Диапазон: 1 3"
            )
            return

    except ValueError:
        await message.answer(
            "Пожалуйста, вводите корректные целые числа для k или диапазона.\n"
            "Примеры:\n"
            " - Одно число: 2\n"
            " - Диапазон: 1 3"
        )
