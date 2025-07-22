from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from pharmbook_app import login, db
from uuid import uuid4
from enum import Enum
from datetime import datetime

class StatusEnum(Enum):
    AVAILABLE = 'available'
    NON_AVAILABLE = 'non-available'
    SPECIAL_ORDER = 'Special Order'
    PRE_ORDER = 'Pre-Order'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Base Product Class
class Product(db.Model):
    __abstract__ = True  # ทำให้เป็น abstract class ไม่สร้างตารางใน database
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    image = db.Column(db.String(256))
    name = db.Column(db.String(256))
    detail = db.Column(db.Text)
    price_thb = db.Column(db.Float)  # เปลี่ยนจาก String เป็น Float เพื่อการคำนวณ
    unit = db.Column(db.String(64))
    status = db.Column(db.Enum(StatusEnum))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # แก้ไขชื่อฟิลด์ให้สอดคล้อง
    
    @property
    def price_btc(self):
        """คำนวณราคา BTC จาก price_thb โดยใช้ API"""
        from .crypto_api import get_current_btc_rate  # สะกดถูกต้องเป็น crypto_api
        btc_rate = get_current_btc_rate()
        return round(self.price_thb / btc_rate, 8) if btc_rate else 0  # ปัดเศษเป็นทศนิยม 8 ตำแหน่ง
    
    @property
    def price_trend(self):
        """ตรวจสอบแนวโน้มราคา BTC จาก API"""
        from .crypto_api import get_btc_trend
        return get_btc_trend()

# Food Class สืบทอดจาก Product
class Food(Product):
    __tablename__ = 'foods'
    
    # สามารถเพิ่มฟิลด์เฉพาะของอาหารได้ที่นี่
    nutrition_facts = db.Column(db.Text)
    expiry_date = db.Column(db.Date)

# Medicine Class สืบทอดจาก Product
class Medicine(Product):
    __tablename__ = 'medicines'
    
    # สามารถเพิ่มฟิลด์เฉพาะของยาได้ที่นี่
    dosage = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    manufacturer = db.Column(db.String(256))

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))