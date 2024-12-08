from datetime import date
from odoo import api,_
from odoo import exceptions
from odoo import fields
from odoo import models
# from dateutil.relativedelta import relativedelta
from odoo.exceptions import  ValidationError

# =============== Dalia Atef =============
class waiting_list_patients(models.Model):
    _name = 'waiting.list.patients'
    _order = "patient_national_id"
    _rec_name = 'patient_national_id'

    # ==================== Methods =========================


    # ==================== Fields ==========================
    patient_name = fields.Char('Patient Name', required=True)
    patient_national_id = fields.Char('National ID', required=True)
    moh_approved_operation= fields.Char('MOH Approved Operation', required=True)
    # sequence = fields.Integer('Sequence', default=0)
    is_active = fields.Boolean('Active', default=True)


    @api.constrains('patient_national_id')
    def check_identification_id(self):
        for rec in self:
            if len(rec.patient_national_id) != 14:
                raise ValidationError(_('Patient National ID Must be 14 Digit'))

    # _sql_constraints = [
    #     (
    #         "id_check",
    #         "CHECK (length(patient_national_identification) > 14)",
    #         "Patient National ID Must be 14 Digit",
    #     )
    # ]
