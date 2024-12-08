# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': "Portal Leaves",
    'version': '14.0.1.0',
    'summary': """
        Apply leaves from portal.Easily access to leave and apply leave from portal.User can easily check for leave status.User can delete the leave from portal.Time Off | timeoff | portal timeoff | Portal Time off | HR Time Off | Portal Leave|Portal Leave application|Leave Application|Employee Leave Portal|Portal Leave Apply|Leave Portal.""",
    'description': """
        =>Apply leaves from portal.Easily access to leave and apply leave from portal.
        =>User can easily check for leave status.
        =>User can delete the leave from portal.
    """,
    'category': 'Human Resources/Time Off',
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'company': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'images': ['static/description/banner.jpg'],
    'depends': ['hr_holidays', 'portal','portal_custom'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/portal_templates.xml',
        'views/users.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'currency': 'EUR',
    'price': '40',
}
