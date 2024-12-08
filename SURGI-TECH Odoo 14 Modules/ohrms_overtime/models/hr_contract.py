from odoo import api, models, fields


class HrContractOvertime(models.Model):
    _inherit = 'hr.contract'
    computeovertime=fields.Boolean(string="Set Manually OverTime Wage",default=False)
    over_hour = fields.Monetary('Hour Wage',compute="_get_over_hour")
    over_day = fields.Monetary('Day Wage',compute="_get_over_day")
    compute_over_hour = fields.Monetary('Compute Hour Wage')
    compute_over_day = fields.Monetary('Compute Day Wage')

    def _get_over_hour(self):
        if self.computeovertime:
            self.over_hour=self.compute_over_hour
        else:
            self.over_hour=self.total_salary/270



    def _get_over_day(self):
        if self.computeovertime:
            self.over_day=self.compute_over_day
        else:
            self.over_day=self.total_salary/30


    @api.onchange('computeovertime')
    def computeovertime_change(self):
        if self.computeovertime:
            self.over_hour=0.0
            self.over_day=0.0
            self.compute_over_hour=0
            self.compute_over_day=0
        else:
            self.over_hour=self.total_salary/270
            self.over_day=self.total_salary/30

    @api.onchange('compute_over_hour')
    def compute_over_hour_change(self):
        if self.computeovertime:
            self.over_hour=self.compute_over_hour
        
    @api.onchange('compute_over_day')
    def compute_over_day_change(self):
        if self.computeovertime:
            self.over_day=self.compute_over_day

            


