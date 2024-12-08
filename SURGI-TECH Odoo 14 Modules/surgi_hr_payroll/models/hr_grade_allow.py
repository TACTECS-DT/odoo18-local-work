# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class GradeGrade(models.Model):
    _inherit = "grade.grade"

    # for specific Salary
    max_salary = fields.Float(string="MAX Salary")
    min_salary = fields.Float(string="MIN Salary")
    # Fixed Allowance
    ## for indoor allowance
    car_allow_in = fields.Float(string="Car Allow")
    driver_rep_allow_in = fields.Float(string='Driver and Rep Allow')
    benzene_allow_in = fields.Float(string="Benzene Allow")
    transport_allow_in = fields.Float(string="Transport Allow")
    transport_to_bank_allow_in = fields.Float(string="Transport Allow To Banks")
    travel_exp_allow_in = fields.Float(string="Travel Exp Allow")
    fix_internal_travel_exp_allow_in = fields.Float(string="Travel Allow Internal")
    housing_allow_in = fields.Float(string="Housing Allowance")
    risk_allow_in = fields.Float(string="Risk Allowance")
    extra_hours_work_allow_in = fields.Float(string="Extra Work Allow")
    fix_collection_comm_allow_in = fields.Float(string="Advanced Collections Commissions")
    fix_sales_comm_allow_in = fields.Float(string="Advanced Sales Commissions")

    ## for outdoor allowance
    car_allow_out = fields.Float(string="Car Allow")
    driver_rep_allow_out = fields.Float(string='Driver and Rep Allow')
    benzene_allow_out = fields.Float(string="Benzene Allow")
    transport_allow_out = fields.Float(string="Transport Allow")
    transport_to_bank_allow_out = fields.Float(string="Transport Allow To Banks")
    travel_exp_allow_out = fields.Float(string="Travel Exp Allow")
    fix_internal_travel_exp_allow_out = fields.Float(string="Travel Allow Internal")
    housing_allow_out = fields.Float(string="Housing Allowance")
    risk_allow_out = fields.Float(string="Risk Allowance")
    extra_hours_work_allow_out = fields.Float(string="Extra Work Allow")
    fix_collection_comm_allow_out = fields.Float(string="Advanced Collections Commissions")
    fix_sales_comm_allow_out = fields.Float(string="Advanced Sales Commissions")

    # Variable Allowance
    var_internal_travel_exp_allow = fields.Float(string="Travel Allow Internal")
    var_external_travel_reward_allow = fields.Float(string="External Travel Reward Allow")
    var_accomod_allow = fields.Float(string="Accomod Allow")
    var_overtime_allow = fields.Float(string="Over Time Allow")
    var_collection_comm_allow = fields.Float(string="Collections Commissions")
    var_sales_comm_allow = fields.Float(string="Sales Commissions")
    var_manufacturing_comm_allow = fields.Float(string="Manufacturing Commissions")
    var_night_shift_allow = fields.Float(string="Night Shifts")


## for read only fields in cotract
class HrContract(models.Model):
    _inherit = "hr.contract"

    ## for indoor allowance
    car_allow_in = fields.Float(string="Car Allow", related='grade_id.car_allow_in', store=True)
    driver_rep_allow_in = fields.Float(string='Driver and Rep Allow', related='grade_id.driver_rep_allow_in', store=True)
    benzene_allow_in = fields.Float(string="Benzene Allow", related='grade_id.benzene_allow_in', store=True)
    transport_allow_in = fields.Float(string="Transport Allow", related='grade_id.transport_allow_in', store=True)
    transport_to_bank_allow_in = fields.Float(string="Transport Allow To Banks", related='grade_id.transport_to_bank_allow_in', store=True)
    travel_exp_allow_in = fields.Float(string="Travel Exp Allow", related='grade_id.travel_exp_allow_in', store=True)
    fix_internal_travel_exp_allow_in = fields.Float(string="Travel Allow Internal", related='grade_id.fix_internal_travel_exp_allow_in', store=True)
    housing_allow_in = fields.Float(string="Housing Allowance", related='grade_id.housing_allow_in', store=True)
    risk_allow_in = fields.Float(string="Risk Allowance", related='grade_id.risk_allow_in', store=True)
    extra_hours_work_allow_in = fields.Float(string="Extra Work Allow", related='grade_id.extra_hours_work_allow_in', store=True)
    fix_collection_comm_allow_in = fields.Float(string="Advanced Collections Commissions", related='grade_id.fix_collection_comm_allow_in', store=True)
    fix_sales_comm_allow_in = fields.Float(string="Advanced Sales Commissions", related='grade_id.fix_sales_comm_allow_in', store=True)

    ## for outdoor allowance
    car_allow_out = fields.Float(string="Car Allow", related='grade_id.car_allow_out', store=True)
    driver_rep_allow_out = fields.Float(string='Driver and Rep Allow', related='grade_id.driver_rep_allow_out', store=True)
    benzene_allow_out = fields.Float(string="Benzene Allow", related='grade_id.benzene_allow_out', store=True)
    transport_allow_out = fields.Float(string="Transport Allow", related='grade_id.transport_allow_out', store=True)
    transport_to_bank_allow_out = fields.Float(string="Transport Allow To Banks", related='grade_id.transport_to_bank_allow_out', store=True)
    travel_exp_allow_out = fields.Float(string="Travel Exp Allow", related='grade_id.travel_exp_allow_out', store=True)
    fix_internal_travel_exp_allow_out = fields.Float(string="Travel Allow Internal", related='grade_id.fix_internal_travel_exp_allow_out', store=True)
    housing_allow_out = fields.Float(string="Housing Allowance", related='grade_id.housing_allow_out', store=True)
    risk_allow_out = fields.Float(string="Risk Allowance", related='grade_id.risk_allow_out', store=True)
    extra_hours_work_allow_out = fields.Float(string="Extra Work Allow", related='grade_id.extra_hours_work_allow_out', store=True)
    fix_collection_comm_allow_out = fields.Float(string="Advanced Collections Commissions", related='grade_id.fix_collection_comm_allow_out', store=True)
    fix_sales_comm_allow_out = fields.Float(string="Advanced Sales Commissions", related='grade_id.fix_sales_comm_allow_out', store=True)

    # Variable Allowance
    var_internal_travel_exp_allow = fields.Float(string="Travel Allow Internal", related='grade_id.var_internal_travel_exp_allow', store=True)
    var_external_travel_reward_allow = fields.Float(string="External Travel Reward Allow", related='grade_id.var_external_travel_reward_allow', store=True)
    var_accomod_allow = fields.Float(string="Accomod Allow", related='grade_id.var_accomod_allow', store=True)
    var_overtime_allow = fields.Float(string="Over Time Allow", related='grade_id.var_overtime_allow', store=True)
    var_collection_comm_allow = fields.Float(string="Collections Commissions", related='grade_id.var_collection_comm_allow', store=True)
    var_sales_comm_allow = fields.Float(string="Sales Commissions", related='grade_id.var_sales_comm_allow', store=True)
    var_manufacturing_comm_allow = fields.Float(string="Manufacturing Commissions", related='grade_id.var_manufacturing_comm_allow', store=True)
    var_night_shift_allow = fields.Float(string="Night Shifts", related='grade_id.var_night_shift_allow', store=True)