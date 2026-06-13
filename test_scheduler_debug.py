"""
Scheduler Debug Skript - Bildirishnoma nima uchun kelmayotganini tekshirish
"""
import asyncio
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

# Tashkent timezone
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

async def debug_scheduler():
    """Scheduler holatini tekshirish"""
    
    print("="*60)
    print("🔍 SCHEDULER DEBUG")
    print("="*60)
    
    # 1. Hozirgi vaqtni tekshirish
    now = datetime.now(TASHKENT_TZ)
    print(f"\n⏰ Hozirgi vaqt (Toshkent):")
    print(f"   📅 Sana: {now.strftime('%Y-%m-%d')}")
    print(f"   🕐 Vaqt: {now.strftime('%H:%M:%S')}")
    print(f"   📆 Kun: {now.weekday()} ({['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba'][now.weekday()]})")
    
    # 2. Database tekshirish
    try:
        import aiosqlite
        from utils.database import DB_PATH
        
        print(f"\n💾 Database: {DB_PATH}")
        
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # Foydalanuvchilar soni
            async with db.execute("SELECT COUNT(*) as count FROM users") as cursor:
                row = await cursor.fetchone()
                user_count = row['count']
                print(f"   👥 Foydalanuvchilar: {user_count} ta")
            
            # Vazifalar soni
            async with db.execute("SELECT COUNT(*) as count FROM tasks WHERE active = 1") as cursor:
                row = await cursor.fetchone()
                task_count = row['count']
                print(f"   📋 Vazifalar: {task_count} ta")
            
            # Jadval soni
            async with db.execute("SELECT COUNT(*) as count FROM schedule WHERE active = 1") as cursor:
                row = await cursor.fetchone()
                schedule_count = row['count']
                print(f"   📅 Jadval: {schedule_count} ta")
            
            # Bugungi jadval
            print(f"\n📅 Bugungi jadval (Day of week = {now.weekday()}):")
            async with db.execute("""
                SELECT s.id, s.user_id, s.start_time, s.end_time, t.task_name, t.category
                FROM schedule s
                LEFT JOIN tasks t ON s.task_id = t.id
                WHERE s.day_of_week = ? AND s.active = 1
                ORDER BY s.start_time
            """, (now.weekday(),)) as cursor:
                rows = await cursor.fetchall()
                if rows:
                    for row in rows:
                        print(f"   🔔 User {row['user_id']}: {row['start_time']}-{row['end_time']} | {row['task_name']} ({row['category']})")
                else:
                    print(f"   ⚠️ Bugun uchun jadval yo'q!")
            
            # Hamma kunlarning jadvali
            print(f"\n📅 Barcha jadvallar:")
            async with db.execute("""
                SELECT s.day_of_week, s.start_time, s.end_time, t.task_name
                FROM schedule s
                LEFT JOIN tasks t ON s.task_id = t.id
                WHERE s.active = 1
                ORDER BY s.day_of_week, s.start_time
            """) as cursor:
                rows = await cursor.fetchall()
                if rows:
                    days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba']
                    current_day = -1
                    for row in rows:
                        if row['day_of_week'] != current_day:
                            current_day = row['day_of_week']
                            print(f"\n   {days[current_day]}:")
                        print(f"      • {row['start_time']}-{row['end_time']}: {row['task_name']}")
                else:
                    print("   ⚠️ Hech qanday jadval yo'q!")
            
    except Exception as e:
        print(f"   ❌ Database xatolik: {e}")
    
    # 3. Scheduler holatini tekshirish (agar ishlab tursa)
    print(f"\n🤖 Bot holati:")
    try:
        from utils.scheduler import scheduler
        
        if scheduler.running:
            print("   ✅ Scheduler ishlayapti")
            
            jobs = scheduler.get_jobs()
            print(f"   📋 Joblar soni: {len(jobs)}")
            
            for job in jobs:
                print(f"      • {job.name} (ID: {job.id})")
                print(f"        ⏰ Keyingi ishga tushish: {job.next_run_time}")
        else:
            print("   ⚠️ Scheduler ishlamayapti!")
    except Exception as e:
        print(f"   ℹ️ Scheduler tekshirib bo'lmadi: {e}")
    
    # 4. Environment variables
    print(f"\n🔑 Environment Variables:")
    print(f"   BOT_TOKEN: {'✅ Mavjud' if os.getenv('BOT_TOKEN') else '❌ Yo\'q'}")
    print(f"   GROQ_API_KEY: {'✅ Mavjud' if os.getenv('GROQ_API_KEY') else '❌ Yo\'q'}")
    
    # 5. Keyingi bildirishnoma vaqti
    print(f"\n⏰ Keyingi bildirishnoma:")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # Bugundan keyingi eng yaqin vaqt
            async with db.execute("""
                SELECT s.start_time, s.end_time, t.task_name, s.user_id
                FROM schedule s
                LEFT JOIN tasks t ON s.task_id = t.id
                WHERE s.day_of_week = ? AND s.active = 1
                ORDER BY s.start_time
            """, (now.weekday(),)) as cursor:
                rows = await cursor.fetchall()
                
                current_time_str = now.strftime('%H:%M')
                found = False
                
                for row in rows:
                    if row['start_time'] >= current_time_str:
                        print(f"   🔔 {row['start_time']} - {row['task_name']} (User: {row['user_id']})")
                        found = True
                        break
                
                if not found:
                    # Ertangi kun
                    tomorrow_day = (now.weekday() + 1) % 7
                    async with db.execute("""
                        SELECT s.start_time, t.task_name
                        FROM schedule s
                        LEFT JOIN tasks t ON s.task_id = t.id
                        WHERE s.day_of_week = ? AND s.active = 1
                        ORDER BY s.start_time
                        LIMIT 1
                    """, (tomorrow_day,)) as cursor2:
                        row2 = await cursor2.fetchone()
                        if row2:
                            tomorrow_name = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba'][tomorrow_day]
                            print(f"   🔔 Ertaga ({tomorrow_name}) {row2['start_time']} - {row2['task_name']}")
                        else:
                            print("   ⚠️ Keyingi bildirishnoma topilmadi")
    except Exception as e:
        print(f"   ❌ Xatolik: {e}")
    
    print("\n" + "="*60)
    print("✅ DEBUG TUGADI")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(debug_scheduler())
