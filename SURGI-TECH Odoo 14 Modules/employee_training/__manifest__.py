# -*- coding: utf-8 -*-
{
    'name': "Employee Orientation And Training",
    'version': '14.0.1.1.0',
    'summary': """Employee Orientation and Training Course""",
    'description': 'Complete Employee Orientation and Training Course',
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base', 'hr'],
    'data': [
        'views/orientation_checklist_line.xml',
        'views/employee_orientation.xml',
        'views/orientation_checklist.xml',
        'views/orientation_checklists_request.xml',
        'views/orientation_checklist_sequence.xml',
        'views/orientation_request_mail_template.xml',
        'views/print_pack_certificates_template.xml',
        'views/report.xml',
        'views/employee_training.xml',
        'security/ir.model.access.csv',
    ],
}
