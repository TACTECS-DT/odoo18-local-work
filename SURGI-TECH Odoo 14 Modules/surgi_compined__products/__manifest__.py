# -*- coding: utf-8 -*-
{
    'name': "surgi_compined_Products",

    'summary': """
        Make Compined Products
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Ahmed Abd Al-Aziz",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','product','account','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
       # 'views/compined_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
