# -*- coding: utf-8 -*-

from odoo import models, fields, api

import mimetypes
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError
from collections import defaultdict

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'


    extension = fields.Char(string='Extension', compute='_compute_extension', store=True)

    @api.depends('mimetype')
    def _compute_extension(self):
        for record in self:
            if record.mimetype:
                record.extension = mimetypes.guess_extension(record.mimetype)
    @api.model
    def check(self, mode, values=None):
        """ Restricts the access to an ir.attachment, according to referred mode """
        if self.env.is_superuser():
            return True
        # Always require an internal user (aka, employee) to access to an attachment
        # if not (self.env.is_admin() or self.env.user.has_group('base.group_user')):
        #     _logger.warning("warning first")
        #     raise AccessError(_("Sorry, you are not allowed to access this document."))
        # collect the records to check (by model)
        model_ids = defaultdict(set)  # {model_name: set(ids)}
        if self:
            # DLE P173: `test_01_portal_attachment`
            self.env['ir.attachment'].flush(['res_model', 'res_id', 'create_uid', 'public', 'res_field'])
            self._cr.execute(
                "SELECT res_model, res_id, create_uid, public, res_field FROM ir_attachment WHERE id IN %s",
                [tuple(self.ids)])
            for res_model, res_id, create_uid, public, res_field in self._cr.fetchall():
                if not self.env.is_system() and res_field:
                    _logger.warning("warning second")
                    raise AccessError(_("Sorry, you are not allowed to access this document."))
                if public and mode == 'read':
                    continue
                if not (res_model and res_id):
                    continue
                model_ids[res_model].add(res_id)
        if values and values.get('res_model') and values.get('res_id'):
            model_ids[values['res_model']].add(values['res_id'])

        # check access rights on the records
        for res_model, res_ids in model_ids.items():
            # ignore attachments that are not attached to a resource anymore
            # when checking access rights (resource was deleted but attachment
            # was not)
            if res_model not in self.env:
                continue
            if res_model == 'res.users' and len(res_ids) == 1 and self.env.uid == list(res_ids)[0]:
                # by default a user cannot write on itself, despite the list of writeable fields
                # e.g. in the case of a user inserting an image into his image signature
                # we need to bypass this check which would needlessly throw us away
                continue
            records = self.env[res_model].browse(res_ids).exists()
            # For related models, check if we can write to the model, as unlinking
            # and creating attachments can be seen as an update to the model
            access_mode = 'write' if mode in ('create', 'unlink') else mode
            records.check_access_rights(access_mode)
            records.check_access_rule(access_mode)



# class portal_custom(models.Model):
#     _name = 'portal_custom.portal_custom'
#     _description = 'portal_custom.portal_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.constrains('groups_id')
    def _check_one_user_type(self):
        """We check that no users are both portal and users (same with public).
           This could typically happen because of implied groups.
        """
        user_types_category = self.env.ref('base.module_category_user_type', raise_if_not_found=False)
        user_types_groups = self.env['res.groups'].search(
            [('category_id', '=', user_types_category.id)]) if user_types_category else False
        # if user_types_groups:  # needed at install
        #     if self._has_multiple_groups(user_types_groups.ids):
        #         raise ValidationError(_('The user cannot have more than one user types.'))
