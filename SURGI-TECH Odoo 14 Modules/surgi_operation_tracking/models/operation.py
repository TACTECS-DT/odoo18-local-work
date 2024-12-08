from odoo import models, fields, api,_
from datetime import date,datetime
from datetime import timedelta

class OperationOperationInherit(models.Model):
    _inherit = 'operation.operation'

    confirmed_date = fields.Date(string="Confirmed Date")
    is_operation_tracking = fields.Boolean(string="",  )
    invoice_ids = fields.Many2many(comodel_name="account.move",related='sale_order_id.invoice_ids')
    invoice_date = fields.Char(string="Invoice Date",compute='compute_invoice_date')
    payment_lines_ids = fields.Many2many(comodel_name="account.payment",string="Payment",related='sale_order_id.payment_lines_ids' )

    is_collection = fields.Boolean(string="IS Collection")
    is_deposit = is_new_field = fields.Boolean(string="IS Deposit")
    collection_date = fields.Date(string="Collection Date")
    deposit_date = fields.Date(string="Deposit Date")

    collection_rep = fields.Many2one('res.users', 'Collection Rep',related='hospital_id.collection_rep')



    def operation_operation_tracking(self):

        user = self.env.user
        operators = []
        states = []
        domain = []
        domains = []
        counter = 0
        if user.has_group('surgi_operation_tracking.access_group_operation_tracking_manager'):

            domain=[]
            counter += 1
        elif user.has_group('surgi_operation_tracking.access_group_operation_tracking_collection_rep'):
            domain.append(('hospital_id.collection_rep','=',user.id))
            counter += 1


        form_view_id = self.env.ref('surgi_operation_tracking.form_view_operation_operation_tracking_inherit')
        tree_view_id = self.env.ref('surgi_operation_tracking.tree_view_operation_tracking')
        search_view_id = self.env.ref('surgi_operation_tracking.surgi_operation_tracking_search_view')

        context = {'default_is_operation_tracking': True, 'search_default_payment_methods': 1}

        return {
            'name': 'Operation Tracking',
            'type': 'ir.actions.act_window',
            'res_model': 'operation.operation',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')],
            'domain': domain,
            'search_view_id': self.env.ref('surgi_operation_tracking.surgi_operation_tracking_search_view').id,
            'context': context,

        }


    # def ks_view_items_view(self):
    #     self.ensure_one()
    #     return {
    #         'name': _("Dashboard Items"),
    #         'res_model': 'ks_dashboard_ninja.item',
    #         'view_mode': 'tree,form',
    #         'view_type': 'form',
    #         'views': [(False, 'tree'), (False, 'form')],
    #         'type': 'ir.actions.act_window',
    #         'domain': [('ks_dashboard_ninja_board_id', '!=', False)],
    #         'search_view_id': self.env.ref('ks_dashboard_ninja.ks_item_search_view').id,
    #         'context': {
    #             'search_default_ks_dashboard_ninja_board_id': self.id,
    #             'group_by': 'ks_dashboard_ninja_board_id',
    #         },
    #         'help': _('''<p class="o_view_nocontent_smiling_face">
    #                                     You can find all items related to Dashboard Here.</p>
    #                                 '''),
    #
    #     }

    def button_collection_date(self):
        self.collection_date = date.today()
        self.is_collection = True

    def button_deposit_date(self):
        self.deposit_date = date.today()
        self.is_deposit = True


    @api.depends('invoice_ids')
    def compute_invoice_date(self):
        for rec in self:
            all_invoice_date=''
            rec.invoice_date=False
            for inv in rec.invoice_ids:
                if inv.invoice_date:
                    all_invoice_date += str("[") +str(inv.invoice_date) + str("]")
            rec.invoice_date=all_invoice_date

    def action_confirm_sales(self):
        res=super(OperationOperationInherit, self).action_confirm_sales()

        if self.state=='confirm':
            self.confirmed_date=date.today()



        return res



    def get_approval_data(self, res_id):

        tracking_lines = self.env['mail.tracking.value'].sudo().search(
            [('mail_message_id.res_id', '=', res_id), ('mail_message_id.model', '=', 'operation.operation'),
             ])
        values = {}
        for track in tracking_lines:
            print(track.new_value_char,"rrrrrrrrrrrrr")
            if track.new_value_char not in ('مرفوض', 'ملغى', 'مرفوضة'):
                date = fields.Datetime.from_string(track.mail_message_id.date) + timedelta(hours=2)
                create_date = fields.Datetime.from_string(track.mail_message_id.create_date) + timedelta(hours=2)
                values.update({track.old_value_char: {'date': date,'create_date':create_date}})
        return values


    def button_operation_tracking(self):

        for rec in self:



            tracking_data = self.get_approval_data(rec.id)
            print(tracking_data)
            confirm_date=False
            for (key, value) in tracking_data.items():
                confirm_date = datetime.strptime(str(value['date']).split(".")[0],
                                                      '%Y-%m-%d %H:%M:%S').date()
            rec.confirmed_date = confirm_date

            sale_order_record = self.env['sale.order'].search([('operation_id','=',rec.id)])
            for sale in sale_order_record:
                rec.sale_order_id=sale.id



class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    payment_lines_ids = fields.Many2many(comodel_name="account.payment", string="Payment",compute='compute_payment_lines')

    @api.depends('state','payment_reference')
    def compute_payment_lines(self):
        for rec in self:
            lines=[]
            for pay in self.env['account.payment'].search([('ref','=',rec.payment_reference)]):
                lines.append(pay.id)
            rec.payment_lines_ids=lines



class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    payment_lines_ids = fields.Many2many(comodel_name="account.payment", string="Payment",compute='compute_payment_lines')

    @api.depends('name')
    def compute_payment_lines(self):
        for rec in self:
            rec.payment_lines_ids=False
            lines=[]
            for inv in self.env['account.move'].search([('invoice_origin','=',rec.name)]):
                rec.payment_lines_ids=inv.payment_lines_ids.ids

