# -*- coding: utf-8 -*-
{
    'name': "surgi_reports_modules",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','surgi_operation','hr_expense','stock','purchase','sales_team','product','surgi_collection_rep'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/access_group.xml',
        'views/sale.xml',
        'views/operation.xml',
        #'views/customer_invoices.xml',
        #'views/expense.xml',
        #'views/stock_valuation.xml',
        #'views/product_move.xml',
        'views/purchase.xml',
        'views/sales_team.xml',
        'views/product_category.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
