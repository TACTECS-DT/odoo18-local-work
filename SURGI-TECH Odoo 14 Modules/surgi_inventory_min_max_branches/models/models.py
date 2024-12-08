# -*- coding: utf-8 -*-

from odoo import models, fields,_


# class branches_location_wharehouse(models.Model):
#     _name= 'branch.location'
#     name = fields.Char(string="Branch",store=True)
#


class inventoryMinMaxBrancesg(models.Model):
    _name = 'minmax.branches'

    product_Id = fields.Many2one('product.product', string="Product", store=True)
    branch_name = fields.Many2one('branch.location', string="Product Branch", store=True)
    min_branch = fields.Char(string="Minimum", store=True)
    max_branch = fields.Char(string="Maximum", store=True)
    avlible_loc = fields.Float(string="Available Quantity", compute="get_available_quantity")
    # avlible_zzzzzzzz = fields.Float(string="Available Quantity 222", compute="get_available_quantity")
    avlible_loc_per_branch = fields.Float(string="Branch Quantity", compute="avlible_qunt_per_branch")
    operation_per_branch = fields.Float(string="Operations", compute="operations_qunt_per_branch")
    sum_of_op = fields.Float(string="Total Branch", compute="operations_total_qy")
    diff_of_op = fields.Float(string="Differential", compute="differential_total_qy", )


    def operations_total_qy(self):

        for objs in self:
            objs.sum_of_op = objs.avlible_loc_per_branch + objs.operation_per_branch

    def differential_total_qy(self):

        for objs in self:
            maxiumm = int(objs.max_branch)

            objs.diff_of_op = objs.sum_of_op - maxiumm

    def operations_qunt_per_branch(self):

        for objs in self:
            objs.operation_per_branch = self.env['stock.quant'].search_count([('product_id', '=', objs.product_Id.id),
                                                                              ('location_id.usage', 'in', ['transit']),
                                                                              ('branch', '=', objs.branch_name.name),
                                                                              ('is_operation_freeze', '=', False),
                                                                              ('is_operation_related', '=', True)])

    def avlible_qunt_per_branch(self):

        for objs in self:
            obj_list = []
            obj_list2 = []

            obj_test = self.env['stock.quant'].search([('product_id', '=', objs.product_Id.id),
                                                       ('location_id.usage', 'in', ['internal', 'transit']),
                                                       ('branch', '=', objs.branch_name.name),
                                                       ('is_operation_related', '=', False), ('on_hand', '=', True)])
            for val in obj_test:
                obj_list2.append(val.available_quantity)
                objs_av = val.available_quantity
                obj_list.append(objs_av)

            objs.avlible_loc_per_branch = sum(obj_list)

    def get_available_quantity(self):
        for rec in self:
            qty = rec.product_Id.qty_available
            rec.avlible_loc =qty
    # def avlible_qunt_location(self):
    #
    #     for objs in self:
    #         obj_list = []
    #         obj_list2 = []
    #
    #         obj_test = self.env['stock.quant'].search(
    #             [('product_id', '=', objs.product_Id.id), ('location_id.usage', 'in', ['internal', 'transit'],),
    #              ('on_hand', '=', True)])
    #         for val in obj_test:
    #             obj_list2.append(val.available_quantity)
    #             objs_av = val.available_quantity
    #             obj_list.append(objs_av)
    #
    #         objs.avlible_loc = sum(obj_list)

    def name_get(self):
        res = []
        for rec in self:
            name = u"{} ({}) ({})".format(rec.branch_name.name, rec.min_branch, rec.max_branch)
            res.append((rec.id, name))
        return res


class Product_Product_Branches(models.Model):
    _inherit = 'product.product'
    MinMaxBranches = fields.One2many(comodel_name='minmax.branches', inverse_name='product_Id', string="Product Branch",
                                     store=True)
    tax_line_ids = fields.Many2many('product.product',
                                    'MinMaxBranches',
                                    'branches',
                                    'min_branch',
                                    'List of taxes',
                                    store=True)


class Product_Product_Branches(models.Model):
    _inherit = 'product.template'

    MinMaxBranches = fields.One2many(related="product_variant_id.MinMaxBranches", readonly=False)


class Stock_qount_Braches(models.Model):
    _inherit = 'stock.quant'

    product_branches = fields.One2many(related='product_id.MinMaxBranches', string="Product Branches")
