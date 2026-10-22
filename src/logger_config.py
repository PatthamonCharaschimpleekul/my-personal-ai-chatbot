import sys
import os
from loguru import logger

# สร้างโฟลเดอร์ logs ถ้ายังไม่มี
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ตั้งค่า loguru
def setup_logging():
    # ล้างค่าเดิม
    logger.remove()

    # 1. แสดงผลใน Console (สีสันสวยงาม)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    # 2. บันทึกลงไฟล์ (แยกตามวัน)
    logger.add(
        os.path.join(LOG_DIR, "system.log"),
        rotation="1 day",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

# รันการตั้งค่าทันทีที่ import
setup_logging()

# Export logger เพื่อให้ไฟล์อื่นใช้ได้
__all__ = ["logger"]
