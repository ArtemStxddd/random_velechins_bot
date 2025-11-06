import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import norm, kstest

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states.convolution_input import ConvolutionInput
from bot.kb.reply import get_select_work_mode_for_second_keyboard


router = Router()

RUSSIAN_DISTRIBUTIONS = {
    "нормальное":      ["norm", ["среднее", "сигма"], ["loc", "scale"]],
    "равномерное":     ["uniform", ["начало", "длина"], ["loc", "scale"]],
    "экспоненциальное":["expon", ["масштаб"], ["scale"]],
    "гамма":           ["gamma", ["форма", "смещение", "масштаб"], ["a", "loc", "scale"]],
    "бета":            ["beta", ["альфа", "бета", "смещение", "масштаб"], ["a", "b", "loc", "scale"]],
    "треугольное":     ["triang", ["мода", "смещение", "масштаб"], ["c", "loc", "scale"]],
    "хи-квадрат":      ["chi2", ["степени свободы", "смещение", "масштаб"], ["df", "loc", "scale"]],
    "логнормальное":   ["lognorm", ["сигма", "смещение", "масштаб"], ["s", "loc", "scale"]]
}


def create_distribution(name_ru, params_dict):
    dist_name, _, params_en = RUSSIAN_DISTRIBUTIONS[name_ru]
    dist = getattr(stats, dist_name)
    return dist(**{params_en[i]: params_dict[key] for i, key in enumerate(params_dict)})

def get_ppf_range(dist, q_low=1e-6, q_high=1-1e-6, fallback_n=200000):
    try:
        a = dist.ppf(q_low)
        b = dist.ppf(q_high)
        if np.isfinite(a) and np.isfinite(b):
            return float(a), float(b)
    except Exception:
        pass
    s = dist.rvs(size=fallback_n)
    return float(np.quantile(s, q_low)), float(np.quantile(s, q_high))


@router.message(F.text.lower() == "/convolution")
@router.message(F.text.lower() == "второй")
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(ConvolutionInput.waiting_for_first_distribution)
    await message.answer(
        "Алгоритм находит сумму случайных величин и проверяет, является ли она нормально распределенной.\n"
        "Выберите первое распределение:",
        reply_markup=get_select_work_mode_for_second_keyboard(RUSSIAN_DISTRIBUTIONS)
    )


@router.message(ConvolutionInput.waiting_for_first_distribution)
async def first_distribution_chosen(message: Message, state: FSMContext):
    name_ru = message.text.lower()
    if name_ru not in RUSSIAN_DISTRIBUTIONS:
        await message.answer("Неизвестное распределение, выберите из клавиатуры.")
        return

    await state.update_data(first_dist_name=name_ru)

    _, params_ru, _ = RUSSIAN_DISTRIBUTIONS[name_ru]
    await state.update_data(first_dist_params_list=params_ru)
    await state.update_data(first_dist_params={})

    await state.set_state(ConvolutionInput.waiting_for_first_params)
    await message.answer(
        f"Введите параметры для '{name_ru}' через запятую в порядке: {', '.join(params_ru)}\n"
    )


@router.message(ConvolutionInput.waiting_for_first_params)
async def first_distribution_params(message: Message, state: FSMContext):
    data = await state.get_data()
    params_ru = data["first_dist_params_list"]
    vals = message.text.split(",")
    if len(vals) != len(params_ru):
        await message.answer(f"Неверное количество параметров, требуется {len(params_ru)}.")
        return

    params_dict = {}
    for key, val in zip(params_ru, vals):
        try:
            params_dict[key] = float(val)
        except ValueError:
            await message.answer(f"Параметр '{key}' не число, используем 0")
            params_dict[key] = 0

    await state.update_data(first_dist_params=params_dict)
    await state.set_state(ConvolutionInput.waiting_for_second_distribution)
    await message.answer(
        "Выберите второе распределение:",
        reply_markup=get_select_work_mode_for_second_keyboard(RUSSIAN_DISTRIBUTIONS)
    )


@router.message(ConvolutionInput.waiting_for_second_distribution)
async def second_distribution_chosen(message: Message, state: FSMContext):
    name_ru = message.text.lower()
    if name_ru not in RUSSIAN_DISTRIBUTIONS:
        await message.answer("Неизвестное распределение, выберите из клавиатуры.")
        return

    await state.update_data(second_dist_name=name_ru)
    _, params_ru, _ = RUSSIAN_DISTRIBUTIONS[name_ru]
    await state.update_data(second_dist_params_list=params_ru)
    await state.update_data(second_dist_params={})
    await state.set_state(ConvolutionInput.waiting_for_second_params)

    await message.answer(
        f"Введите параметры для '{name_ru}' через запятую в порядке: {', '.join(params_ru)}"
    )


import os
from aiogram.types import FSInputFile

@router.message(ConvolutionInput.waiting_for_second_params)
async def second_distribution_params(message: Message, state: FSMContext):
    data = await state.get_data()
    params_ru = data["second_dist_params_list"]
    vals = message.text.split(",")
    if len(vals) != len(params_ru):
        await message.answer(f"Неверное количество параметров, требуется {len(params_ru)}.")
        return

    params_dict = {}
    for key, val in zip(params_ru, vals):
        try:
            params_dict[key] = float(val)
        except ValueError:
            params_dict[key] = 0

    await state.update_data(second_dist_params=params_dict)

    data = await state.get_data()
    dist1 = create_distribution(data["first_dist_name"], data["first_dist_params"])
    dist2 = create_distribution(data["second_dist_name"], data["second_dist_params"])

    # Диапазон
    x1_min, x1_max = get_ppf_range(dist1)
    x2_min, x2_max = get_ppf_range(dist2)
    pad = 0.1 * max(x1_max - x1_min, x2_max - x2_min)
    x_start = min(x1_min, x2_min) - pad
    x_end = max(x1_max, x2_max) + pad

    N = 10000
    x = np.linspace(x_start, x_end, N)
    dx = x[1] - x[0]

    pdf1 = dist1.pdf(x)
    pdf2 = dist2.pdf(x)

    pdf_sum = np.convolve(pdf1, pdf2, mode="full") * dx
    pdf_sum /= np.trapezoid(pdf_sum, dx=dx)
    len_sum = len(pdf_sum)
    x_sum = 2*x_start + np.arange(len_sum) * dx

    mean_sum = np.trapezoid(x_sum * pdf_sum, x_sum)
    var_sum = np.trapezoid((x_sum - mean_sum)**2 * pdf_sum, x_sum)
    sigma_sum = np.sqrt(var_sum)

    sample = np.random.choice(x_sum, size=10000, p=pdf_sum / pdf_sum.sum())
    stat, p_value = kstest(sample, 'norm', args=(mean_sum, sigma_sum))

    filename = f"sum_distribution_{message.from_user.id}.png"
    plt.figure(figsize=(10,6))
    plt.plot(x, pdf1, label=f"X₁ ~ {data['first_dist_name']}({data['first_dist_params']})")
    plt.plot(x, pdf2, label=f"X₂ ~ {data['second_dist_name']}({data['second_dist_params']})")
    plt.plot(x_sum, pdf_sum, label="PDF(X₁ + X₂)", linestyle="--", linewidth=2.5)
    pdf_norm = norm.pdf(x_sum, mean_sum, sigma_sum)
    plt.plot(x_sum, pdf_norm, ':', label=f"Нормальная аппроксимация N({mean_sum:.2f}, {sigma_sum:.2f}²)")
    plt.title("Сумма двух случайных величин")
    plt.xlabel("x")
    plt.ylabel("Плотность вероятности")
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

    caption = (
        f"Среднее: {mean_sum:.4f}\nСигма: {sigma_sum:.4f}\n\n"
        f"{'Распределение суммы близко к нормальному.' if p_value>0.05 else 'Распределение суммы отличается от нормального.'}"
    )

    photo = FSInputFile(filename)
    await message.bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=caption)

    if os.path.exists(filename):
        os.remove(filename)

    await message.answer("Вы можете повторить, введя команду /convolution или выбрать другой режим работы /start")
    await state.clear()
