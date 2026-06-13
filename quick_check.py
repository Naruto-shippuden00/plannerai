"""
TEZKOR TEKSHIRISH - Bildirishnoma muammosini topish
"""
import asyncio
import aiosqlite
from datetime import datetime
from zoneinfo import ZoneInfo

TASHKENT_TZ = ZoneInfo("Asia/Tashkent")
DB_PATH = "data/productivity.db"

async def quick_check():
    print("\n" + "="*70)
    print("🔍 TEZKOR TEKSHIRISH - BILDIRISHNOMA")
    print("="*70)
    
    # 1. Hozirgi vaqt
    now = datetime.now(TASHKENT_TZ)
    print(f"\n⏰ HOZIRGI VAQT:")
    print(f"   📅 Sana: {now.strftime('%Y-%m-%d')}")
    print(f"   🕐 Vaqt: {now.strftime('%H:%M:%S')}")
    print(f"   📆 Kun: {['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba'][now.weekday()]}")
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # 2. Users
            print(f"\n👥 FOYDALANUVCHILAR:")
            async with db.execute("SELECT user_id, username, full_name FROM users") as cursor:
                users = await cursor.fetchall()
                if users:
                    for user in users:
                        print(f"   • ID: {user['user_id']} | @{user['username']} | {user['full_name']}")
                else:
                    print("   ❌ HECH KIM YO'Q! /start bosing!")
            
            # 3. Tasks
            print(f"\n📋 VAZIFALAR (active):")
            async with db.execute("SELECT id, task_name, category FROM tasks WHERE active = 1") as cursor:
                tasks = await cursor.fetchall()
                if tasks:
                    for task in tasks:
                        print(f"   • ID {task['id']}: {task['task_name']} ({task['category']})")
                else:
                    print("   ❌ VAZIFALAR YO'Q! /tasks bosing!")
            
            # 4. Schedule - HAMMA KUNLAR
            print(f"\n📅 JADVAL (hamma kunlar):")
            days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba']
            
            async with db.execute("""
                SELECT s.day_of_week, s.start_time, s.end_time, s.task_id, t.task_name, s.user_id, s.active
                FROM schedule s
                LEFT JOIN tasks t ON s.task_id = t.id
                ORDER BY s.day_of_week, s.start_time
            """) as cursor:
                all_schedules = await cursor.fetchall()
                
                if all_schedules:
                    current_day = -1
                    for sched in all_schedules:
                        if sched['day_of_week'] != current_day:
                            current_day = sched['day_of_week']
                            print(f"\n   📆 {days[current_day]} (day_of_week={current_day}):")
                        
                        active_mark = "✅" if sched['active'] == 1 else "❌ INACTIVE"
                        print(f"      {active_mark} {sched['start_time']}-{sched['end_time']}: {sched['task_name']} (User: {sched['user_id']}, Task ID: {sched['task_id']})")
                else:
                    print("   ❌ JADVAL YO'Q! /schedule bosing!")
            
            # 5. BUGUNGI JADVAL
            print(f"\n🔔 BUGUNGI JADVAL ({days[now.weekday()]}, day_of_week={now.weekday()}):")
            async with db.execute("""
                SELECT s.start_time, s.end_time, t.task_name, s.user_id, s.task_id, s.active
                FROM schedule s
                LEFT JOIN tasks t ON s.task_id = t.id
                WHERE s.day_of_week = ?
                ORDER BY s.start_time
            """, (now.weekday(),)) as cursor:
                today_schedules = await cursor.fetchall()
                
                if today_schedules:
                    current_time = now.strftime('%H:%M')
                    print(f"   ⏰ Hozirgi vaqt: {current_time}")
                    print()
                    
                    for sched in today_schedules:
                        active_mark = "✅" if sched['active'] == 1 else "❌"
                        
                        # Vaqt taqqoslash
                        if sched['start_time'] == current_time:
                            print(f"      🔥 HOZIR! {active_mark} {sched['start_time']}-{sched['end_time']}: {sched['task_name']}")
                        elif sched['start_time'] > current_time:
                            print(f"      ⏰ Keyingi: {active_mark} {sched['start_time']}-{sched['end_time']}: {sched['task_name']}")
                        else:
                            print(f"      ⏱ O'tgan: {active_mark} {sched['start_time']}-{sched['end_time']}: {sched['task_name']}")
                else:
                    print(f"   ❌ BUGUN JADVAL YO'Q!")
                    print(f"   💡 Iltimos boshqa kunga jadval qo'shing yoki bugun uchun yangi jadval tuzing!")
            
            # 6. Keyingi bildirishnoma
            print(f"\n⏰ KEYINGI BILDIRISHNOMA:")
            
            # Bugundan keyingi
            current_time = now.strftime('%H:%M')
            found = False
            
            async with db.execute("""
                SELECT s.start_time, s.end_time, t.task_name, s.user_id
                FROM schedule s
                LEFT JOIN tasks t ON s.task_id = t.id
                WHERE s.day_of_week = ? AND s.start_time > ? AND s.active = 1
                ORDER BY s.start_time
                LIMIT 1
            """, (now.weekday(), current_time)) as cursor:
                next_today = await cursor.fetchone()
                if next_today:
                    print(f"   🔔 Bugun {next_today['start_time']} - {next_today['task_name']} (User: {next_today['user_id']})")
                    found = True
            
            if not found:
                # Keyingi kun
                for i in range(1, 8):
                    next_day = (now.weekday() + i) % 7
                    async with db.execute("""
                        SELECT s.start_time, t.task_name
                        FROM schedule s
                        LEFT JOIN tasks t ON s.task_id = t.id
                        WHERE s.day_of_week = ? AND s.active = 1
                        ORDER BY s.start_time
                        LIMIT 1
                    """, (next_day,)) as cursor:
                        next_sched = await cursor.fetchone()
                        if next_sched:
                            print(f"   🔔 {days[next_day]} {next_sched['start_time']} - {next_sched['task_name']}")
                            break
                else:
                    print("   ❌ KEYINGI BILDIRISHNOMA YO'Q!")
            
    except Exception as e:
        print(f"\n❌ XATOLIK: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ TEKSHIRISH TUGADI")
    print("="*70)
    print("\n💡 XULOSA:")
    print("   1. Agar 'HECH KIM YO'Q' bo'lsa → Botda /start bosing")
    print("   2. Agar 'VAZIFALAR YO'Q' bo'lsa → /tasks bosing")
    print("   3. Agar 'JADVAL YO'Q' bo'lsa → /schedule bosing")
    print("   4. Agar jadval bor lekin 'BUGUN JADVAL YO'Q' bo'lsa → Bugun uchun jadval qo'shing!")
    print("   5. Agar hammasi bor lekin bildirishnoma yo'q bo'lsa → Bot loglarini yuboring!\n")

if __name__ == "__main__":
    asyncio.run(quick_check())
