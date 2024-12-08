# See LICENSE file for full copyright and licensing details.

{
    "name": "HR Applicant",
    "version": "14.0.0.1.0",
    "summary": "Applicant and Employee Subsections, Training",
    "author": "NextEra",
    "depends": ["hr_recruitment"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/select_training_view.xml",
        "report/report_view.xml",
        "views/hr_recruitment_views.xml",
        "views/hr_recruitment_employee_views.xml",
        "views/training_views.xml",
        "views/applicant_profile_report_view.xml",
    ],
}
