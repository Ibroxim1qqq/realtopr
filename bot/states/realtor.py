from aiogram.fsm.state import StatesGroup, State

class RegisterState(StatesGroup):
    fullName = State()
    phone = State()
    region = State()
    type = State()
