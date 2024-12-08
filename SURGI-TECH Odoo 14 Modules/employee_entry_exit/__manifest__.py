# -*- coding: utf-8 -*-
{
    'name': 'Employee Checklist',
    'version': '14.0.1.0.1',
    'summary': """Manages Employee's Entry & Exit Process""",
    'description': """This module is used to remembering the employee's entry and exit progress.""",
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base', 'employee_documents_expiration_notify', 'mail', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/employee_form_inherit_view.xml',
        'views/checklist_view.xml',
        'views/employee_check_list_view.xml',
        'views/hr_plan_view.xml',
    ],
}

