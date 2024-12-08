from odoo import models, fields, api
from datetime import date,datetime,time,timedelta

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'


    accounting_approval = fields.Selection(string="Accounting Apploval",
                                           selection=[('approve', 'Approved'),
                                                      ('reject', 'Rejected'),
                                                      ('hold', 'Hold'),
                                                      ], readonly=True,track_visibility='onchange' )

    approval_date = fields.Date(string="Approval Date", readonly=True,track_visibility='onchange' )
    reject_date = fields.Date(string="Rejected Date", readonly=True,track_visibility='onchange' )
    hold_date = fields.Date(string="Hold Date", readonly=True,track_visibility='onchange' )

    def approve_button(self):
        self.accounting_approval='approve'
        self.approval_date=date.today()


    def reject_button(self):
        self.accounting_approval='reject'
        self.reject_date = date.today()

    def hold_button(self):
        self.accounting_approval='hold'
        self.hold_date = date.today()