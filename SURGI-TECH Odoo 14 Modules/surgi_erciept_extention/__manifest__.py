# -*- coding: utf-8 -*-
{
    'name': "surgi_erciept_extention",

    'summary': """
        Surgi Modefication For Erciept""",

    'description': """
       Surgi Modefication For Erciept
    """,

    'author': "Ahmed Abd Al Aziz",
    'website': "https://www.linkedin.com/in/ahmed-gawad/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base','eta_ereceipt_integration'
        
    ],



    # always loaded
    'data': [
        # 'security/ess_security.xml',
        # 'security/ir.model.access.csv',
      'security/security.xml',
        'views/view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
