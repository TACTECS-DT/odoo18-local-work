from odoo import fields, models, api


class POSPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    eg_eta_code = fields.Selection([('C', 'Cash'),
                                    ('V', 'Visa'),
                                    ('CC', 'Cash with contractor'),
                                    ('VC', 'Visa with contractor'),
                                    ('VO', 'Vouchers'),
                                    ('PR', 'Promotion'),
                                    ('GC', 'Gift Card'),
                                    ('P', 'Points'),
                                    ('O', 'Others')], string='ETA Payment Code')


