# -*- coding: utf-8 -*-
{
    'name': 'Loan Accounting',
    'version': '14.0.1.0.0',
    'summary': 'Loan Accounting',
    'description': """
        Create accounting entries for loan requests.
        """,
    'author': "NextEra",
    'company': 'NextEra',
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'employee_loan',
    ],
    'data': [
        'views/hr_loan_config.xml',
        'views/hr_loan_acc.xml',
        'security/show_loan.xml',
    ],
}
