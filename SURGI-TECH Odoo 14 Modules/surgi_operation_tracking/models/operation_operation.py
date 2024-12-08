from odoo import models, fields, api,_

from datetime import datetime

class OperationOperationdate(models.Model):
    _inherit = 'operation.operation'


    started_op_date = fields.Char(string="Strat Operation Date",readonly=True)
    started_op = fields.Boolean(readonly=True,invisible=1)
    ended_op = fields.Boolean(readonly=True,invisible=1)

    ended_op_date = fields.Char(string="End Operation Date",readonly=True)


    def action_start_operation_date(self):
        now = datetime.now()
        # self.started_op_date=datetime.now(),
        self.started_op_date = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.started_op =True
    def action_end_operation_date(self):
        now = datetime.now()

        self.ended_op_date = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.ended_op =True

