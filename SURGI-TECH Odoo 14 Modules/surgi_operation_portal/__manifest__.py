# -*- coding: utf-8 -*-
{
    'name': "surgi_operation_portal",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sales_team','sale','sale_management','account','base', 'portal_custom', 'surgi_operation', 'stock','account_accountant'],

    # always loaded
    'data': [
        'views/assets.xml',

        'security/ir.model.access.csv',
        'views/users.xml',
        'views/portal_share.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/operation_edit.xml',
        'views/operation_new.xml',
        'views/surgi_operation.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'license': 'AGPL-3',}
