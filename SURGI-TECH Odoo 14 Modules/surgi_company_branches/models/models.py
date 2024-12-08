# -*- coding: utf-8 -*-

from odoo import models, fields, api


class surgi_company_branches(models.Model):
     _name = 'surgi.company.branches'
     _description = 'surgi_company_branches.surgi_company_branches'

     name=fields.Char("Branch Name")
     company_id=fields.Many2one('res.company',  string="Company")


class branch_company_inhert(models.Model):
     _inherit="res.company"
     branches=fields.One2many('surgi.company.branches', 'company_id', string="Branches")


#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
class stock_location_branch_inhert(models.Model):
     _inherit = "stock.location"
     @api.model
     def get_company_id_domain(self):
          domain = "[('company_id','='," + str(self.company_id.id)+ ")]"
          return domain


     branch=fields.Many2one("surgi.company.branches",string="Branch")


class stock_quant_branch_inhert(models.Model):
     _inherit = "stock.quant"
#      def __init__(self):
#           super().__init__() 
#           self.update_branches()
     #branch=fields.Many2one("surgi.company.branches",string="branch",compute="_get_branch",store=True)
     #branch=fields.Selection(selection=lambda self: self.get_branches,compute="_get_branch")#,
     #branch =fields.Char(string="branches")#related='location_id.branch.name'
     #branch=fields.Char(related=get_current_branch())
     branch=fields.Char(string='Branch',compute="_get_current_branch",store=True)
     # def get_branches(self):
     #      b=[]
     #      b.append((str(-1),""))
     #      for i in self.location_id.company_id.branches:
     #           b.append((str(i.id),str(i.name)))
     #      return b
     #      pass
     #@api.depends('location_id')
     @api.model
     def update_branches(self):
          allrec=self.search([])
          for rec in allrec:
               if rec.location_id.usage=="view":
                    if rec.location_id.branch.name:
                         rec.write({"branch": rec.location_id.branch.name})
                         

               else:
                    if rec.location_id.location_id.branch.name:
                         x=rec.location_id.location_id.branch.name
                         rec.write({"branch": rec.location_id.location_id.branch.name})


          # pass
     def _get_current_branch(self):
          for rec in self:
               if rec.location_id.usage=="view":
                    if rec.location_id.branch:
                         rec.branch= rec.location_id.branch.name
                    else:
                         rec.branch= ""
               else:
                    if rec.location_id.location_id.branch.name:
                         x=rec.location_id.location_id.branch.name
                         rec.branch= rec.location_id.location_id.branch.name
                    else:
                         rec.branch= ""
          pass
     #@api.depends('location_id.branch', 'location_id.location_id.branch')
     def _get_branch(self):
          for rec in self:
               if rec.location_id.usage=="view":
                    if rec.location_id.branch:
                         return rec.location_id.branch.id
                    else:
                         return -1
               else:
                    if self.location_id.location_id.branch:
                         return self.location_id.location_id.branch.id
                    else:
                         return -1
