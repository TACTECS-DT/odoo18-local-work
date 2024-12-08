# -*- coding: utf-8 -*-
{
    'name': 'Official Announcements',
    'version': '14.0.1.0.0',
    'summary': """Managing Official Announcements""",
    'description': 'This module helps you to manage hr official announcements',
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base', 'hr','mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/reward_security.xml',
        'views/hr_announcement_view.xml',
    ],
}
