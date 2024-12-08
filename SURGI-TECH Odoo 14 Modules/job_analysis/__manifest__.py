# -*- coding: utf-8 -*-
{
    'name': "Job Analysis",
    'summary': """Job Analysis Management & Operations""",
    'description': """Job Analysis Management & Operations""",
    'author': "Mohamed Saber",
    'category': 'Job Analysis',
    'version': '0.1',
    'license': 'AGPL-3',
    # any module necessary for this one to work correctly

    'depends': ['base','mail','hr','portal','surgi_hr_employee','surgi_hr_payroll'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/job_analysis_batch.xml',
        'views/base_view.xml',
        'views/answer_view.xml',
        'views/collection_view.xml',
        'views/job_position.xml',
        'views/manager_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
