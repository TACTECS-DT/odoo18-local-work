# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class ResUser(models.Model):
    _inherit = 'res.users'

    evaluation_portal_access = fields.Boolean('Evaluation portal access')

class valuationnherit(models.Model):
    _inherit = 'evaluation.evaluation'

    @api.model
    def edit_self_evaluation_portal_record(self, values):
        evaluation_record = self.browse(values.get('evaluation_id'))

        # Update the core competencies
        core_values = values.get('core_competencies', [])
        for core_val in core_values:
            core_record = self.env['core2.competencies2'].browse(core_val.get('id'))
            core_record.write({
                'employee_self_assessment': core_val.get('employee_self_assessment'),
                # Include other fields as needed
            })

        # Update the function competencies
        function_values = values.get('function_comp', [])
        for function_val in function_values:
            function_record = self.env['function2.competencies2'].browse(function_val.get('id'))
            function_record.write({
                'employee_self_assessment': function_val.get('employee_self_assessment'),
                # Include other fields as needed
            })

        # Update the KPI competencies
        kpi_values = values.get('employee_kpi', [])
        for kpi_val in kpi_values:
            kpi_record = self.env['kpi.competencies'].browse(kpi_val.get('id'))
            kpi_record.write({
                'employee_self_assessment': kpi_val.get('employee_self_assessment'),
                # Include other fields as needed
            })

        # Update any other fields in the evaluation record if needed

        return True
