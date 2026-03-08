# SomCoffe_POS
SomCoffe_POS/
│
├── run.py
├── config.py
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│
│   ├── extensions/
│   │   ├── db.py
│   │   ├── login_manager.py
│   │   └── cache.py
│
│   ├── models/
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── table.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   └── payment.py
│
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   ├── report_service.py
│   │   └── inventory_service.py
│
│   ├── blueprints/
│   │
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   ├── services.py
│   │   │   └── templates/auth/login.html
│   │
│   │   ├── dashboard/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── templates/dashboard/dashboard.html
│   │
│   │   ├── pos/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── api.py
│   │   │   ├── services.py
│   │   │   ├── static/
│   │   │   │   ├── js/pos.js
│   │   │   │   └── css/pos.css
│   │   │   └── templates/pos/pos.html
│   │
│   │   ├── products/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── services.py
│   │   │   └── templates/products/products.html
│   │
│   │   ├── orders/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── services.py
│   │   │   └── templates/orders/orders.html
│   │
│   │   └── reports/
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       ├── services.py
│   │       └── templates/reports/sales.html
│
│   ├── templates/
│   │   └── layout/base.html
│
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── images/
│
│   ├── database/
│   │   ├── mysql_db.py
│   │   └── sqlite_db.py
│
│   ├── sync/
│   │   └── sync_service.py
│
│   ├── automation/
│   │   ├── scheduler.py
│   │   └── auto_reports.py
│
│   ├── ai/
│   │   ├── sales_prediction.py
│   │   ├── recommendation.py
│   │   └── anomaly_detection.py
│
│   └── utils/
│       ├── helpers.py
│       └── security.py
│
└── migrations/
