# -*- coding: utf-8 -*-

{
    'name': 'Leave Multi-Level Approval',
    'version': '14.0.1.0.0',
    'summary': """Multilevel Approval for Leaves""",
    'description': 'Multilevel Approval for Leaves, leave approval, multiple leave approvers, leave, approval',
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base_setup', 'hr_holidays'],
    'data': [
        'views/leave_request.xml',
        'security/ir.model.access.csv',
        'security/security.xml'
    ],
}
