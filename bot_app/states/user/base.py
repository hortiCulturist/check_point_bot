from aiogram.fsm.state import StatesGroup, State


class AccessFlow(StatesGroup):
    waiting_for_check = State()
