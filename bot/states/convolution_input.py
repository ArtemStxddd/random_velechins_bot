from aiogram.fsm.state import StatesGroup, State

class ConvolutionInput(StatesGroup):
    waiting_for_first_distribution = State()
    waiting_for_first_params = State()
    waiting_for_second_distribution = State()
    waiting_for_second_params = State()
