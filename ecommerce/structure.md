templates/
├── admin/                        # Base admin templates
│   ├── base.html                 # Master dashboard template (sidebar, nav)
│   ├── head.html                 # Dashboard-specific CSS/JS
│   └── navbar.html               # Admin top navigation
│
├── dashboard/                    # Core dashboard sections
│   ├── overview.html             # Analytics summary (sales, users)
│   │
│   ├── products/                 # Product management
│   │   ├── list.html             # Product table (with filters)
│   │   ├── add.html              # Add/edit product form
│   │   └── inventory.html        # Stock level adjustments
│   │
│   ├── orders/                   # Order management
│   │   ├── list.html             # Orders table (status filters)
│   │   └── detail.html           # Order fulfillment view
│   │
│   ├── users/                    # User management
│   │   ├── list.html             # User accounts table
│   │   └── detail.html           # User activity/order history
│   │
│   ├── promotions/               # Discounts/coupons
│   │   ├── coupons.html          # Coupon code management
│   │   └── sales.html            # Flash sale scheduling
│   │
│   └── reports/                  # Analytics
│       ├── sales.html            # Revenue reports (date ranges)
│       └── products.html         # Best-selling items
│
├── partials/                     # Reusable dashboard components
│   ├── charts.html               # Chart.js graphs
│   ├── stats_cards.html          # Summary cards (e.g., "Total Revenue")
│   └── datatable.html            # DataTables.js table template
│
└── 403.html                      # Dashboard-specific error pages
    404.html