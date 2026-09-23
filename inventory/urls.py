from django.urls import path
from . import views

urlpatterns = [

    # ===========================
    # Leadership Section
    # ===========================
    path('leadership/dashboard/', views.leadership_dashboard, name='leadership_dashboard'),
    path('leadership-items/', views.leadership_items_list, name='leadership_items_list'),
path('leadership-transactions/', views.leadership_transactions_list, name='leadership_transactions_list'),
    path('leadership-items/add/', views.leadership_item_add, name='leadership_item_add'),
    path('leadership-items/<int:pk>/edit/', views.leadership_item_edit, name='leadership_item_edit'),
    path('leadership-items/<int:pk>/delete/', views.leadership_item_delete, name='leadership_item_delete'),
    path('leadership-items/<int:pk>/', views.leadership_item_detail, name='leadership_item_detail'),
    path('leadership-items/export/excel/', views.leadership_items_export, name='leadership_items_export'),

    # ===========================
    # Users & Permissions
    # ===========================
    path('users/', views.users_list, name='users_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),

    

    # Dashboard
    path(
        "",
        views.dashboard,
        name="dashboard"
    ),

    # ===========================
    # Products
    # ===========================

    path(
        "products/",
        views.products_list,
        name="products_list"
    ),

    path(
        "products/add/",
        views.add_product,
        name="add_product"
    ),

    path(
        "products/low-stock/",
        views.low_stock_products,
        name="low_stock_products",
    ),

    path(
        "products/<int:pk>/",
        views.product_detail,
        name="product_detail"
    ),

    path(
        "products/<int:pk>/edit/",
        views.edit_product,
        name="edit_product"
    ),

    path(
        "products/<int:pk>/delete/",
        views.delete_product,
        name="delete_product"
    ),


    # ===========================
    # Categories
    # ===========================

    path(
        "categories/",
        views.categories_list,
        name="categories_list"
    ),

    path(
        "categories/add/",
        views.add_category,
        name="add_category"
    ),

    path(
        "categories/<int:pk>/edit/",
        views.edit_category,
        name="edit_category"
    ),

    path(
        "categories/<int:pk>/delete/",
        views.delete_category,
        name="delete_category"
    ),

    # ===========================
    # Colors
    # ===========================

    path(
        "colors/",
        views.colors_list,
        name="colors_list"
    ),

    path(
        "colors/add/",
        views.add_color,
        name="add_color"
    ),

    path(
        "colors/<int:pk>/edit/",
        views.edit_color,
        name="edit_color"
    ),

    path(
        "colors/<int:pk>/delete/",
        views.delete_color,
        name="delete_color"
    ),

    # ===========================
    # Sizes
    # ===========================

    path(
        "sizes/",
        views.sizes_list,
        name="sizes_list"
    ),

    path(
        "sizes/add/",
        views.add_size,
        name="add_size"
    ),

    path(
        "sizes/<int:pk>/edit/",
        views.edit_size,
        name="edit_size"
    ),

    path(
        "sizes/<int:pk>/delete/",
        views.delete_size,
        name="delete_size"
    ),

    # ===========================
    # Inventory Transactions
    # ===========================

    path(
        "transactions/",
        views.transactions_list,
        name="transactions_list"
    ),

    path(
        "transactions/add/",
        views.add_transaction,
        name="add_transaction"
    ),
    
path(
    "reports/warehouse-stock/",
    views.warehouse_stock_report,
    name="warehouse_stock_report",
),
path(
    "reports/partner-statement/",
    views.partner_statement_report,
    name="partner_statement_report",
),
path(
    "reports/profit/",
    views.profit_report,
    name="profit_report",
),
path(
    "reports/inventory/",
    views.inventory_report,
    name="inventory_report",
),
path(
    "activity/",
    views.activity_logs,
    name="activity_logs",
),

    path("management/warehouses/", views.warehouses_list, name="warehouses_list"),
    path("management/warehouses/add/", views.add_warehouse, name="add_warehouse"),
    path("management/warehouses/<int:pk>/edit/", views.edit_warehouse, name="edit_warehouse"),
    path("management/warehouses/<int:pk>/delete/", views.delete_warehouse, name="delete_warehouse"),

    path("management/partners/", views.partners_list, name="partners_list"),
    path("management/partners/add/", views.add_partner, name="add_partner"),
    path("management/partners/<int:pk>/edit/", views.edit_partner, name="edit_partner"),
    path("management/partners/<int:pk>/delete/", views.delete_partner, name="delete_partner"),

    path(
        "settings/",
        views.system_settings,
        name="system_settings",
    ),
    path(
        "settings/import-excel/",
        views.import_stock_excel,
        name="import_stock_excel",
    ),
    path("remote-setup-db/", views.remote_setup, name="remote_setup"),
]