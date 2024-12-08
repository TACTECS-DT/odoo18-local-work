# -*- coding: utf-8 -*-
{
    'name': "portal_custom",

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
    'depends': ['base', 'website', 'portal','surgi_attendance_sheet','surgi_evaluation','surgi_employee_custom'],

    # always loaded
    'data': [

        'views/frontend/website_dashboard_assets.xml',
        'views/frontend/website_dashboard_views.xml',
        'views/frontend/my_profile.xml',
        'views/backend/users.xml',
        'views/frontend/access_dined.xml',
        'views/backend/backend_assets.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
