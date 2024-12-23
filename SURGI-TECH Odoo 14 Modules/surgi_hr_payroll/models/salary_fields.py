# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class increment_contract(models.Model):
    _name = 'increment.contract'

    @api.model
    def year_selection(self):
        year = 1990  # replace 2000 with your a start year
        year_list = []
        while year != 2030:  # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list
    # @api.onchange('emp_contract')
    # def set_employee_name(self):
    #     for rec in self:
    #        if rec.emp_contract:
    #            rec.emp_contract_name = rec.emp_contract.employee_id


    @api.onchange('grade_id')
    def set_employee_name(self):
        for rec in self:
           if rec.grade_id:
               rec.grade_ids = rec.grade_id

    @api.onchange('rank_id')
    def set_employee_name(self):
        for rec in self:
           if rec.rank_id:
               rec.rank_ids = rec.rank_id

    @api.onchange('rang_id')
    def set_employee_name(self):
        for rec in self:
           if rec.rang_id:
               rec.rang_ids = rec.rang_id



    @api.depends('current_salary', 'amount_increment' )
    def _getsum_total_current_salary(self):
        for rec in self:
            rec.total_current_salary = rec.current_salary + rec.amount_increment


    grade_id = fields.Many2one('grade.grade')
    rank_id = fields.Many2one('rank.rank')
    rang_id = fields.Many2one('rang.rang')
    grade_ids = fields.Char(string='Grade' )
    rank_ids = fields.Char(string='Rank')
    rang_ids = fields.Char(string='Range')



    employee_id= fields.Many2one('hr.employee', string='employee')
    year_increment = fields.Selection(year_selection,string="Year" , default="2020")
    amount_increment = fields.Float(string="Increment Amount")
    increment_id= fields.Many2one('hr.contract',string='Employee increement', required=True)
    current_salary= fields.Float(string="Salary")
    total_empp_salary = fields.Float(string='Current Salary', related='increment_id.total_salary',store=True,readonly=True, forcesave=True ,ondelete='cascade',onchange=True,index=True)
    emp_contract = fields.Many2one('hr.employee')
    # emp_contract_name = fields.Char(string='Employee')

    total_current_salary = fields.Float('Total Salary with increment', compute='_getsum_total_current_salary')




    job_ides = fields.Many2one('hr.job',store=True, required=True , Create=False , string='Jop Position')












class HRjobincr(models.Model):
    _inherit = 'hr.job'

class hrempin(models.Model):
    _inherit = 'hr.employee'




class HrContract(models.Model):
    _inherit = 'hr.contract'

    # @api.depends('increase_2018', 'increase_2017', 'increase_2016', 'increase_2015', 'increase_2014')
    # def _getsum_increase_total(self):
    #     for rec in self:
    #         rec.increase_total = rec.increase_2018 + rec.increase_2017 + rec.increase_2016 + rec.increase_2015 + rec.increase_2014

    @api.depends('increase_2021','increase_2020','increase_2018', 'increase_2017', 'increase_2016', 'increase_2015', 'increase_2014')
    def _getsum_increase_total(self):
        for rec in self:
            rec.increase_total = rec.increase_2021 + rec.increase_2020 + rec.increase_2018 + rec.increase_2017 + rec.increase_2016 + rec.increase_2015 + rec.increase_2014

    @api.depends('advanced_incentive','standalone_incentive', 'variable_incentive', 'incentive_2021','incentive_2018', 'incentive_2017', 'incentive_2016', 'incentive_2015' ,'incentive_2014')
    def _getsum_incentive_total(self):
        for rec in self:
            rec.incentive_total = rec.advanced_incentive + rec.standalone_incentive + rec.variable_incentive + rec.incentive_2021 + rec.incentive_2018 + rec.incentive_2017 + rec.incentive_2016 + rec.incentive_2015 + rec.incentive_2014

    @api.depends('basic_salary', 'increase_total')
    def _getsum_salary_total_without_incentive(self):
        for rec in self:
            rec.total_salary_without_incentive = rec.basic_salary + rec.increase_total


    # @api.depends('basic_salary', 'increase_total','variable_incentive')
    # def _getsum_salary_total(self):
    #     for rec in self:
    #         rec.total_salary_without_incentive = rec.basic_salary + rec.increase_total + rec.incentive_total
    #
    @api.depends('total_salary_without_incentive', 'incentive_total')
    def _getsum_total_salary(self):
        for rec in self:
            rec.total_salary = rec.total_salary_without_incentive + rec.incentive_total

    basic_salary = fields.Float('Basic Wage',tracking=True,digits=dp.get_precision('Payroll'))
    basic_salary_precent = fields.Float('Basic Salary Precent',tracking=True,digits=dp.get_precision('Payroll'))
    increase_2021 = fields.Float('2021 Increase.', tracking=True, digits=dp.get_precision('Payroll'))
    increase_2018 = fields.Float('2018 Increase.',tracking=True,digits=dp.get_precision('Payroll'))
    increase_2017 = fields.Float('2017 Increase.',tracking=True,digits=dp.get_precision('Payroll'))
    increase_2016 = fields.Float('2016 Increase.',tracking=True,digits=dp.get_precision('Payroll'))
    increase_2015 = fields.Float('2015 Increase.',tracking=True,digits=dp.get_precision('Payroll'))
    increase_2014 = fields.Float('2014 Increase.',tracking=True,digits=dp.get_precision('Payroll'))

    increase_total = fields.Float('Total Increase',compute='_getsum_increase_total', tracking=True)#compute='_getsum_increase_total',

    total_salary_without_incentive = fields.Float('Total Basic salary without incentive',compute='_getsum_salary_total_without_incentive', tracking=True)#

    advanced_incentive = fields.Float('Odoo Incentive.', tracking=True,digits=dp.get_precision('Payroll'))
    standalone_incentive = fields.Float('Standalone Incentive.',tracking=True,digits=dp.get_precision('Payroll'))
    incentive_2021 = fields.Float('2021 Incentive.', tracking=True, digits=dp.get_precision('Payroll'))
    incentive_2018 = fields.Float('2018 Incentive.',tracking=True,digits=dp.get_precision('Payroll'))
    incentive_2017 = fields.Float('2017 Incentive.',tracking=True,digits=dp.get_precision('Payroll'))
    incentive_2016 = fields.Float('2016 Incentive.',tracking=True,digits=dp.get_precision('Payroll'))
    incentive_2015 = fields.Float('2015 Incentive.',tracking=True,digits=dp.get_precision('Payroll'))
    incentive_2014 = fields.Float('2014 Incentive.',tracking=True,digits=dp.get_precision('Payroll'))

    incentive_total = fields.Float('Total Incentive',compute='_getsum_incentive_total', tracking=True)#compute='_getsum_incentive_total',

    total_salary = fields.Float('Total Salary', compute='_getsum_total_salary', tracking=True)

    car_allow = fields.Float('Car Allowance',tracking=True,digits=dp.get_precision('Payroll'))
    fuel_allow = fields.Float('Fuel Allowance',tracking=True,digits=dp.get_precision('Payroll'))
    # trans_allow = fields.Float('Transportation',tracking=True,digits=dp.get_precision('Payroll'))
    trans_allow_mokattam = fields.Float('Transportation Mokattam',tracking=True,digits=dp.get_precision('Payroll'))
    trans_allow_bank = fields.Float('Transportation Bank',tracking=True,digits=dp.get_precision('Payroll'))
    travel_expenses_allow = fields.Float('Travel Exp Allow.',tracking=True,digits=dp.get_precision('Payroll'))
    hazard_pay = fields.Float('Hazard Pay',tracking=True,digits=dp.get_precision('Payroll'))
    travel_allow_int_f = fields.Float('Travel Allow internal Fixed',tracking=True,digits=dp.get_precision('Payroll'))
    advance_sales_comm = fields.Float('Advanced Sales Commissions',tracking=True,digits=dp.get_precision('Payroll'))
    advance_collection_comm = fields.Float('Advanced Collection Commissions',tracking=True,digits=dp.get_precision('Payroll'))
    mobi = fields.Float('Mobile',tracking=True,digits=dp.get_precision('Payroll'))
    housing = fields.Float('Housing Allowance',tracking=True,digits=dp.get_precision('Payroll'))
    nature = fields.Float('Nature Of Work',tracking=True,digits=dp.get_precision('Payroll'))
    increment_contract = fields.One2many('increment.contract', 'increment_id', string='Increment Emp Contract')

    extra_hour = fields.Float(string="Extra Hour", required=False, )
    inflation_incentive = fields.Float(string="Inflation Incentive", required=False, )
    increase_2020 = fields.Float(string="Increase 2020", required=False, )
    # increase_2021 = fields.Float('2021 Increase.',tracking=True, digits=dp.get_precision('Payroll'))
    ac_baha = fields.Float(string="A/C Dr. Baha", required=False, )
    variable_incentive = fields.Float(string="Variable Incentive 2020", required=False, )
