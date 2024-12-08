{
    'name': 'HR Job Offering',
    'version': '14.0.1.0.0',
    'category': 'Human Resources/Recruitment',
    'summary': 'Adds Job Offering',
    'author': "Mohamed Saber",
    'license': 'AGPL-3',
    'depends': [
        'hr_recruitment','mail','surgi_hr_payroll','surgi_recruitment_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/hr_applicant_view.xml',
        'views/hr_job_offer_view.xml',
        'report/job_offer_template_report.xml',
        'data/mail_data.xml',
    ],
    'installable': True,
}
