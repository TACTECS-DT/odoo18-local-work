# -*- coding: utf-8 -*-
{
    'name': "surgi-dummy-Items",

    'summary': """
       Sock Picking dummy items""",

    'description': """
        Sock Picking dummy items
    """,

    'author': "Ahmed Abd Al Aziz",
    #'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock_lot_scan','stock_scan_frontend'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/user_groups.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
