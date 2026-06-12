#!/usr/bin/env python3
"""
Bildirishnomani test qilish uchun script
Vazifani 5 daqiqadan keyinga o'rnatadi
"""
import sqlite3
from datetime import datetime, timedelta
import sys

def setup_test_reminder(minutes_from_now=5):
    """
    Vazifani N daqiqadan keyinga sozlash
    """
    # Hozirgi vaqt
    now = datetime.now()
    
    # N daqiqadan keyingi vaqt
    start_time = (now + timedelta(minutes=minutes_from_now)).strftime("%H:%M")
    end_time = (now + timedelta(minutes=minutes_from_now + 60)).strftime("%H:%M")  # +1 soat
    day_of_week = now.weekday()
    
    # Kun nomlari
    day_names = {
        0: "Dushanba",
        1: "Seshanba",
        2: "Chorshanba",
        3: "Payshanba",
        4: "Juma",
        5: "Shanba",
        6: "Yakshanba"
    }
    
    print("\n" + "="*50)
    print("🧪 BILDIRISHNOMA TESTINI SOZLASH")
    print("="*50 + "\n")
    
    print(f"⏰ Hozirgi vaqt: {now.strftime('%H:%M')}")
    print(f"📅 Kun: {day_names[day_of_week]}")
    print(f"⏱ Test vaqti: {start_time} - {end_time}")
    print(f"⏳ Kutish vaqti: {minutes_from_now} daqiqa\n")
    
    try:
        # Database'ga ulanish
        conn = sqlite3.connect('data/productivity.db')
        cursor = conn.cursor()
        
        # Foydalanuvchilarni olish
        cursor.execute("SELECT user_id, username, full_name FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("❌ Hech qanday foydalanuvchi topilmadi!")
            print("💡 Avval botda /start yuboring va qayta urinib ko'ring.\n")
            return
        
        print(f"👥 Topilgan foydalanuvchilar: {len(users)}\n")
        
        for user_id, username, full_name in users:
            print(f"\n🔧 Sozlanmoqda: {full_name or username} (ID: {user_id})")
            
            # Bu foydalanuvchining vazifalarini olish
            cursor.execute("""
                SELECT id, task_name, category, duration_minutes 
                FROM tasks 
                WHERE user_id = ? AND active = 1
                LIMIT 1
            """, (user_id,))
            
            task = cursor.fetchone()
            
            if not task:
                print(f"  ⚠️  Vazifa topilmadi. Avval vazifa qo'shing!")
                continue
            
            task_id, task_name, category, duration = task
            print(f"  📝 Vazifa: {task_name}")
            print(f"  📂 Kategoriya: {category}")
            print(f"  ⏱  Davomiyligi: {duration} min")
            
            # Jadvalda bu vazifa bormi?
            cursor.execute("""
                SELECT id FROM schedule 
                WHERE user_id = ? AND task_id = ?
            """, (user_id, task_id))
            
            schedule_item = cursor.fetchone()
            
            if schedule_item:
                # Mavjud jadvalni yangilash
                schedule_id = schedule_item[0]
                cursor.execute("""
                    UPDATE schedule 
                    SET day_of_week = ?,
                        start_time = ?,
                        end_time = ?,
                        active = 1
                    WHERE id = ?
                """, (day_of_week, start_time, end_time, schedule_id))
                print(f"  ✅ Jadval yangilandi (ID: {schedule_id})")
            else:
                # Yangi jadval qo'shish
                cursor.execute("""
                    INSERT INTO schedule (user_id, task_id, day_of_week, start_time, end_time, active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (user_id, task_id, day_of_week, start_time, end_time))
                print(f"  ✅ Yangi jadval qo'shildi")
        
        # O'zgarishlarni saqlash
        conn.commit()
        conn.close()
        
        print("\n" + "="*50)
        print("✅ SOZLASH MUVAFFAQIYATLI!")
        print("="*50 + "\n")
        
        print(f"🎯 BILDIRISHNOMA {start_time} DA KELADI!")
        print(f"⏳ {minutes_from_now} DAQIQA KUTISH...\n")
        
        print("📱 Telegram'da botni ochib qoying va kutasiz!\n")
        
        print("📋 KUTILGAN NATIJA:")
        print(f"   1. {start_time} da birinchi bildirishnoma")
        print(f"   2. Har 5 daqiqada eslatma (rasm yubormasangiz)")
        print(f"   3. Rasm yuboring - bildirishnomalar to'xtaydi")
        print(f"   4. Pomodoro timer boshlanadi\n")
        
    except sqlite3.Error as e:
        print(f"\n❌ Database xatosi: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Xatolik: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    # Command line argumentlar
    if len(sys.argv) > 1:
        try:
            minutes = int(sys.argv[1])
            if minutes < 1 or minutes > 60:
                print("⚠️  Daqiqalar 1 dan 60 gacha bo'lishi kerak!")
                sys.exit(1)
            setup_test_reminder(minutes)
        except ValueError:
            print("❌ Noto'g'ri format! Faqat raqam kiriting.")
            print("Misol: python test_reminder.py 5")
            sys.exit(1)
    else:
        # Default - 5 daqiqa
        setup_test_reminder(5)
