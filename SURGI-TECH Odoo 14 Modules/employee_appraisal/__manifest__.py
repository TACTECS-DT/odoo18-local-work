# -*- coding: utf-8 -*-
{
    'name': "Employee Appraisal",
    'version': '14.0.1.0.0',
    'summary': """appraisal plans""",
    'description': """appraisal plans""",
    'author': 'NextEra',
    'company': 'NextEra',
    'depends': ['base', 'hr', 'survey'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_appraisal_security.xml',
        'views/hr_appraisal_survey_views.xml',
        'views/hr_appraisal_form_view.xml',
        'data/hr_appraisal_stages.xml'
    ],
}
