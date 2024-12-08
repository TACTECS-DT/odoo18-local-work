# -*- coding: utf-8 -*-
{
    'name': "Eg-Invoice",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ahmed Abd Al-Aziz Abd Al-Hadi",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_edi','sale','sale_management','stock','surgi_invoice_print','surgi_operation'],
'external_dependencies': {
        'python': ['requests','dateutil']
    },
    # always loaded
    'data': [
         'security/ir.model.access.csv',
         'security/secure.xml',
       # 'views/views.xml',
        'views/templates.xml',
        'views/account_move.xml',
        'views/product_template.xml',
       'views/view_tax.xml',
        'views/res_company.xml',
        'views/res_partener.xml',
        'views/assets.xml',
        'views/egtaxonline.xml',
        'views/currency.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'qweb': [
    'static/xml/canceldeletebuttons.xml'
],
'installable': True,
    #'post_init_hook': '_update_taxes',
}
