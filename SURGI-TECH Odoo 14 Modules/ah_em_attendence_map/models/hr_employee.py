from datetime import datetime, timedelta
from odoo import api, fields, http, models, _
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from geopy import distance

class AhHrEmployee(models.Model):
    _inherit = 'hr.employee'
    multi_location_checkin=fields.Many2many( comodel_name="res.partner",string="Additional Checkin Locations")

    def attendance_manual(self, next_action, lat, longi, entered_pin=None):
        #super(AhHrEmployee,self).attendance_manual( next_action, lat, longi, entered_pin=None)
        self.ensure_one()
        res_config = self.env['res.config.settings'].sudo().search([],
                                                                   order="id desc",
                                                                   limit=1)
        address_locations=[]
        location_restriction = self.sudo().location_restriction

        if location_restriction == True:
            if not self.multi_location_checkin and not self.address_id :
                raise ValidationError(_('Please Add CheckIn Locations'))
            partner_ids = self.multi_location_checkin
            partner_idx=self.address_id
            if partner_idx.partner_latitude == 0 or partner_idx.partner_longitude == 0:
                raise ValidationError(
                    _('Please Set the Geolocation'
                      ' of the Work Address : %s address first' % partner_idx.name))
            for partner_id in partner_ids:
                if partner_id.partner_latitude == 0 or partner_id.partner_longitude == 0:
                    raise ValidationError(
                        _('Please Set the Geolocation'
                        ' of the Work Address : %s address first' % partner_id.name))
            max_distance = float(
                self.env['ir.config_parameter'].sudo().get_param(
                    'emp_attendance_map_advance_app.max_attendance_distance'))
            
            address_locations.append(tuple((partner_idx.partner_latitude, partner_idx.partner_longitude)))
            
            for partner_id in partner_ids:         
                address_locations.append(tuple((partner_id.partner_latitude, partner_id.partner_longitude)))
            employee_location = (lat, longi)
            approved=0
            for address_location in address_locations:
                dist = distance.distance(address_location, employee_location).km
                if dist <= max_distance:
                    approved=1
            if not approved:
                raise ValidationError(_(
                    'Please Check In near your Working Address : %s' % partner_idx.name))
            # if lat and longi:
            #     co_long = float(res_config.longitude)
            #     co_lat = float(res_config.latitude)
            #     if lat != co_lat or longi != co_long:
            #         raise ValidationError(_('Check In from the working area'))
        can_check_without_pin = not self.env.user.has_group(
            'hr_attendance.group_hr_attendance_use_pin') or (
                                        self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
            return self._attendance_action(next_action)
        return {'warning': _('Wrong PIN')}



class respartenerihert(models.Model):
    _inherit = 'res.partner'
    #hr_employee_locations=fields.Many2one(comodel_name="ah.hr.employee.locations",string="employee Locations")
    multi_location_checkin_inverse=fields.One2many(comodel_name='hr.employee',inverse_name="multi_location_checkin")


        
    

# class HrEmployeeLocations(models.Model):
#     _name="ah.hr.employee.locations"
#     multi_location_checkin_inverse=fields.One2many(comodel_name='hr.employee',inverse_name="multi_location_checkin")
#     location=fields.One2many(comodel_name='res.partner',string="Location",inverse_name="hr_employee_locations")





    

    
