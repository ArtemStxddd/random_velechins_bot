from aiogram.fsm.state import StatesGroup, State

class NumberInput(StatesGroup):
    waiting_for_array = State()
    waiting_for_k = State()
