# -*- coding: utf-8 -*-
{
    'name': "surgi_help_desk_category",

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
    'depends': ['base','helpdesk','hr','repair','helpdesk_sale','project','maintenance'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/category.xml',
        'views/ticket.xml',
        'views/helpdesk.xml',
        'views/request.xml',
        'views/other_request.xml',
        'views/task.xml',
        # 'views/maintenance_request.xml',
        # 'views/maintenance_team_request.xml',
        # 'views/maintenance_other_request.xml',
        'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
