{
    'name': 'Surgitech Inventory',
    'version': '10.0.0.1',
    'category': 'Inventory',
    'description': """
Warehouse modifications
==========================
    """,
    'depends': ['stock','stock_account','surgi_product_template','sale'],
    'data': [
        # 'security/stock_security.xml',
        'views/stock_picking_changes_view.xml',
        'views/stock_picking_type_changes_view.xml',
        'views/stock_warehouse_view_changes.xml',
        'views/stock_location_changes_view.xml',
        'views/stock_warehouse_changes_view.xml',
        'views/sale.order.xml',
        'views/stock_quant_change_view.xml',
        'views/stock_move_line_changes.xml',
        'views/inventory_menu.xml',
        'views/branches_view.xml',
        'security/ir.model.access.csv',
        'security/stock_inventory_security.xml',


    ],
}
