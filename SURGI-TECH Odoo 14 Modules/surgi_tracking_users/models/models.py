from odoo import models, fields, api,_
from datetime import date,datetime,time,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError



class surgi_tracking_users(models.Model):
    _inherit = "stock.picking"
    transfer_created_on = fields.Char(string="Created On Date", readonly=True)
    transfer_created_by = fields.Char(string="Created by", readonly=True)
    validated_on = fields.Char(string="Validate On Date", readonly=True)
    validated_by = fields.Char(string="Validate by", readonly=True)

    @api.model
    def create(self,vals):

        user = self.env.user

        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
                # self.started_op_date=datetime.now(),
        vals['transfer_created_on'] = now.strftime("%m/%d/%Y, %H:%M:%S")
        vals['transfer_created_by'] = user_name
        res = super(surgi_tracking_users, self).create(vals)

        return res
    def button_validate(self):
        res = super(surgi_tracking_users, self).button_validate()
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.validated_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.validated_by = user_name
        return res
