from odoo import models, fields, api
class SalaOrder(models.Model):
    _inherit = 'sale.order'

    expenses_line_ids = fields.One2many(comodel_name="expenses.lines", inverse_name="sale_id",)
    #is_expenses_line_ids = fields.Boolean(string="",compute='compute_is_expenses_line_ids'  )


    def compute_is_expenses_line_ids(self):
        for rec in self:
           lines_list=[(5,0,0)]
           rec.is_expenses_line_ids=False
           # for expen in self.env['hr.expense'].search([('sales_id','=',rec.id)]):
           #     lines_list.append((0,0,{
           #         'expenses_id':expen.id,
           #         'date':expen.date,
           #         'total_amount':expen.total_amount,
           #     }))
           #     rec.is_expenses_line_ids =True
           # rec.expenses_line_ids=lines_list





class HRExpensesLine(models.Model):
    _name = 'expenses.lines'
    _rec_name = 'expenses_id'

    expenses_id = fields.Many2one(comodel_name="hr.expense", string="Expenses",)
    date = fields.Date(string="Date", required=False, )
    total_amount = fields.Float(string="Total Amount", required=False, )
    sale_id = fields.Many2one(comodel_name="sale.order", string="", required=False, )
