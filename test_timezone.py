#!/usr/bin/env python3
"""
Vaqt zonasi va kun tekshirish testi
"""
from datetime import datetime
from zoneinfo import ZoneInfo

# Tashkent vaqt zonasi
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

def test_timezone():
    """Vaqt zonasi testlari"""
    print("=" * 60)
    print("VAQT ZONASI TESTI")
    print("=" * 60)
    
    # Hozirgi vaqt (serverda)
    server_time = datetime.now()
    print(f"\n1. Server vaqti (timezone yo'q): {server_time}")
    print(f"   Soat: {server_time.hour:02d}:{server_time.minute:02d}")
    print(f"   Kun: {server_time.weekday()} ({get_day_name(server_time.weekday())})")
    
    # Tashkent vaqti
    tashkent_time = datetime.now(TASHKENT_TZ)
    print(f"\n2. Tashkent vaqti: {tashkent_time}")
    print(f"   Soat: {tashkent_time.hour:02d}:{tashkent_time.minute:02d}")
    print(f"   Kun: {tashkent_time.weekday()} ({get_day_name(tashkent_time.weekday())})")
    
    # Farq
    print(f"\n3. Farq:")
    print(f"   Soat farqi: {abs(server_time.hour - tashkent_time.hour)} soat")
    print(f"   Kun farqi: {abs(server_time.weekday() - tashkent_time.weekday())} kun")
    
    # Inglizcha kun nomi
    eng_day = tashkent_time.strftime("%A").lower()
    print(f"\n4. Inglizcha kun nomi: {eng_day}")
    
    # Jadval uchun day_of_week
    day_of_week = tashkent_time.weekday()
    print(f"\n5. Database uchun day_of_week: {day_of_week}")
    print(f"   (0=Dushanba, 1=Seshanba, 2=Chorshanba, 3=Payshanba, 4=Juma, 5=Shanba, 6=Yakshanba)")
    
    print("\n" + "=" * 60)
    print("TEST TUGADI")
    print("=" * 60)

def get_day_name(weekday: int) -> str:
    """Hafta kuni nomini olish"""
    days = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
    return days[weekday]

if __name__ == "__main__":
    test_timezone()
