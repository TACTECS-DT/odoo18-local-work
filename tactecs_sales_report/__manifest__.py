{
    'name': 'Sales Report',
    'version': '1.0',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['base', 'mail'],
    'data': [
        'views/sales_report_view.xml',
        'security/ir.model.access.csv',
        'views/base_menu.xml',
    ],
    'installable': True,
    'application': True,
}
