from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from utils.db import db
from datetime import datetime

router = Router()

# Price logic - Hardcoded for now based on request description or fixed
PRICE_PER_CONTACT = 5000 # Example amount in sum

@router.callback_query(F.data.startswith("buy_contact:"))
async def buy_contact_handler(call: CallbackQuery, bot: Bot):
    request_id = call.data.split(":")[1]
    realtor_id = call.from_user.id
    
    # Get Realtor Info (mainly balance)
    realtor = db.get_realtor(realtor_id)
    if not realtor:
        await call.answer("Siz ro'yxatdan o'tmagansiz.", show_alert=True)
        return
    
    # realtor row: id, name, region, type, phone, balance, registered_at
    # Balance is index 5
    balance = int(realtor[5])
    
    if balance < PRICE_PER_CONTACT:
        await call.answer("Hisobingizda mablag' yetarli emas!", show_alert=True)
        return

    # Process Transaction
    db.update_balance(realtor_id, -PRICE_PER_CONTACT)
    db.add_transaction(realtor_id, request_id, PRICE_PER_CONTACT)
    
    # Get Request Info to show phone
    request_data = db.get_request(request_id)
    if request_data:
        # Request row: id, type, region, rooms, price, phone, status, created_at
        client_phone = request_data[5]
        
        await call.message.answer(f"✅ Xarid muvaffaqiyatli!\n\nMijoz raqami: {client_phone}")
        # Optionally edit the message to remove button or update text
        await call.message.edit_reply_markup(reply_markup=None)
        await call.answer()
    else:
        await call.answer("So'rov topilmadi.", show_alert=True)
