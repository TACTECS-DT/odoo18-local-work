# -*- coding: utf-8 -*-
{
    'name': "surgi_regularity",

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
    'depends': ['base','stock','product','sale','sale_crm','crm','web_tour','mail','purchase'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/reg_security.xml',
        'views/views.xml',
        'views/registrationLic.xml',
        'views/configuration.xml',
        'views/importationPlan.xml',
        'views/scientific_committee.xml',
        'views/appointment.xml',
        'views/certificate.xml',
        'views/check_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
