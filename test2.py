from app_init import db, Distributer, Supplier_password, app, Climat
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import random

with app.app_context():
    start_dat_1 = "2025-06-12"
    start_1 = datetime.strptime(start_dat_1, '%Y-%m-%d').date()

    now = datetime.now().date()
    print(now, start_1)
    places = ['Участок калибровки', 'Зона хранения комплектующих']
    times = [f'8:15:{random.randint(12,53)}', f'14:15:{random.randint(9,55)}']
    while start_1 <= now:
        for time in times:
            for place in places:
                add_1 = Climat(day=start_1, time=time,
                               temperature=round(random.uniform(20.121, 24.965), 2), humidity=round(random.uniform(48.1, 62.2), 2),
                               place=place)

                db.session.add(add_1)
                db.session.commit()
            print(start_1)

        start_1 = start_1 + timedelta(days=1)
