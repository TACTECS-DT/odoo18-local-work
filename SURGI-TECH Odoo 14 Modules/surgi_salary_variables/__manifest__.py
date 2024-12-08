# -*- coding: utf-8 -*-
{
    'name': "Surgi Salary Variables",

    'summary': """
    """,



    'description': """
    """,

    'author': "Surgitech",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'hr_payroll','surgi_hr_payroll'],

    # always loaded
    'data': [
        'security/access_groups.xml',
        'views/hr_variable_allowance_request.xml',
        'views/hr_variable_allowance_rule.xml',
        'views/my_request_allowance.xml',
        'views/manager_request_allowance.xml',
        'views/all_request_allowance.xml',
        'views/employee.xml',
        'data/hr_salary_structure.xml',
        'security/ir.model.access.csv'
    ]
}
