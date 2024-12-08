from datetime import datetime, timedelta

from odoo import models, fields, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    move_created_on = fields.Char(string="Created On Date", readonly=True)
    move_created_by = fields.Char(string="Created by", readonly=True)
    move_post_on = fields.Char(string="Posted On", readonly=True)
    move_post_by = fields.Char(string="Posted By", readonly=True)
    # expenses_approve_on = fields.Char(string="Approved On",readonly=True)
    # expenses_approve_by = fields.Char(string="Approved By",readonly=True)
    # account_reviewed_on = fields.Char(string="Account Reviewed On",readonly=True)
    # account_reviewed_by = fields.Char(string="Account Reviewed By",readonly=True)
    # treasury_manager_on = fields.Char(string="Treasury Manager On",readonly=True)
    # treasury_manager_by = fields.Char(string="Treasury Manager By",readonly=True)
    # submitted_on = fields.Char(string="Submitted On",readonly=True)
    # submitted_by = fields.Char(string="Submitted By",readonly=True)

    move_reset_on = fields.Char(string="Reset To Draft On", readonly=True)
    move_reset_by = fields.Char(string="Reset To Draft By", readonly=True)

    # secend_approved_on = fields.Char(string="Second Approve On", readonly=True)
    # secend_approved_by = fields.Char(string="Second Approve by", readonly=True)
    # cfo_approved_on= fields.Char(string="CFO Approve On", readonly=True)
    # cfo_approved_by=fields.Char(string='CFO Approve by', readonly=True)
    #

    @api.model
    def create(self, vals):
        res = super(AccountMoveInherit, self).create(vals)
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
        vals['move_created_on'] = now.strftime("%m/%d/%Y, %H:%M:%S")
        vals['move_created_by'] = user_name
        return res

    def action_post(self):
        res = super(AccountMoveInherit, self).action_post()
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
        # self.started_op_date=datetime.now(),
        self.move_post_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.move_post_by = user_name
        return res

    def button_draft(self):
        res = super(AccountMoveInherit, self).button_draft()
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
        self.move_reset_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.move_reset_by = user_name
        return res
