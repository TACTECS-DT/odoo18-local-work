# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError
import csv
from odoo.modules.module import get_module_resource
import logging
_logger = logging.getLogger(__name__)
#from types import ClassType
# class surgi_pricelists(models.Model):
#     _name = 'surgi_pricelists.surgi_pricelists'
#     _description = 'surgi_pricelists.surgi_pricelists'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100



class PriceListsSurgi(models.Model):
    #_name = 'customer.multi.pricelists'
    _inherit="res.partner"
    #_description = 'model.technical.name'
    #hospitalpricelists=fields.One2many(string="Hospitals Price Lists",comodel_name="product.pricelist",inverse_name="hospitalpricelistsrev")
    hospitalpricelists = fields.Many2many(
        string='Hospitals Price Lists',
        comodel_name='product.pricelist',
        relation='partner_pricelists_rel',
        column1='hospitalpricelistsrev',
        column2='hospitalpricelists',
    )
    tracker=fields.One2many(comodel_name="hospitallist_tracker",inverse_name="hospital")
    #@api.model
    def action_insert_pricelists(self):
        #with open('https://shaarani.odoo.com/surgi_pricelists/static/src/pricelists.csv', mode='r') as csv_file:
        text_file_path = get_module_resource('surgi_pricelists', 'static\\src\\', 'pricelists.csv')
        with open(text_file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            partener=None
            pricelist=[]
            x=0
            for row in csv_reader:
                raise UserError(row)
                if x>1:
                    break
                if row['id']:
                    x+=1
                    partener=self.env['res.partner'].search([('id','=',int(row['id']))])
                    partener.sudo().write({'hospitalpricelists':int(row['pricelist'])})
                    #if partener:
                    #    partener.create({'hospitalpricelists':pricelist})
                    #pricelist=[]
                    #partener=self.env['res.partner'].search([('id','=',row['id'])])
                    #pricelist.append(row['pricelist'])
                else:
                    partener.sudo().write({'hospitalpricelists':int(row['pricelist'])})
                _logger.debug('Create a %s with vals %s', partener.name, row['pricelist'])    
        return True            
    def write(self,vals):
        for rec in self:
            
            if 'hospitalpricelists' in vals:
                #raise UserError(str(vals['hospitalpricelists'][0]))
                listname=""
                if  len(rec.hospitalpricelists)<len(vals['hospitalpricelists'][0]):
                    #raise UserError(str(vals['hospitalpricelists']))
                    listname+="Add Price List "
                    if vals['hospitalpricelists'] and vals['hospitalpricelists'][0] and vals['hospitalpricelists'][0][-1]:
                        for c in vals['hospitalpricelists'][0][-1]:
                            if c not in rec.hospitalpricelists.ids:
                                listname+=self.env['product.pricelist'].search([('id','=',c)]).name+" , "
                    #listname+="Add Price List "+self.env['product.pricelist'].search([('id','=',vals['hospitalpricelists'][0][-1][-1])]).name   
                
                elif False in vals['hospitalpricelists'][0]:
                    listname+="Delete Price List "
                    z=0
                    #raise UserError(str(vals['hospitalpricelists'][0]))
                    for i in vals['hospitalpricelists'][0]:
                        
                        if i==False:
                            #raise UserError(str(rec.hospitalpricelists[z].name))
                            listname+=rec.hospitalpricelists[z].name+" , "

                        z+=1    


                    #listname="Delete Price List "+rec.hospitalpricelists[-1].name
                self.env['hospitallist_tracker'].create({
                    "description":str(listname),
                    "user":self.env.user.id,
                    "actiondate":datetime.datetime.now(),
                    'hospital':rec.id
                })
        return super(PriceListsSurgi, self).write(vals)         
    def unlink(self):
        
        for rec in self:
            self.env['pricelist_tracker'].create({
                "description":"delete price List "+rec.name,
                "user":self.env.user.id,
                "actiondate":datetime.datetime.now(),
                'hospital':rec.hospitalpricelists.id
            })
        super(HospitalListTracker, self).unlink()    
    #     #return res    
    #     pass
    
class HospitalListTracker(models.Model):
    _name="hospitallist_tracker"
    description=fields.Text("Detail")
    user=fields.Many2one(string="User",comodel_name="res.users")
    actiondate=fields.Datetime("Time Of Action")
    partener=fields.Many2one("product.pricelist",string="Price List")
    hospital=fields.Many2one("res.partner",string="Hospital Price List Item") 
            

class PriceListInhert(models.Model):
    _inherit = 'product.pricelist'
    _description = 'model.technical.name'
    product_line=fields.Many2one(string="Product Lines",comodel_name="product.lines")
    parentproductline=fields.Char(string="Parent Product Line",related='product_line.product_line_parent')
    paymenttype=fields.Selection([("Cash","Cash"),("Credit","Credit"),("Depit","Depit"),('cashpatient', 'Cash Patient'),('hospitalcash', 'Hospital Cash')],"Payment Type")
    #hospitalpricelistsrev=fields.Many2one(comodel_name="res.partner")
    hospitalpricelistsrev=fields.Many2many(
        string='Hospitals Price Lists',
        comodel_name='res.partner',
        relation='partner_pricelists_rel',
        column1='hospitalpricelists',
        column2='hospitalpricelistsrev',
    )
    op_type = fields.Selection([
        ('private', 'Private'),
        ('tender', 'Waiting List'),
        ('supply_order', 'Supply Order'),
    ], string='Type', default="private")
    tracker=fields.One2many(comodel_name="pricelist_tracker",inverse_name="pricelist")
    #@api.model
    def write(self, vals):
        str1=""
        for x,y in vals.items():
            #if str(type(y)) == "<type 'classobj'>":
            #raise UserError(str(y))
#             if isinstance(x,object):    
#                 #oldval=getattr(x,y)
#                 oldval=getattr(y,x)
#                 str1+=str(y)+" changed from "+str(oldval.name)+" to "+str(y[0][2])+" , "
#             else: 
              if self._fields[x].string not in ["Tracker","product.pricelist.item","Items"] and self._fields[x].string not in ["Items","Pricelist Items"]:
                oldval=getattr(self,x)
                #str1+=getattr(self,"name")+" changed from "+oldval+" to "+str(y)
                str1+=self._fields[x].string+" changed from "+str(oldval)+" to "+str(y)
        
        res = super(PriceListInhert, self).write(vals)
        #raise UserError('1 ..')
        if len(vals)>0:
            for rec in self:
                
                self.env['pricelist_tracker'].create({
                    "description":""+str1,
                    "user":self.env.user.id,
                    "actiondate":datetime.datetime.now(),
                    "pricelist":rec.id
                })
        
        return res
    

    
class ResUserInhirt(models.Model):
    _inherit = 'res.users'
    pricelisttrackerid=fields.One2many(comodel_name="pricelist_tracker",inverse_name="user")
    
    
    
class PriceListitemsInhert(models.Model):
    _inherit = 'product.pricelist.item'
    tracker=fields.One2many(comodel_name="pricelist_tracker",inverse_name="pricelistitem")
    def unlink(self):
        
        if self.pricelist_id:
            pricelist=self.pricelist_id.id
        else:
            pricelist=vals['pricelist_id']
        for rec in self:
            self.env['pricelist_tracker'].create({
                "description":"delete product "+rec.name,
                "user":self.env.user.id,
                "actiondate":datetime.datetime.now(),
                'pricelist':pricelist
            })
        super(PriceListitemsInhert, self).unlink()    
        #return res    
        pass
    @api.model
    def write(self, vals):
        str1=""
        for x,y in vals.items():
            if type(y) == "<type 'classobj'>":
                oldval=getattr(self,y)
                str1+=str(y)+" changed from "+str(oldval)+" to "+str(y[0][2])
            else:    
                oldval=getattr(self,x)
                str1+=str(x)+" changed from "+str(oldval)+" to "+str(y)
            #str1+=self._fields[x].string+" changed from "+str(oldval)+" to "+str(y)
        res = super(PriceListitemsInhert, self).write(vals)
        #raise UserError('2 ..')
        #for rec in self:
        if self.pricelist_id:
            pricelist=self.pricelist_id.id
        else:
            pricelist=vals['pricelist_id']
        self.env['pricelist_tracker'].create({
                "description":"change in "+self.name+""+str1,
                "user":self.env.user.id,
                "actiondate":datetime.datetime.now(),
                'pricelist':pricelist
            })
        return res    
    
    
class PriceListTracker(models.Model):
    _name="pricelist_tracker"
    description=fields.Text("Detail")
    user=fields.Many2one(string="User",comodel_name="res.users")
    actiondate=fields.Datetime("Time Of Action")
    pricelist=fields.Many2one("product.pricelist",string="Price List")
    pricelistitem=fields.Many2one("product.pricelist.item",string="Price List Item")


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    pricelist=fields.Many2one(string="Line PriceList",comodel_name="product.pricelist")
        
