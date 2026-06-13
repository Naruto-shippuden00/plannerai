"""
Scheduler debug - Jadval va eslatmalarni tekshirish
"""
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.database import init_db, get_all_users, get_user_schedule_for_today, get_user_tasks

TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

async def check_schedule_debug():
    """Jadval va vazifalarni tekshirish"""
    print("=" * 60)
    print("🔍 SCHEDULER DEBUG - JADVAL TEKSHIRUVI")
    print("=" * 60)
    
    # Database init
    await init_db()
    
    # Hozirgi vaqt
    current_time = datetime.now(TASHKENT_TZ)
    current_day = current_time.weekday()
    day_names = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
    
    print(f"\n⏰ Hozirgi vaqt: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Kun: {day_names[current_day]} (day_of_week={current_day})")
    print(f"🕐 Soat:Daqiqa: {current_time.hour:02d}:{current_time.minute:02d}")
    
    # Barcha foydalanuvchilarni olish
    users = await get_all_users()
    print(f"\n👥 Jami foydalanuvchilar: {len(users)}")
    
    for user in users:
        user_id = user['user_id']
        username = user.get('username', 'Unknown')
        
        print(f"\n{'='*60}")
        print(f"👤 User: {username} (ID: {user_id})")
        print(f"{'='*60}")
        
        # Vazifalar
        tasks = await get_user_tasks(user_id)
        print(f"\n📝 Vazifalar: {len(tasks)} ta")
        for task in tasks:
            status = "✅ Aktiv" if task['active'] == 1 else "❌ O'chirilgan"
            print(f"  • {task['task_name']} - {status}")
            print(f"    ID: {task['id']}, Kategoriya: {task['category']}, Davomiylik: {task['duration_minutes']} min")
        
        # Bugungi jadval
        schedule = await get_user_schedule_for_today(user_id, current_day)
        print(f"\n📅 {day_names[current_day]} jadval: {len(schedule)} ta vazifa")
        
        if not schedule:
            print("  ⚠️ Bugun uchun jadval yo'q!")
        else:
            for idx, item in enumerate(schedule, 1):
                start_time = item.get('start_time', 'N/A')
                end_time = item.get('end_time', 'N/A')
                task_name = item.get('task_name', 'Unknown')
                task_id = item.get('task_id', 'N/A')
                
                print(f"\n  {idx}. {task_name}")
                print(f"     ⏰ Vaqt: {start_time} - {end_time}")
                print(f"     🆔 Task ID: {task_id}")
                print(f"     🔍 Schedule ID: {item.get('id', 'N/A')}")
                
                # Vaqt tekshiruvi
                try:
                    item_hour, item_minute = map(int, start_time.split(':'))
                    if item_hour == current_time.hour and item_minute == current_time.minute:
                        print(f"     🔔 ✅ HOZIR VAQTI! Bildirishnoma yuborilishi kerak!")
                    elif item_hour < current_time.hour or (item_hour == current_time.hour and item_minute < current_time.minute):
                        print(f"     ⏮️ O'tib ketgan")
                    else:
                        print(f"     ⏭️ Kelgusi vaqt")
                except Exception as e:
                    print(f"     ❌ Vaqt parse xatosi: {e}")
        
        # Butun haftalik jadval
        print(f"\n📊 Haftalik to'liq jadval:")
        for day_num in range(7):
            day_schedule = await get_user_schedule_for_today(user_id, day_num)
            marker = "👉" if day_num == current_day else "  "
            print(f"{marker} {day_names[day_num]}: {len(day_schedule)} ta vazifa")
    
    print(f"\n{'='*60}")
    print("✅ Tekshirish tugadi!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(check_schedule_debug())
