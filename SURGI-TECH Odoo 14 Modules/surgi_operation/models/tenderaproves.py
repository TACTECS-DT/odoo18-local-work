from odoo import fields, models, api, exceptions
from odoo.exceptions import  Warning
import logging
import inspect
_logger = logging.getLogger(__name__)
class ResUserTenderAproves(models.Model):
    _inherit = 'res.users'
    #tenderaprove=fields.Many2one(comodel_name="operation_tender_aproves")

class OperationsTenderAproves(models.Model):
    _inherit = 'operation.operation'
    
    def tender_aprove_admin(self):
        print("aaa")
        uid=self.env.user.id
        for rec in self:            
            for aprove in rec.tenderaprove:
                if uid==aprove.user.id:
                    aprove.write({"aproved":True})
    tenderaprove=fields.One2many(comodel_name="operation_tender_aproves",inverse_name="operation",string="Need Aprove")
    @api.model
    def create(self,vals):
        res= super(OperationsTenderAproves, self).create(vals)
        for rec in res:
            users = self.env.ref('surgi_operation.operations_tender_aprove').users
            if rec.operation_type.is_tender and not rec.tenderaprove:
                res.tenderaprove.unlink()
                _logger.info('------------------------>>>>>>>>'+str(type(res.id)))
                for user in users:
                    rec.tenderaprove.create({'operation':rec.id,'user':user.id})
            else:
                print("in else")
                #rec.tenderaprove.unlink()
                
        return res            
    @api.onchange('operation_type')
    def aprovetender(self):
        for rec in self:
            users = self.env.ref('surgi_operation.operations_tender_aprove').users
            if rec.operation_type.is_tender:
                rec.tenderaprove.unlink()
                _logger.info('------------------------>>>>>>>>'+str(type(rec.id)))
                if str(type(rec.id)) == "<class 'odoo.models.NewId'>":
                    opid=rec.id
                else:
                    opid=int(str(rec.id).strip('NewId_'))
                opid=self._origin.id
                print("a")
                for user in users:
                   
                    rec.tenderaprove.create({'operation':opid,'aproved':False,'user':user.id})
            else:
                print("")
#                 #rec.tenderaprove.unlink()    
class operation_tender_aproves(models.Model):
    _name = 'operation_tender_aproves'
    _description = 'operation_tender_aproves'
    aproved=fields.Boolean("Aproved")
    username=fields.Char("Aprover",related='user.name')
    user=fields.Many2one(comodel_name="res.users",string="Aprover")
    operation=fields.Many2one(comodel_name="operation.operation",string="Aprover")


    

    

    

    
    
