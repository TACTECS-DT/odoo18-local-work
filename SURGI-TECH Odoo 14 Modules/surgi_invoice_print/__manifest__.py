{
    'name': 'Surgitech invoice change',
    'version': '1.0',
    'author': 'Amhd Abd Al Aziz',
    'category': 'Invoice',
    'description': """
Change Invoice Template
==========================
    """,
    'depends': ['account','sale'],
    'data': [
        'security/invoice_security.xml',
        'views/template.xml',
        'views/invoice.xml',
        'views/credit_note.xml',

    ],
}
