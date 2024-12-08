# -*- coding: utf-8 -*-
{
    'name': 'Employee Verification',
    'version': '14.0.1.0.0',
    'summary': """Verify the background details of an Employee """,
    'description': 'Manage the employees background verification Process employee varification ',
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base', 'hr', 'hr_recruitment', 'mail', 'hr_employee_info', 'contacts', 'portal', 'website'],
    'data': [
             'security/ir.model.access.csv',
             'views/view_verification.xml',
             'views/res_partner_agent_view.xml',
             'views/agent_portal_templates.xml',
             'data/default_mail.xml'
             ],
}
