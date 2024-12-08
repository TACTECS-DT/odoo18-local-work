from odoo import models, fields, api,exceptions ,_





class crm_pipeline_res_partner_emp(models.Model):
    _name = 'contact.representative'
    contact_id = fields.Many2one("res.partner", string="contact",store=True)

    position_representative = fields.Char('Position',store=True)
    name = fields.Char(string="Client Name",store=True)
    client_representative_mobile = fields.Char(string="Client Mobile",store=True)

class crm_pipeline_res_partner(models.Model):
    _inherit = 'res.partner'


    erepresentative_id = fields.One2many('contact.representative','contact_id', string='Representative',store=True)


class crm_pipeline_specialization(models.Model):
    _name = 'product.specializationinfos'
    # _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char(string="product specialization",store=True)
class crm_pipeline_operation(models.Model):
    _name = 'product.operating'
    # _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char(string="Operating",store=True)

class crm_pipeline_occupation(models.Model):
    _name = 'product.occupation'
    # _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char(string="Occupation",store=True)




class sale_order(models.Model):
    _inherit = "sale.order"

    maint_loc_so = fields.Char("محضر تركيب و تشغيل أجهزة", compute='get_mainta_so')#, compute=get_operation_so
    maint_delivary_so = fields.Char("نموذج إستلام / تسليم اجهزة", compute='get_mainta_delivery_so')#, compute=get_operation_so
    maint_repair_so = fields.Char("نموذج إستلام/إصلاح", compute='get_mainta_repair_so')#, compute=get_operation_so
    maint_final_so = fields.Char("محضر تسليم نهائي", compute='get_mainta_final_so')#, compute=get_operation_so
    maint_visit_so = fields.Char("نموذج زيارة وخدمة ما بعد البيع", compute='get_mainta_visit_so')#, compute=get_operation_so
    maint_inform_so = fields.Char("البلاغ", compute='get_maintenance_inform_so')#, compute=get_operation_so

    after_sales_check = fields.Boolean('After Sales')
    def get_mainta_so(self):
        for rec in self:
            maintenanceSO = self.env['pickup.installation'].search([('order_id', '=', rec.id)])
            if maintenanceSO:
                rec.maint_loc_so = len(maintenanceSO)
            else:
                rec.maint_loc_so=0

    def action_view_sales_SO(self):
        for rec in self:
            operations = self.env['pickup.installation'].search([('order_id', '=', rec.id)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "محضر تركيب و تشغيل أجهزة",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'pickup.installation',
                'target': 'current',
                'domain': [('id', 'in', list)],
                'context': "{'search_default_order_id': active_id, 'default_order_id': active_id}"

            }
##################################################################################################
    def get_mainta_delivery_so(self):
        for rec in self:
            maintenanceSO = self.env['pickup.delivery'].search([('order_id', '=', rec.id)])
            if maintenanceSO:
                rec.maint_delivary_so = len(maintenanceSO)
            else:
                rec.maint_delivary_so = 0

    def action_view_delivery_sales_SO(self):
        for rec in self:
            operations = self.env['pickup.delivery'].search([('order_id', '=', rec.id)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': " نموذج إستلام / تسليم اجهزة",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'pickup.delivery',
                'target': 'current',
                'domain': [('id', 'in', list)],
                'context': "{'search_default_order_id': active_id, 'default_order_id': active_id}"

            }

    ##################################################################################################

    def get_mainta_repair_so(self):
        for rec in self:
            maintenanceSO = self.env['pickup.repair'].search([('order_id', '=', rec.id)])
            if maintenanceSO:
                rec.maint_repair_so = len(maintenanceSO)
            else:
                rec.maint_repair_so = 0

    def action_view_sales_repair_SO(self):
        for rec in self:
            operations = self.env['pickup.repair'].search([('order_id', '=', rec.id)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "نموذج إستلام/إصلاح",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'pickup.repair',
                'target': 'current',
                'domain': [('id', 'in', list)],
                'context': "{'search_default_order_id': active_id, 'default_order_id': active_id}"

            }
        ##################################################################################################

    ##################################################################################################
    def get_mainta_final_so(self):
        for rec in self:
            maintenanceSO = self.env['pickup.final'].search([('order_id', '=', rec.id)])
            if maintenanceSO:
                rec.maint_final_so = len(maintenanceSO)
            else:
                rec.maint_final_so = 0

    def action_view_sales_final_SO(self):
        for rec in self:
            operations = self.env['pickup.final'].search([('order_id', '=', rec.id)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "محضر تسليم نهائي",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'pickup.final',
                'target': 'current',
                'domain': [('id', 'in', list)],
                'context': "{'search_default_order_id': active_id, 'default_order_id': active_id}"

            }
##################################################################################################

    def get_mainta_visit_so(self):
        for rec in self:
            maintenanceSO = self.env['pickup.visit'].search([('order_id', '=', rec.id)])
            if maintenanceSO:
                rec.maint_visit_so = len(maintenanceSO)
            else:
                rec.maint_visit_so = 0

    def action_view_sales_visit_SO(self):
        for rec in self:
            operations = self.env['pickup.visit'].search([('order_id', '=', rec.id)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "نموذج زيارة وخدمة ما بعد البيع",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'pickup.visit',
                'target': 'current',
                'domain': [('id', 'in', list)],
                'context': "{'search_default_order_id': active_id, 'default_order_id': active_id}"

            }
##################################################################################################

    def get_maintenance_inform_so(self):
        for rec in self:
            maintenanceSO = self.env['maintenance.inform'].search([('order_id', '=', rec.id)])
            if maintenanceSO:
                rec.maint_inform_so = len(maintenanceSO)
            else:
                rec.maint_inform_so = 0

    def action_view_maintenance_inform_SO(self):
        for rec in self:
            operations = self.env['maintenance.inform'].search([('order_id', '=', rec.id)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "البلاغ",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'maintenance.inform',
                'target': 'current',
                'domain': [('id', 'in', list)],
                'context': "{'search_default_order_id': active_id, 'default_order_id': active_id}"

            }
