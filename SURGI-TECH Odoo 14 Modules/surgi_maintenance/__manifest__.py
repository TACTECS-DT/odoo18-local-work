# -*- coding: utf-8 -*-
{
    'name': "surgi_maintenance",

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
    'depends': ['base','product','hr','crm','sale','product_warranty_management'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
        'security/maintenance_security.xml',

        'data/main_code_seq.xml',
        'views/product_temp.xml',
        'views/views.xml',
        'views/product_spl.xml',
        'views/form_p_d.xml',
        'views/form_p_repair.xml',
        'views/form_p_install.xml',
        'views/form_final_install.xml',
        'views/form_visit.xml',
        'reports/report.xml',
        'reports/report_repair.xml',
        'reports/install_report.xml',
        'reports/final_install_report.xml',
        'reports/Visit_report.xml',
        'views/sale_order_views.xml',
        'views/product_operationg.xml',
        'views/product_occup.xml',
        'views/mainta_inform.xml',

        'views/product_warranty_management.xml',
        'views/warranty.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
