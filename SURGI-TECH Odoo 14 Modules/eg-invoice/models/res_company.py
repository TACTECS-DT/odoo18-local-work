from odoo import fields, models, api
from . import EnvoConfig


class ResCompanyInhert(models.Model):
    #_name="res_company_egytax_inhert"
    _inherit = 'res.company'

#,selection =EnvoConfig.Segnelton.getActivities()
    activitytype=fields.Selection(string="Company Activity",selection =[("","")],selection_add =EnvoConfig.Segnelton.getActivities())
    registration_id=fields.Char(string="Tax Registration id")
    pre_egtax_v=fields.Float("Pre Production Version")
    pro_egtax_v=fields.Float("Production Version")
    pre_egtax_clientid=fields.Char("Pre-Production Client ID")
    pro_egtax_clientid=fields.Char("Production Client ID")
    pre_egtax_clientsecret1=fields.Char("Pre-Production Secret Key 1")
    pro_egtax_clientsecret1=fields.Char("Production Secret Key 1")
    pre_egtax_clientsecret2=fields.Char("Pre-Production Secret Key 2")
    pro_egtax_clientsecret2=fields.Char("Production Secret Key 2")
    pre_egtax_default=fields.Boolean("Use Production")
    building_no=fields.Char(string="Building No.")

