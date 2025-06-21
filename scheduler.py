
from tinydb import TinyDB, Query
from datetime import datetime, timedelta

db = TinyDB('users.json')
User = Query()
now = datetime.utcnow()

users = db.all()
updated = 0

for user in users:
    last_claim = datetime.strptime(user.get('last_claim', '2000-01-01'), '%Y-%m-%d %H:%M:%S.%f')
    if (now - last_claim) >= timedelta(hours=24):
        meter = user.get('meter', 0)
        if meter > 0:
            new_points = user.get('points', 0) + meter
            db.update({'points': new_points, 'last_claim': str(now)}, User.id == user['id'])
            updated += 1

print(f"✅ تم تحديث {updated} مستخدم(ين) بتاريخ {now}")
