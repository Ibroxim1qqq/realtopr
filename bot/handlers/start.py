from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from bot.states.realtor import RegisterState
from bot.keyboards.reply import contact_kb, get_regions_kb, type_kb, menu_kb

from utils.db import db
from bot.loader import bot

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    # Check if already registered
    realtor = db.get_realtor(message.from_user.id)
    if realtor:
        await message.answer(f"Assalomu alaykum, {realtor[1]}! Xush kelibsiz.", reply_markup=menu_kb)
        return

    await message.answer("Assalomu alaykum! Rieltor sifatida ro'yxatdan o'tish uchun ism-familiyangizni kiriting.")
    await state.set_state(RegisterState.fullName)

@router.message(F.text == "💰 Mening Balansim")
async def balance_handler(message: Message):
    realtor = db.get_realtor(message.from_user.id)
    if realtor:
        # realtor: id, name, region, type, phone, balance, reg
        # Balance is at index 5
        balance = realtor[5]
        await message.answer(f"💰 Sizning balansingiz: {balance} so'm")
    else:
        await message.answer("Siz ro'yxatdan o'tmagansiz.")


@router.message(RegisterState.fullName)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(fullName=message.text)
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=contact_kb)
    await state.set_state(RegisterState.phone)

@router.message(RegisterState.phone)
async def get_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text
    
    await state.update_data(phone=phone)
    await message.answer("Qaysi tumanga xizmat ko'rsatasiz?", reply_markup=get_regions_kb())
    await state.set_state(RegisterState.region)

@router.message(RegisterState.region)
async def get_region(message: Message, state: FSMContext):
    await state.update_data(region=message.text)
    await message.answer("Siz asosan nima bilan shug'ullanasiz?", reply_markup=type_kb)
    await state.set_state(RegisterState.type)

@router.message(RegisterState.type)
async def get_type(message: Message, state: FSMContext):
    data = await state.get_data()
    r_type = message.text
    
    # Map text to simplified type if needed, or store as is
    # Data: telegram_id, full_name, region, r_type, phone
    
    success = db.add_realtor(
        telegram_id=message.from_user.id,
        full_name=data['fullName'],
        region=data['region'],
        r_type=r_type,
        phone=data['phone']
    )
    
    if success:
        await message.answer("Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz. Yangi mijozlar haqida shu yerda xabar olasiz.", reply_markup=menu_kb)
    else:
        await message.answer("Xatolik yuz berdi. Qaytadan urinib ko'ring yoki keyinroq kiring.")
    
    await state.clear()
