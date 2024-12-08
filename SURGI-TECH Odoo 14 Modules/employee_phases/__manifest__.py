# -*- coding: utf-8 -*-
{
    'name': 'Employee Phases',
    'version': '14.0.1.0.0',
    'summary': """Manages Employee Phases""",
    'description': """This module is used to tracking employee's different Phases.""",
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_phases_view.xml',
    ],
}


