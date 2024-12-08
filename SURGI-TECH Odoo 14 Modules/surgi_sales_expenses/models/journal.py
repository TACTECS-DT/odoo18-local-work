from odoo import models, fields, api
class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    partner_surgeon_id = fields.Many2one(comodel_name="res.partner", string="Surgeon")
    event_id = fields.Many2one(comodel_name="hr.expenses.event", string="Event", )
    expenses_created_on = fields.Char(string="Created On Date", readonly=True)
    expenses_created_by = fields.Char(string="Created by", readonly=True)

    expenses_approve_on = fields.Char(string="Approved On",readonly=True)
    expenses_approve_by = fields.Char(string="Approved By",readonly=True)
    account_reviewed_on = fields.Char(string="Account Reviewed On",readonly=True)
    account_reviewed_by = fields.Char(string="Account Reviewed By",readonly=True)
    treasury_manager_on = fields.Char(string="Treasury Manager On",readonly=True)
    treasury_manager_by = fields.Char(string="Treasury Manager By",readonly=True)
    submitted_on = fields.Char(string="Submitted On",readonly=True)
    submitted_by = fields.Char(string="Submitted By",readonly=True)
    post_on = fields.Char(string="Posted On",readonly=True)
    post_by = fields.Char(string="Posted By",readonly=True)
    reset_on =fields.Char(string="Reset To Draft On",readonly=True)
    reset_by = fields.Char(string="Reset To Draf By", readonly=True)
    secend_approved_on = fields.Char(string="Second Approve On", readonly=True)
    secend_approved_by = fields.Char(string="Second Approve by", readonly=True)
    cfo_approved_on= fields.Char(string="CFO Approve On", readonly=True)
    cfo_approved_by=fields.Char(string='CFO Approve by', readonly=True)

    
class AccountJournalInherit(models.Model):
    _inherit ='account.journal'

    transferred_by_bank = fields.Boolean('Transferred By Bank')

