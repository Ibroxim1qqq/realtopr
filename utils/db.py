import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .config import GOOGLE_KEY_FILE, SHEET_URL
from datetime import datetime

import json
import os
import time

class GoogleSheet:
    def __init__(self):
        self.client = None
        self.sheet = None
        self.mock_data = {
            "realtors": [],
            "requests": [],
            "transactions": []
        }
        self.is_mock = False
        self.cache = {}
        self.cache_expiry = 30 # seconds
        self.connect()

    def connect(self):
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            
            # 1. Try ENV Variable (Best for Render/Cloud)
            json_creds = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if json_creds:
                creds_dict = json.loads(json_creds)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            # 2. Try File (Best for Local)
            elif GOOGLE_KEY_FILE and os.path.exists(GOOGLE_KEY_FILE):
                creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_KEY_FILE, scope)
            # 3. Fallback to Mock
            else:
                print("Warning: No Google Credentials found. Using Local JSON Mock DB.")
                self.is_mock = True
                self.load_mock()
                return

            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_url(SHEET_URL)
            self.ensure_tabs()
        except Exception as e:
            print(f"Error connecting to Google Sheet: {e}. Switching to Mock DB.")
            self.is_mock = True
            self.load_mock()

    def load_mock(self):
        if os.path.exists("mock_db.json"):
            with open("mock_db.json", "r") as f:
                self.mock_data = json.load(f)

    def save_mock(self):
        with open("mock_db.json", "w") as f:
            json.dump(self.mock_data, f, indent=4)

    def ensure_tabs(self):
        if self.is_mock or not self.sheet: return
        
        required_tabs = ["Realtors", "Requests", "Transactions"]
        existing_tabs = [ws.title for ws in self.sheet.worksheets()]
        
        for tab in required_tabs:
            if tab not in existing_tabs:
                try:
                    self.sheet.add_worksheet(title=tab, rows=1000, cols=10)
                    print(f"Created missing worksheet: {tab}")
                    # Optional: Add headers
                    ws = self.sheet.worksheet(tab)
                    if tab == "Realtors":
                        ws.append_row(["telegram_id", "full_name", "region", "type", "phone", "balance", "registered_at"])
                    elif tab == "Requests":
                        ws.append_row(["id", "type", "region", "rooms", "price", "phone", "status", "created_at"])
                    elif tab == "Transactions":
                        ws.append_row(["id", "realtor_id", "request_id", "amount", "date"])
                except Exception as e:
                    print(f"Error creating tab {tab}: {e}")

    def get_worksheet(self, name):
        if self.is_mock: return None
        if not self.sheet: self.connect()
        if self.sheet:
            return self.sheet.worksheet(name)
        return None

    def add_realtor(self, telegram_id, full_name, region, r_type, phone):
        # Normalize
        region = region.strip().lower()
        r_type = r_type.strip().lower()

        if self.is_mock:
            for r in self.mock_data["realtors"]:
                if str(r.get("telegram_id")) == str(telegram_id): return False
            self.mock_data["realtors"].append({
                "telegram_id": str(telegram_id),
                "full_name": full_name,
                "region": region,
                "type": r_type,
                "phone": phone,
                "balance": 0,
                "registered_at": str(datetime.now())
            })
            self.save_mock()
            return True

        ws = self.get_worksheet("Realtors")
        if not ws: return False
        
        cell = ws.find(str(telegram_id))
        if cell: return False

        ws.append_row([str(telegram_id), full_name, region, r_type, phone, 0, str(datetime.now())])
        return True

    def get_realtor(self, telegram_id):
        if self.is_mock:
            for r in self.mock_data["realtors"]:
                if str(r.get("telegram_id")) == str(telegram_id):
                    # Return list format to match gspread: id, name, region, type, phone, balance, reg
                    return [
                        r["telegram_id"], r["full_name"], r["region"], r["type"], 
                        r["phone"], r["balance"], r["registered_at"]
                    ]
            return None

        ws = self.get_worksheet("Realtors")
        if not ws: return None
        try:
            cell = ws.find(str(telegram_id))
            if cell:
                return ws.row_values(cell.row)
        except:
            pass
        return None
    
    def get_realtors_by_filter(self, region, r_type):
        if self.is_mock:
            filtered = []
            for r in self.mock_data["realtors"]:
                if r.get('region') == region:
                    if r.get('type') == 'Both' or r_type == 'Both' or r.get('type') == r_type:
                         filtered.append(r)
            return filtered

        ws = self.get_worksheet("Realtors")
        if not ws: 
            print("❌ Debug: Realtors sheet not found!")
            return []
        
        all_realtors = ws.get_all_records()
        print(f"🔍 Debug: Found {len(all_realtors)} realtors in DB.")
        
        filtered = []
        
        # Normalize input
        target_region = region.strip().lower() if region else ""
        target_type = r_type.strip().lower() if r_type else ""
        
        print(f"🔍 Debug: target_region='{target_region}', target_type='{target_type}'")

        for r in all_realtors:
            # Normalize db values
            r_region = str(r.get('region', '')).strip().lower()
            r_type_db = str(r.get('type', '')).strip().lower()
            r_id = r.get('telegram_id')
            
            print(f"  - Checking Realtor {r_id}: region='{r_region}', type='{r_type_db}'")

            # Check Region (Exact match usually required)
            if r_region == target_region:
                # Check Type
                is_type_match = False
                if "ikkisi" in r_type_db or "both" in r_type_db:
                    is_type_match = True
                elif r_type_db == target_type:
                    is_type_match = True
                
                if is_type_match:
                     print(f"    ✅ MATCH FOUND! ({r_id})")
                     filtered.append(r)
                else:
                     print(f"    ❌ Type mismatch")
            else:
                 print(f"    ❌ Region mismatch")
                 
        return filtered
        
        for r in all_realtors:
            # Normalize db values
            r_region = str(r.get('region', '')).strip().lower()
            r_type_db = str(r.get('type', '')).strip().lower()
            
            # Check Region (Exact match usually required)
            if r_region == target_region:
                # Check Type
                # Logic:
                # 1. Realtor handles "ikkisi ham" (both) -> matches any request
                # 2. Request is "buy", Realtor is "buy" -> match
                # 3. Request is "rent", Realtor is "rent" -> match
                
                is_type_match = False
                if "ikkisi" in r_type_db or "both" in r_type_db:
                    is_type_match = True
                elif r_type_db == target_type:
                    is_type_match = True
                
                if is_type_match:
                     filtered.append(r)
        return filtered

    def update_balance(self, telegram_id, amount_change):
        if self.is_mock:
            for r in self.mock_data["realtors"]:
                if str(r.get("telegram_id")) == str(telegram_id):
                    r["balance"] = int(r.get("balance", 0)) + amount_change
                    self.save_mock()
                    return True
            return False

        ws = self.get_worksheet("Realtors")
        if not ws: return False
        try:
            cell = ws.find(str(telegram_id))
            if cell:
                current_bal = int(ws.cell(cell.row, 6).value)
                new_bal = current_bal + amount_change
                ws.update_cell(cell.row, 6, new_bal)
                return True
        except Exception as e:
            print(f"Error updating balance: {e}")
        return False

    def add_request(self, request_data):
        req_id = str(int(datetime.now().timestamp()))
        
        if self.is_mock:
            self.mock_data["requests"].append({
                "id": req_id,
                "type": request_data.get('type'),
                "region": request_data.get('region'),
                "rooms": request_data.get('rooms'),
                "price": request_data.get('price'),
                "phone": request_data.get('phone'),
                "status": "New",
                "created_at": str(datetime.now())
            })
            self.save_mock()
            return req_id

        ws = self.get_worksheet("Requests")
        if not ws: return None
        row = [
            req_id,
            request_data.get('type'),
            request_data.get('region'),
            request_data.get('rooms'),
            request_data.get('price'),
            request_data.get('phone'),
            "New",
            str(datetime.now())
        ]
        ws.append_row(row)
        return req_id

    def get_request(self, req_id):
        if self.is_mock:
            for req in self.mock_data["requests"]:
                if str(req.get("id")) == str(req_id):
                    # Return list format: id, type, region, rooms, price, phone, status, created_at
                    return [
                        req["id"], req["type"], req["region"], req["rooms"],
                        req["price"], req["phone"], req["status"], req["created_at"]
                    ]
            return None

        try:
            ws = self.get_worksheet("Requests")
            if not ws: return None
            cell = ws.find(str(req_id))
            if cell:
                return ws.row_values(cell.row)
        except Exception as e:
            print(f"Error getting request {req_id}: {e}")
        return None

    def add_transaction(self, realtor_id, request_id, amount):
        trans_id = str(int(datetime.now().timestamp()))
        if self.is_mock:
            self.mock_data["transactions"].append({
                "id": trans_id,
                "realtor_id": str(realtor_id),
                "request_id": str(request_id),
                "amount": amount,
                "date": str(datetime.now())
            })
            self.save_mock()
            return

        ws = self.get_worksheet("Transactions")
        if not ws: return
        ws.append_row([trans_id, str(realtor_id), str(request_id), amount, str(datetime.now())])

    def get_all_realtors(self):
        if self.is_mock:
            return self.mock_data["realtors"]
            
        now = time.time()
        if "realtors" in self.cache and now - self.cache["realtors"]["time"] < self.cache_expiry:
            return self.cache["realtors"]["data"]

        try:
            ws = self.get_worksheet("Realtors")
            if not ws: return self.cache.get("realtors", {}).get("data", [])
            data = ws.get_all_records()
            self.cache["realtors"] = {"time": now, "data": data}
            return data
        except Exception as e:
            print(f"Error fetching realtors: {e}")
            return self.cache.get("realtors", {}).get("data", [])

    def get_stats(self):
        if self.is_mock:
            return {
                "daily_requests": len(self.mock_data["requests"]),
                "daily_sales": len(self.mock_data["transactions"]),
                "total_realtors": len(self.mock_data["realtors"])
            }
            
        now = time.time()
        if "stats" in self.cache and now - self.cache["stats"]["time"] < self.cache_expiry:
            return self.cache["stats"]["data"]

        try:
            req_ws = self.get_worksheet("Requests")
            trans_ws = self.get_worksheet("Transactions")
            realtors_ws = self.get_worksheet("Realtors")
            
            if not req_ws or not trans_ws or not realtors_ws:
                return self.cache.get("stats", {}).get("data", {"daily_requests": 0, "daily_sales": 0, "total_realtors": 0})

            req_count = len(req_ws.get_all_values()) - 1
            trans_count = len(trans_ws.get_all_values()) - 1
            realtor_count = len(realtors_ws.get_all_values()) - 1
            
            data = {
                "daily_requests": max(0, req_count),
                "daily_sales": max(0, trans_count),
                "total_realtors": max(0, realtor_count)
            }
            self.cache["stats"] = {"time": now, "data": data}
            return data
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return self.cache.get("stats", {}).get("data", {"daily_requests": 0, "daily_sales": 0, "total_realtors": 0})

    def get_pending_requests(self):
        if self.is_mock:
            return [r for r in self.mock_data["requests"] if r.get("status") == "New"]
        
        now = time.time()
        if "pending_reqs" in self.cache and now - self.cache["pending_reqs"]["time"] < self.cache_expiry:
            return self.cache["pending_reqs"]["data"]

        try:
            ws = self.get_worksheet("Requests")
            if not ws: return self.cache.get("pending_reqs", {}).get("data", [])
            
            all_reqs = ws.get_all_records()
            data = [r for r in all_reqs if r.get("status") == "New"]
            self.cache["pending_reqs"] = {"time": now, "data": data}
            return data
        except Exception as e:
            print(f"Error fetching pending requests: {e}")
            return self.cache.get("pending_reqs", {}).get("data", [])

    def update_request_status(self, req_id, status):
        if self.is_mock:
            for r in self.mock_data["requests"]:
                if str(r.get("id")) == str(req_id):
                    r["status"] = status
                    self.save_mock()
                    return True
            return False

        ws = self.get_worksheet("Requests")
        if not ws: return False
        
        try:
            cell = ws.find(str(req_id))
            if cell:
                # Status is 7th column
                # Headers: id, type, region, rooms, price, phone, status, created_at
                ws.update_cell(cell.row, 7, status)
                return True
        except Exception as e:
            print(f"Error updating status: {e}")
        return False

    def update_request_details(self, req_id, region, price, rooms):
        if self.is_mock:
            for r in self.mock_data["requests"]:
                if str(r.get("id")) == str(req_id):
                    r["region"] = region
                    r["price"] = price
                    r["rooms"] = rooms
                    self.save_mock()
                    return True
            return False

        ws = self.get_worksheet("Requests")
        if not ws: return False
        
        try:
            cell = ws.find(str(req_id))
            if cell:
                # Headers: id(1), type(2), region(3), rooms(4), price(5), phone(6), status(7), created_at(8)
                ws.update_cell(cell.row, 3, region)
                ws.update_cell(cell.row, 4, rooms)
                ws.update_cell(cell.row, 5, price)
                return True
        except Exception as e:
            print(f"Error updating details: {e}")
        return False

db = GoogleSheet()
