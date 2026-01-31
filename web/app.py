from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from utils.db import db
import logging

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="web/templates")

class ClientRequest(BaseModel):
    request_type: str
    region: str
    rooms: str
    price: str
    phone: str

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.loader import bot

@app.post("/api/request")
async def submit_request(data: ClientRequest):
    try:
        req_id = db.add_request({
            "type": data.request_type,
            "region": data.region,
            "rooms": data.rooms,
            "price": data.price,
            "phone": data.phone
        })
        
        if req_id:
            # Broadcast logic removed - moved to Admin Approval
            return {"status": "success", "id": req_id, "message": "Moderatsiyaga yuborildi"}
        else:
            raise HTTPException(status_code=500, detail="Database Error")
    except Exception as e:
        logging.error(f"Error submitting request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/action")
async def admin_action(req_id: str = Form(...), action: str = Form(...)):
    if action == "approve":
        # 1. Update DB Status
        if db.update_request_status(req_id, "Approved"):
            
            # 2. Get Request Data for Broadcasting
            req_data_list = db.get_request(req_id)
            # req_data_list: [id, type, region, rooms, price, phone, status, created_at]
            if req_data_list:
                data = {
                    "request_type": req_data_list[1],
                    "region": req_data_list[2],
                    "rooms": req_data_list[3],
                    "price": req_data_list[4]
                }
                
                # 3. Broadcast to Public Channel
                from utils.config import CHANNEL_ID
                public_msg = (
                    f"🆕 <b>Yangi E'lon!</b>\n\n"
                    f"📍 Tuman: {data['region']}\n"
                    f"🚪 Xonalar: {data['rooms']}\n"
                    f"💰 Narx: {data['price']}\n"
                    f"📝 Turi: {data['request_type']}\n\n"
                    f"📞 Aloqa uchun botga kiring: @sotuuzbot"
                )
                
                if CHANNEL_ID and str(CHANNEL_ID).startswith("-100"):
                    try:
                        await bot.send_message(chat_id=CHANNEL_ID, text=public_msg)
                    except Exception as e:
                        logging.error(f"Failed to send to channel {CHANNEL_ID}: {e}")
                
                # 4. Broadcast to Targeted Realtors
                r_type_filter = data['request_type']
                realtors = db.get_realtors_by_filter(data['region'], r_type_filter)
                
                private_msg = (
                    f"🎯 <b>Sizning tumaningizda yangi so'rov!</b>\n\n"
                    f"📍 Tuman: {data['region']}\n"
                    f"🚪 Xonalar: {data['rooms']}\n"
                    f"💰 Narx: {data['price']}\n"
                    f"📝 Turi: {data['request_type']}"
                )
                
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"📞 Kontaktni olish (5000 so'm)", callback_data=f"buy_contact:{req_id}")]
                ])
                
                for r in realtors:
                    try:
                        if r.get('telegram_id'):
                            await bot.send_message(chat_id=r['telegram_id'], text=private_msg, reply_markup=kb)
                    except Exception as e:
                        logging.error(f"Failed to send to realtor {r.get('telegram_id')}: {e}")

    elif action == "reject":
        db.update_request_status(req_id, "Rejected")
        
    return RedirectResponse(url="/admin", status_code=303)
@app.get("/admin")
async def admin_dashboard(request: Request):
    stats = db.get_stats()
    raw_realtors = db.get_all_realtors()
    # Filter out empty or invalid realtor records if necessary
    realtors = [r for r in raw_realtors if r.get('telegram_id')]
    
    pending_requests = db.get_pending_requests()
    
    from utils.config import CHANNEL_ID
    channel_valid = False
    if CHANNEL_ID and str(CHANNEL_ID).startswith("-100") and len(str(CHANNEL_ID)) > 9:
        channel_valid = True
        
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "daily_requests": stats.get("daily_requests", 0),
        "daily_sales": stats.get("daily_sales", 0),
        "total_realtors": stats.get("total_realtors", 0),
        "realtors": realtors,
        "pending_requests": pending_requests,
        "channel_id": CHANNEL_ID,
        "channel_id_valid": channel_valid
    })

@app.post("/admin/balance")
async def update_balance(telegram_id: str = Form(...), amount: int = Form(...)):
    db.update_balance(telegram_id, amount)
    return RedirectResponse(url="/admin", status_code=303)
