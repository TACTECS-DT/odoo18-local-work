# -*- coding: utf-8 -*-
{
    'name': 'Employee Info',
    'version': '14.0.1.0.0',
    'summary': """Adding Advanced Fields In Employee""",
    'description': 'This module helps you to add more information in employee records.',
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base', 'hr', 'mail', 'hr_gamification', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/contract_days_view.xml',
        'views/updation_config.xml',
        'views/hr_employee_view.xml',
        'views/hr_notification.xml',
    ],
}
