# -*- coding: utf-8 -*-
{
    'name': 'Loan Management',
    'version': '14.0.1.1.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of Employees.
        """,
    'author': "NextEra",
    'company': 'NextEra',
    'depends': [
        'base', 'hr_payroll', 'hr', 'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'views/hr_loan.xml',
        'views/manager_loan.xml',
        'views/all_request_loan.xml',
        'views/hr_payroll.xml',
    ],
}
