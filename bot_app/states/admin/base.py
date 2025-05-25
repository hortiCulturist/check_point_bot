from aiogram.fsm.state import State, StatesGroup


class TaskStates(StatesGroup):
    waiting_for_duration_input = State()


class AddTaskStates(StatesGroup):
    choosing_chat = State()
    entering_title = State()
    entering_type = State()
    entering_target_url = State()
    entering_button_text = State()
    choosing_duration = State()
    entering_custom_duration = State()
    entering_manual_duration = State()
