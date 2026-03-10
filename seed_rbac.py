"""
seed_rbac.py  —  Create all 4 RBAC test users for SomCoffe POS
Run once:  venv\Scripts\python seed_rbac.py
"""
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions.db import db
from app.models.user import User

app = create_app()

RBAC_USERS = [
    dict(username='admin',   email='admin@somcoffe.com',   role='admin',   password='admin123'),
    dict(username='manager', email='manager@somcoffe.com', role='manager', password='manager123'),
    dict(username='cashier', email='cashier@somcoffe.com', role='cashier', password='cashier123'),
    dict(username='waiter',  email='waiter@somcoffe.com',  role='waiter',  password='waiter123'),
]

with app.app_context():
    created = 0
    for u in RBAC_USERS:
        existing = User.query.filter_by(username=u['username']).first()
        if existing:
            # Update role in case it changed
            existing.role = u['role']
            db.session.commit()
            print(f"  [~] Updated : {u['username']:10} -> role={u['role']}")
        else:
            user = User(username=u['username'], email=u['email'], role=u['role'])
            user.set_password(u['password'])
            db.session.add(user)
            db.session.commit()
            print(f"  [+] Created : {u['username']:10} -> role={u['role']}  pw={u['password']}")
            created += 1

    print(f"\n{'-'*50}")
    print(f"  {created} user(s) created, {len(RBAC_USERS)-created} updated.")
    print(f"{'-'*50}")
    print(f"  Login URL   : http://127.0.0.1:5000/auth/login")
    print(f"  Waiter test : username=waiter   password=waiter123")
    print(f"  Cashier     : username=cashier  password=cashier123")
    print(f"  Manager     : username=manager  password=manager123")
    print(f"  Admin       : username=admin    password=admin123")
    print(f"{'─'*50}\n")
