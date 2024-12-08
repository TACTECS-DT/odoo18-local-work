# -*- coding: utf-8 -*-
{
    'name': 'Employee Penalty',
    'version': '14.0.1.0.0',
    'summary': """Employee Penalty""",
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base', 'mail', 'employee_creation_from_user'],
    'data': ['views/disciplinary_action.xml',
             'views/disciplinary_sequence.xml',
             'views/category_view.xml',
             'security/ir.model.access.csv',
             'security/security.xml'],
}
