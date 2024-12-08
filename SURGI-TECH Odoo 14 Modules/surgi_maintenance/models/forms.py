from odoo import models, fields, api, exceptions, _

from datetime import datetime, timedelta


class pick_up_and_delivery_form(models.Model):
    _name = 'pickup.delivery'

    client_res = fields.Many2one('res.partner', related="order_id.partner_id", string='العميل', store=True, )
    employee_id = fields.Many2one(related="order_id.user_id", string='موظف الشركة')

    contact_representative = fields.Many2one('contact.representative', string='المندوب', store=True,
                                             domain="[('contact_id', '=', client_res)]", )
    representative_mobile = fields.Char(string="التلفون", related='contact_representative.client_representative_mobile',
                                        store=True)
    pick_up = fields.Boolean('استلام')
    delivery = fields.Boolean('تسليم')

    pickup_date = fields.Date(string='التاريخ')

    comments = fields.Text(string='Comments')
    product_status = fields.One2many('product.forms', 'product_contact')

    #################### location
    street1 = fields.Char(related='client_res.street', string='الشارع')
    street2 = fields.Char(related='client_res.street2', string='الشارع')
    city = fields.Char(related='client_res.city', string='المدينة')
    country_id = fields.Char(related='client_res.country_id.name', string='البلد')

    order_id = fields.Many2one('sale.order', store=True, string='رقم امر التوريد')
    sale_date = fields.Datetime(related='order_id.date_order', string='تاريخ امر التوريد')
    picking_id = fields.Many2one('stock.picking', store=True, domain="[('sale_id', '=', order_id)]")
    product_forms = fields.One2many('stock.move.line', 'pickup_delivery_id',
                                    related="picking_id.move_line_ids_without_package", domain=[()], string='المنتج',
                                    readonly=False)

    @api.onchange('order_id')
    def compute_display_name_order_id(self):
        self.picking_id = ""

    def _get_default_code(self):
        return self.env["ir.sequence"].next_by_code("pickup.delivery.code")

    name = fields.Char(
        "الرقم المرجعي", readonly=True, index=True, store=True, default=_get_default_code
    )

    @api.onchange('client_res')
    def compute_display_name(self):
        self.contact_representative = ""

    def print_delivery_report(self):
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date
        }
        # docids = self.env['sale.order'].search([]).ids
        return self.env.ref('surgi_maintenance.report_maintenance_card').report_action(None, data=data)


class SaleOrderLine(models.Model):
    _inherit = 'stock.move.line'

    pickup_delivery_id = fields.Many2one('pickup.delivery', store=True, )
    pickup_repair = fields.Many2one('pickup.repair', store=True, )
    pickup_installation = fields.Many2one('pickup.installation', store=True, )
    pickup_delivery_final = fields.Many2one('pickup.final', store=True, )
    pickup_delivery_visit = fields.Many2one('pickup.visit', store=True, )
    pickup_delivery_inform = fields.Many2one('maintenance.inform', store=True, )

    specilaization = fields.Many2many('product.specializationinfos', string='التخصص')
    operting_maint = fields.Many2many('product.operating', string='طريقة التشغيل')
    occuption_maint = fields.Many2many('product.occupation', string='الوظيفة')


class maint_pic_up(models.AbstractModel):
    _name = 'report.maintenance.report_maintenance_card'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pickup.delivery'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'pickup.delivery',
            'docs': docs,
            'data': data,
            'get_something': self.get_something,
        }

    def get_something(self):
        return 5


class pick_up_and_repair_form(models.Model):
    _name = 'pickup.repair'

    client_res = fields.Many2one('res.partner', related="order_id.partner_id", string='العميل', store=True, )
    employee_id = fields.Many2one(related="order_id.user_id", string='موظف الشركة')
    contact_representative = fields.Many2one('contact.representative', string='المندوب', store=True,
                                             domain="[('contact_id', '=', client_res)]", )
    representative_mobile = fields.Char(string="التلفون", related='contact_representative.client_representative_mobile',
                                        store=True)
    pick_up = fields.Boolean('استلام')
    repair = fields.Boolean('إصلاح')

    pickup_date = fields.Date(string='التاريخ')
    comments = fields.Text(string='ملاحظات')
    product_repair = fields.One2many('product.forms', 'product_repair')
    product_status = fields.One2many('product.forms', 'product_repair')

    #################### location
    street1 = fields.Char(related='client_res.street', string='الشارع')
    street2 = fields.Char(related='client_res.street2', string='الشارع')
    city = fields.Char(related='client_res.city', string='المدينة')
    country_id = fields.Char(related='client_res.country_id.name', string='البلد')

    order_id = fields.Many2one('sale.order', store=True, string='رقم امر التوريد')
    sale_date = fields.Datetime(related='order_id.date_order', string='تاريخ امر التوريد')
    picking_id = fields.Many2one('stock.picking', store=True, domain="[('sale_id', '=', order_id)]")
    product_forms = fields.One2many('stock.move.line', 'pickup_repair',
                                    related="picking_id.move_line_ids_without_package", domain=[()], string='المنتج',
                                    readonly=False , ondelete="cascade")

    @api.onchange('order_id')
    def compute_display_name_order_id(self):
        self.picking_id = ""

    def print_report(self):
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date
        }

        return self.env.ref('surgi_maintenance.report_maintenance_repair_card').report_action(None, data=data)

    def _get_default_code(self):
        return self.env["ir.sequence"].next_by_code("pickup.repair.code")

    name = fields.Char(
        "الرقم المرجعي", readonly=True, index=True, store=True, default=_get_default_code
    )

    @api.onchange('client_res')
    def compute_display_name(self):
        self.contact_representative = ""


class maint_repair(models.AbstractModel):
    _name = 'report.maintenance.report_maintenance_repair_card'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pickup.repair'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'pickup.repair',
            'docs': docs,
            'data': data,
            'get_something': self.get_something,
        }

    def get_something(self):
        return 5


class pick_up_Installation_form(models.Model):
    _name = 'pickup.installation'

    client_res = fields.Many2one('res.partner', related="order_id.partner_id", string='العميل', store=True, )
    employee_id = fields.Many2one(related="order_id.user_id", string='موظف الشركة')
    contact_representative = fields.Many2one('contact.representative', string='المندوب', store=True,
                                             domain="[('contact_id', '=', client_res)]", )
    representative_mobile = fields.Char(string="التلفون", related='contact_representative.client_representative_mobile',
                                        store=True)
    pickup_date = fields.Date(string='تاريخ التركيب والتشغيل')
    comments = fields.Text(string='ملاحظات')

    #################### location
    street1 = fields.Char(related='client_res.street', string='الشارع')
    street2 = fields.Char(related='client_res.street2', string='الشارع')
    city = fields.Char(related='client_res.city', string='المدينة')
    country_id = fields.Char(related='client_res.country_id.name', string='البلد')

    order_id = fields.Many2one('sale.order', store=True, string='رقم امر التوريد')
    sale_date = fields.Datetime(related='order_id.date_order', string='تاريخ امر التوريد')
    picking_id = fields.Many2one('stock.picking', store=True, domain="[('sale_id', '=', order_id)]")
    product_forms = fields.One2many('stock.move.line', 'pickup_installation',
                                    related="picking_id.move_line_ids_without_package", domain=[()], string='المنتج',
                                    readonly=False)

    def _get_default_code(self):
        return self.env["ir.sequence"].next_by_code("pickup.installation.code")

    name = fields.Char(
        "الرقم المرجعي", readonly=True, index=True, store=True, default=_get_default_code
    )

    @api.onchange('client_res')
    def compute_display_name(self):
        self.contact_representative = ""

    def print_installation_report(self):
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date
        }
        # docids = self.env['sale.order'].search([]).ids
        return self.env.ref('surgi_maintenance.report_maintenance_install_card').report_action(None, data=data)


class maint_installation(models.AbstractModel):
    _name = 'report.maintenance.report_maintenance_install_card'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pickup.installation'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'pickup.installation',
            'docs': docs,
            'data': data,
            'get_something': self.get_something,
        }

    def get_something(self):
        return 5


class pick_up_Installation_form(models.Model):
    _name = 'pickup.final'

    client_res = fields.Many2one('res.partner', related="order_id.partner_id", string='العميل', store=True, )
    employee_id = fields.Many2one(related="order_id.user_id", string='موظف الشركة')
    contact_representative = fields.Many2one('contact.representative', string='المندوب', store=True,
                                             domain="[('contact_id', '=', client_res)]", )
    representative_mobile = fields.Char(string="التلفون", related='contact_representative.client_representative_mobile',
                                        store=True)
    pickup_date = fields.Date(string='تاريخ التسليم')
    comments = fields.Text(string='ملاحظات')

    #################### location
    street1 = fields.Char(related='client_res.street', string='الشارع')
    street2 = fields.Char(related='client_res.street2', string='الشارع')
    city = fields.Char(related='client_res.city', string='المدينة')
    country_id = fields.Char(related='client_res.country_id.name', string='البلد')

    sale_date = fields.Datetime(related='order_id.date_order', string='تاريخ امر التوريد')

    order_id = fields.Many2one('sale.order', store=True, string='رقم امر التوريد')
    sale_date = fields.Datetime(related='order_id.date_order', string='تاريخ امر التوريد')
    picking_id = fields.Many2one('stock.picking', store=True, domain="[('sale_id', '=', order_id)]")
    product_forms = fields.One2many('stock.move.line', 'pickup_delivery_final',
                                    related="picking_id.move_line_ids_without_package", domain=[()], string='المنتج',
                                    readonly=False)

    def _get_default_code(self):
        return self.env["ir.sequence"].next_by_code("pickup.final.code")

    name = fields.Char(
        "الرقم المرجعي", readonly=True, index=True, store=True, default=_get_default_code
    )

    # @api.multi
    # def print_report(self):
    #     return self.env.ref('').report_action(self)

    @api.onchange('client_res')
    def compute_display_name(self):
        self.contact_representative = ""

    def print_final_installation_report(self):
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date
        }
        # docids = self.env['sale.order'].search([]).ids
        return self.env.ref('surgi_maintenance.report_maintenance_final_install_card').report_action(None, data=data)


class maint_final_install(models.AbstractModel):
    _name = 'report.maintenance.report_maintenance_final_install_card'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pickup.final'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'pickup.final',
            'docs': docs,
            'data': data,
            'get_something': self.get_something,
        }

    def get_something(self):
        return 5


class pick_up_Installation_form(models.Model):
    _name = 'pickup.visit'

    client_res = fields.Many2one('res.partner', related="order_id.partner_id", string='العميل', store=True, )
    employee_id = fields.Many2one(related="order_id.user_id", string='موظف الشركة')
    contact_representative = fields.Many2one('contact.representative', string='المندوب', store=True,
                                             domain="[('contact_id', '=', client_res)]", )
    representative_mobile = fields.Char(string="التلفون", related='contact_representative.client_representative_mobile',
                                        store=True)
    pickup_date = fields.Date(string='تاريخ التسليم')
    comments = fields.Text(store=True, string='ملاحظات')
    comments1 = fields.Text(store=True, string='ملاحظات')
    comments2 = fields.Text(store=True, string='ملاحظات')
    comments3 = fields.Text(store=True, string='ملاحظات')
    comments4 = fields.Text(store=True, string='ملاحظات')
    sale_date = fields.Datetime(related='order_id.date_order', string='تاريخ امر التوريد')
    product_inform = fields.Many2one('maintenance.inform',string="البلاغ" ,domain="[('client_res','=',client_res)]")

    #################### location
    street1 = fields.Char(related='client_res.street', string='الشارع')
    street2 = fields.Char(related='client_res.street2', string='الشارع')
    city = fields.Char(related='client_res.city', string='المدينة')
    country_id = fields.Char(related='client_res.country_id.name', string='البلد')

    order_id = fields.Many2one('sale.order', store=True, string='رقم امر التوريد')
    sale_date = fields.Datetime(related='order_id.date_order', string='تاريخ امر التوريد')
    picking_id = fields.Many2one('stock.picking', store=True, domain="[('sale_id', '=', order_id)]")
    product_forms = fields.One2many('stock.move.line', 'pickup_delivery_visit',
                                    related="picking_id.move_line_ids_without_package", domain=[()], string='المنتج',
                                    readonly=False)

    def _get_default_code(self):
        return self.env["ir.sequence"].next_by_code("pickup.visit.code")

    name = fields.Char(
        "الرقم المرجعي", readonly=True, index=True, store=True, default=_get_default_code
    )

    inform = fields.Boolean('إبلاغ')
    planed = fields.Boolean('مخطط')
    installed = fields.Boolean('تركيب')
    insure = fields.Boolean('داخل الضمان')
    uninsure = fields.Boolean('خارج الضمان')
    ###############################################
    press = fields.Boolean('الضغط')
    filt = fields.Boolean('الفلاتر')
    dry = fields.Boolean('التجفيف')
    received = fields.Boolean('مسلمة')
    unreceived = fields.Boolean('غير مسلمة')
    temp = fields.Boolean('درجة الحرارة')
    timeder = fields.Boolean('مدة الدورة')
    fit_to_dry = fields.Boolean('وجود مجفف من عدمة')
    dry_or_not = fields.Boolean('ملائمة الغسيل')
    customer_vgood = fields.Boolean('ممتازة')
    customer_good = fields.Boolean('جيدة')
    customer_bad = fields.Boolean('سيئة')

    @api.onchange('client_res')
    def compute_display_name(self):
        self.contact_representative = ""

    def print_visit_report(self):
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date
        }
        # docids = self.env['sale.order'].search([]).ids
        return self.env.ref('surgi_maintenance.report_maintenance_visit_card').report_action(None, data=data)


class maint_final_visit(models.AbstractModel):
    _name = 'report.maintenance.report_maintenance_visit_card'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pickup.visit'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'pickup.visit',
            'docs': docs,
            'data': data,
            'get_something': self.get_something,
        }

    def get_something(self):
        return 5



class product_forms(models.Model):
    _name = 'product.forms'
    product_form_id = fields.Many2one('product.template', string='المنتج')
    product_contact = fields.Many2one('pickup.delivery')
    product_repair = fields.Many2one('pickup.repair')
    product_installation = fields.Many2one('pickup.installation')
    product_final = fields.Many2one('pickup.final')
    product_visit = fields.Many2one('pickup.visit')

    internal_ref = fields.Char(related='product_form_id.default_code', string='رقم الكتالوج')
    specilaization = fields.Many2many('product.specializationinfos', string='التخصص')
    notic = fields.Char(string='ملاحظات')
    date = fields.Date(string='التاريخ')
    product_status = fields.Char('حالة الجهاز الظاهرية')
    product_sug = fields.Char('اﻷجراءت المقترحة')
    product_status_tec = fields.Char('حالة الجهاز الفنية')





class sale_order(models.Model):
    _inherit = "sale.order"
    maintenance_id = fields.Many2one(comodel_name='pickup.installation', string="Related maintenance")
