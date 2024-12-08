# -*- coding: utf-8 -*-
{
    'name': 'Employee History',
    'version': '14.0.1.0.0',
    'summary': """History Of Employees In Your Company""",
    'description': 'Track the History of Employees in your Company',
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['hr', 'hr_contract', 'employee_creation_from_user'],
    'data': ['views/employee_history.xml',
             'views/history_views.xml',
             'security/ir.model.access.csv'
             ],
}
