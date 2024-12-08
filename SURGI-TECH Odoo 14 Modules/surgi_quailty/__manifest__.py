# -*- coding: utf-8 -*-
{
    'name': "surgi_quailty",

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
    'depends': ['base','surgi_operation','stock','purchase','surgi_serial_number'],

    # always loaded
    'data': [
        'security/quality_security.xml',
        'views/view_quality_operations_coordinator.xml',
        'views/stock_transfer.xml',
        'views/inventory_report.xml',
        'views/lot_serial_num.xml',
        'views/opration_quality.xml',
        'views/purches.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
