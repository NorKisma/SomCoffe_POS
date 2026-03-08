# SomCoffe POS System ☕ 🚀

Welcome to the **SomCoffe POS** (Point of Sale) Management System! A highly advanced, modular, and AI-powered Point of Sale solution specifically designed to fit the modern needs of local and international restaurants & cafes.

Built carefully with **Python, Flask, SQLAlchemy, JS/Ajax, Bootstrap 5**, and integrated with top-notch intelligence.

---

## ✨ Key Features & Capabilities

### 🛒 1. Responsive Smart POS Terminal
- Sleek, premium dark mode aesthetic (tailored for low-light environments like cafes).
- Lightning-fast **AJAX Cart system**: Add to cart, adjust quantity, and clear out seamlessly.
- Intuitive grid selector for **Categories** and Live Search for **Products**.
- Support for **Physical Items & Services** (Takeaway vs Table orders).

### 💳 2. Somali Local Payment Adapters & Methods
Fully integrated payment method buttons on checkout allowing cashiers to rapidly record:
- **EVC Plus**
- **eDahab**
- **Cash**
- **Banks**
- **Order Only (Pending)**

### 🌐 3. Hybrid Database Capabilities
- Fully functional **Offline Mode** utilizing a local `SQLite` database (guaranteeing 100% uptime without internet).
- Readily scalable **Online Mode** utilizing full cloud setups (MySQL/PostgreSQL) by just switching the `.env` configuration.

### 🤖 4. "AI" & Automation Integrated
- Intelligent **Dashboard Metrics** to show live analytics and insights on revenue, staff, and live table status.
- **Sales Prediction Module**: AI components ready to predict tomorrow's sales output.
- **Fraud/Anomaly Detection**: Logs unusually large or suspicious orders.
- Automated Data Generators (Seed scripts) to populate menus and initial data instantly.

### 🔐 5. Role-Based Security & User Management
- Separate configurations for **SuperAdmins, Cashiers, and Admins**.
- Features restricted natively by route decorators `@admin_required`.
- Ability to Add, Update, Block, and Delete user access.
- Integrated Auth via Flask-Login (Sessions securely handled).

---

## 🏗️ Project Architecture & Structure

```text
SomCoffe_POS/
├── app/
│   ├── ai/            # AI Prediction, Recommendations & Anomaly tracking
│   ├── automation/    # Automated background scheduling & reports
│   ├── blueprints/    # Flask application grouped logic
│   │   ├── auth/          # Login, Registration, OTP, Passwords
│   │   ├── dashboard/     # Home analytics & Feed
│   │   ├── orders/        # Order history, View/Edit statuses
│   │   ├── pos/           # Point of sale cart & terminal UI
│   │   ├── products/      # Inventory management & uploads
│   │   ├── reports/       # Graphical business insights charts
│   │   ├── settings/      # System environment settings
│   │   └── users/         # Staff/Role management
│   ├── extensions/    # Plugins (DB, Login Manager, Mail)
│   ├── models/        # Database Schema mapped definitions
│   ├── services/      # Business logic controllers avoiding fat routes
│   ├── sync/          # Future scope for Local ↔ Cloud Syncing
│   │── templates/     # Jinja2 HTML Layouts (Base, Modals, Forms)
│   │── static/        # CSS (Styling), JS (Interactions), Uploads (Images)
│   └── utils/         # Helper functions & security constraints
│
├── .env               # Secrets & Variables (Not on Github)
├── requirements.txt   # Dependencies
├── run.py             # Server execution file
├── config.py          # App configs loader
└── somcoffe.db        # Offline Database file
```

---

## 🛠️ Installation & Setup (Local Environment)

Follow these steps to securely set up SomCoffe POS on your local Windows/Mac/Linux machine.

### 1) Clone Repository
```bash
git clone https://github.com/NorKisma/SomCoffe_POS.git
cd SomCoffe_POS
```

### 2) Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

### 3) Install Dependencies
```bash
pip install -r requirements.txt
```

### 4) Setup Environment Variables
1. Copy the example environment file: `cp .env.example .env` (or just create `.env`).
2. Fill out standard variables inside the `.env`:
```env
SECRET_KEY=somcoffe-super-secret-123
DB_MODE=offline
# Or DB_MODE=online and set ONLINE_DATABASE_URL=
```

### 5) Initialize Database & Create Admin
Run the following tools provided:
```bash
flask db upgrade
# Create your superadmin login
python create_admin.py
# If you want to seed testing menu categories & products
python seed_restaurant.py
```

### 6) Run Server
```bash
flask run
```
Access the interface visiting **`http://127.0.0.1:5000/`** natively via your web browser.

---

## 🤝 Contribution Guidelines
When updating logic or creating new functions:
1. Try utilizing the `app/services/` layer instead of writing huge code chunks inside `app/blueprints/routes.py`.
2. Ensure you have activated `# type: ignore` to unneeded Pyre Linter errors to maintain clean IDE spaces.
3. Keep the frontend responsive! All styling has been crafted neatly via specific `static/css/` sheets (e.g. `pos.css`, `auth.css`) & Bootstrap 5 templates.

**Developed with ❤️ and Intelligence**
