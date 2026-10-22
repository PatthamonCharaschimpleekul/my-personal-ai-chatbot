import re

def remove_chinese_chars(text: str) -> str:
    """ลบตัวอักษรจีน (Simplified/Traditional) ออกจากข้อความ"""
    if not text:
        return ""
    # ช่วงตัวอักษรจีนพื้นฐาน: 一-鿿
    return re.sub(r'[一-鿿]+', '', text)
