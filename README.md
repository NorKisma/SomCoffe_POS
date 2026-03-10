# SomCoffe POS System ☕ 🚀

> A professional, modular, and secure **Point of Sale** system built for Somali restaurants & cafes.
>
> Built with **Python · Flask · SQLAlchemy · Flask-WTF · Bootstrap 5 · jQuery**

---

## ✨ Key Features

| Module | Description |
|---|---|
| 🛒 **POS Terminal** | Real-time cart, product search, table & customer selection, multi-payment support |
| 📦 **Inventory** | Product & category management with image uploads and stock tracking |
| 🧾 **Order History** | View, edit, and print all orders with status management |
| 👥 **Customers (Macaamiil)** | Customer profiles, credit/debit tracking, order history per customer |
| 👨‍💼 **Employees (Shaqaale)** | Staff directory, position, salary, and status management |
| 📊 **Analytics & Reports** | Revenue charts, top-selling items, status-based breakdowns |
| 🔐 **Role-Based Auth** | Admin / Manager / Staff roles with login, OTP password reset |
| ⚙️ **System Settings** | Restaurant name, currency, tax rate, address — all configurable |
| 💳 **Payment Methods** | Cash · EVC Plus · eDahab · Credit (Deyn) · Pending |
| 🌐 **Hybrid Database** | Switch between local SQLite (offline) and MySQL (online) via `.env` |
| 🛡️ **CSRF Protection** | All forms and AJAX requests protected with Flask-WTF CSRF tokens |

---

## 🏗️ Optimized Professional Project Structure

```text
SomCoffe_POS/
│
├── run.py                          # Entry point — python run.py
├── config.py                       # Configuration loader (reads .env)
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── app/
│   ├── __init__.py                 # App factory (create_app), blueprint & extension registration
│
│   ├── extensions/                 # Flask extension singletons (initialized once, imported everywhere)
│   │   ├── db.py                   # SQLAlchemy instance
│   │   ├── login_manager.py        # Flask-Login
│   │   └── cache.py                # Flask-Caching (performance layer)
│
│   ├── models/                     # SQLAlchemy ORM database schemas
│   │   ├── user.py                 # System users (admin, manager, staff)
│   │   ├── category.py             # Product categories
│   │   ├── product.py              # Menu items & services
│   │   ├── table.py                # Dining tables
│   │   ├── order.py                # Customer orders (header)
│   │   ├── order_item.py           # Order line items
│   │   └── payment.py              # Payment transaction records
│
│   ├── services/                   # Shared business logic (decoupled from routes)
│   │   ├── auth_service.py         # Login validation, password hashing, OTP
│   │   ├── order_service.py        # Order creation, status updates, totals
│   │   ├── payment_service.py      # Payment recording & credit reconciliation
│   │   ├── report_service.py       # Revenue aggregation, chart data
│   │   └── inventory_service.py    # Stock checks, product CRUD, category ops
│
│   ├── blueprints/                 # Feature modules — each is a self-contained Flask Blueprint
│   │
│   │   ├── auth/
│   │   │   ├── __init__.py         # Blueprint definition
│   │   │   ├── routes.py           # Login, logout, forgot password, OTP, reset
│   │   │   ├── forms.py            # WTForms (LoginForm, ForgotPasswordForm, etc.)
│   │   │   ├── services.py         # Auth-specific logic (OTP generation, email send)
│   │   │   └── templates/auth/
│   │   │       ├── login.html
│   │   │       ├── forgot_password.html
│   │   │       ├── verify_otp.html
│   │   │       └── reset_password.html
│   │
│   │   ├── dashboard/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # Home stats: revenue, orders, low-stock alerts
│   │   │   └── templates/dashboard/
│   │   │       └── dashboard.html
│   │
│   │   ├── pos/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # POS page render
│   │   │   ├── api.py              # JSON API: /checkout, /add_customer (AJAX endpoints)
│   │   │   ├── services.py         # Cart processing, order creation, tax calculation
│   │   │   ├── static/
│   │   │   │   ├── js/pos.js       # POS terminal logic (cart, AJAX checkout)
│   │   │   │   └── css/pos.css     # POS-specific styles
│   │   │   └── templates/pos/
│   │   │       └── pos.html
│   │
│   │   ├── products/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # Product & category CRUD
│   │   │   ├── services.py         # Image upload, stock management
│   │   │   └── templates/products/
│   │   │       └── products.html
│   │
│   │   ├── orders/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # Order list, view details, edit status, print
│   │   │   ├── services.py         # Order data assembly, print formatting
│   │   │   └── templates/orders/
│   │   │       └── index.html
│   │
│   │   └── reports/
│   │       ├── __init__.py
│   │       ├── routes.py           # Analytics page
│   │       ├── services.py         # Revenue queries, chart data builders
│   │       └── templates/reports/
│   │           └── index.html
│
│   ├── templates/                  # Global Jinja2 layout (shared across all blueprints)
│   │   └── layout/
│   │       └── base.html           # Master layout: sidebar, navbar, dark mode, CSRF meta
│
│   ├── static/                     # Global frontend assets
│   │   ├── css/
│   │   │   └── style.css           # Global design system (variables, sidebar, cards)
│   │   ├── js/
│   │   │   └── main.js             # Shared JS utilities
│   │   └── images/                 # Static brand images & icons
│
│   ├── database/                   # Database engine configuration
│   │   ├── mysql_db.py             # MySQL connection setup & pool config
│   │   └── sqlite_db.py            # SQLite fallback configuration
│
│   ├── sync/                       # Offline ↔ Cloud synchronization engine
│   │   └── sync_service.py         # Delta sync logic (local → remote)
│
│   ├── automation/                 # Background task scheduling
│   │   ├── scheduler.py            # APScheduler setup & job registration
│   │   └── auto_reports.py         # Automated daily/weekly report generation
│
│   ├── ai/                         # Intelligence & prediction modules
│   │   ├── sales_prediction.py     # Forecast tomorrow's revenue (ML model)
│   │   ├── recommendation.py       # Suggest top-selling combos to cashiers
│   │   └── anomaly_detection.py    # Flag unusually large or suspicious orders
│
│   └── utils/                      # Reusable helpers & security utilities
│       ├── helpers.py              # Date formatting, currency helpers, pagination
│       └── security.py             # Role decorators (@admin_required, @manager_required)
│
└── migrations/                     # Alembic auto-generated database migration scripts
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/NorKisma/SomCoffe_POS.git
cd SomCoffe_POS
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```
Open `.env` and fill in:
```env
SECRET_KEY=your-strong-secret-key-here

# DATABASE MODE
# 'offline'  → uses local SQLite (no internet required)
# 'online'   → uses MySQL/remote database
DB_MODE=offline

# Only required if DB_MODE=online
ONLINE_DATABASE_URL=mysql+pymysql://user:password@localhost:3306/somcoffe

# EMAIL — for OTP password reset
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_app_password_here
```

### 5. Initialize the Database
```bash
flask db upgrade
```

### 6. Create Superadmin Account
```bash
python create_admin.py
```

### 7. (Optional) Seed Sample Data
```bash
python seed_restaurant.py
```

### 8. Run the Application
```bash
python run.py
```
Then open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🔐 User Roles

| Role | Access Level |
|---|---|
| `admin` | Full system access: users, settings, all modules |
| `manager` | POS, orders, customers, employees, inventory, reports |
| `staff` | POS terminal & order history only |

---

## 📦 Core Dependencies

| Package | Purpose |
|---|---|
| `flask` | Web framework |
| `flask-sqlalchemy` | ORM & database management |
| `flask-login` | Session-based authentication |
| `flask-migrate` | Database schema migrations (Alembic) |
| `flask-wtf` | CSRF protection on all forms & AJAX |
| `flask-mail` | Email delivery (OTP password reset) |
| `flask-babel` | Somali (so) / English (en) localization |
| `python-dotenv` | `.env` file loading |
| `pymysql` | MySQL database driver |
| `cryptography` | Secure connection support |

---

## 🤝 Development Guidelines

1. **Thin routes** — business logic belongs in `services/`, not in `blueprints/routes.py`.
2. **Blueprint-level services** — each blueprint can have its own `services.py` for logic used only within that module.
3. **CSRF required everywhere** — every `<form method="POST">` must include `{{ csrf_token() }}`. Every AJAX POST must send the `X-CSRFToken` header (auto-handled via the global jQuery `$.ajaxSetup` in `base.html`).
4. **Per-module assets** — POS-specific JS/CSS lives inside `blueprints/pos/static/`. Shared global styles go in `app/static/css/style.css`.
5. **Responsive-first** — all pages must extend `templates/layout/base.html` and use the premium dark-mode design system.
6. **Role enforcement** — use `@admin_required` / `@manager_required` decorators from `utils/security.py` on protected routes.

---

**Developed with ❤️ for SomCoffe — Mogadishu, Somalia 🇸🇴**
