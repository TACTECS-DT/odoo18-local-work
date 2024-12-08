# -*- coding: utf-8 -*-
{
    'name': 'Employee Documents',
    'version': '14.0.1.0.0',
    'summary': """Manages Employee Documents With Expiry Notifications.""",
    'description': """Manages Employee Related Documents with Expiry Notifications.""",
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_document_view.xml',
        'views/document_type_view.xml',
        'views/hr_document_template.xml',
    ],
}
