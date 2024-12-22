from odoo import fields, models, api
import pytz
from datetime import datetime


class ReportTemplate(models.TransientModel):
    _name = 'setu.inventory.reporting.template'
    _description = 'Setu Inventory Reporting Template'

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product"
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse"
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location"
    )
    theoretical_qty = fields.Float(
        string="Theoretical Quantity"
    )
    counted_qty = fields.Float(
        string="Counted Quantity"
    )
    discrepancy_qty = fields.Float(
        string="Discrepancy Quantity"
    )
    inventory_count_date = fields.Date(
        string="Inventory Count Date"
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User"
    )

    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Users"
    )
    warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse",
        string="Warehouses"
    )
    location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Locations"
    )
    start_date = fields.Date(
        string="Start Date"
    )
    end_date = fields.Date(
        string="End Date"
    )


class InvCountReport(models.TransientModel):
    _name = 'inventory.count.report'
    _inherit = 'setu.inventory.reporting.template'
    _description = 'Inventory Count Report'

    count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        string="Count"
    )

    @api.onchange('user_ids')
    def onchange_user_ids(self):
        users = self.sudo().env.ref('setu_inventory_count_management_18.group_setu_inventory_count_manager').users
        ids = users.ids if users else []
        return {'domain': {'user_ids': [('id', 'in', ids)]}}

    def generate_report(self):
        location_ids = False
        warehouse_ids = False
        user_ids = False
        if self.location_ids:
            location_ids = 'ARRAY' + str(self.location_ids.ids)
        if self.warehouse_ids:
            warehouse_ids = 'ARRAY' + str(self.warehouse_ids.ids)
        if self.user_ids:
            user_ids = 'ARRAY' + str(self.user_ids.ids)
        where_query = get_dynamic_query(
            'count_line.location_id', location_ids,
            'cou.approver_id', user_ids,
            'cou.warehouse_id', warehouse_ids
        )
        start_date = '1990-01-01'
        end_date = '2100-01-01'

        local_timezone = self.env.context.get('tz', 'UTC')
        if self.start_date:
            start_date = str(self.start_date)#change_time_zone(local_timezone, str(self.start_date) + ' 00:00:00')
        if self.end_date:
            end_date = str(self.end_date)#change_time_zone(local_timezone, str(self.end_date) + ' 23:59:59')
        self._cr.execute('delete from inventory_count_report;')
        query = f"""
       select 
            count_line.product_id,
            cou.warehouse_id,
            count_line.location_id,
            cou.inventory_count_date,
            max(coalesce(count_line.qty_in_stock,0))as theoretical_qty,
            max(coalesce(count_line.counted_qty,0)) as counted_qty,
            abs(max(coalesce(count_line.qty_in_stock,0)) - max(coalesce(count_line.counted_qty,0))) as discrepancy_qty, 
            cou.approver_id as user_id,
            cou.id as count_id

        from setu_stock_inventory_count_line count_line
        inner join setu_stock_inventory_count cou on cou.id = count_line.inventory_count_id
        where cou.state in ('Inventory Adjusted','Approved')
        and count_line.is_discrepancy_found = 't'
        and cou.inventory_count_date::date >= '{str(start_date)}' and cou.inventory_count_date::date <= '{str(end_date)}'
        {where_query}
        group by
            count_line.product_id,
            cou.warehouse_id,
            count_line.location_id,
            cou.inventory_count_date,
            cou.approver_id,
            cou.id;
        """
        self._cr.execute(query)
        data_list = self._cr.dictfetchall()
        for data in data_list:
            self.create({
                'product_id': data['product_id'],
                'warehouse_id': data['warehouse_id'],
                'location_id': data['location_id'],
                'inventory_count_date': data['inventory_count_date'],
                'theoretical_qty': data['theoretical_qty'],
                'counted_qty': data['counted_qty'],
                'discrepancy_qty': data['discrepancy_qty'],
                'user_id': data['user_id'],
                'count_id': data['count_id']
            })
        action = self.sudo().env.ref('setu_inventory_count_management_18.inventory_count_report_act_window').read()[0]
        return action


class InvAdjustmentReport(models.TransientModel):
    _name = 'inventory.adjustment.report'
    _inherit = 'setu.inventory.reporting.template'
    _description = 'Inventory Adjustment Report'

    count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        string="Count"
    )
    adjustment_type = fields.Selection(
        [('IN', 'IN'),
         ('OUT', 'OUT')],
        string="Adjustment Type"
    )

    @api.onchange('user_ids')
    def onchange_user_ids(self):
        users = self.sudo().env.ref('setu_inventory_count_management_18.group_setu_inventory_count_manager').users
        ids = users.ids if users else []
        return {'domain': {'user_ids': [('id', 'in', ids)]}}

    def generate_report(self):
        location_ids = False
        warehouse_ids = False
        user_ids = False
        if self.location_ids:
            location_ids = 'ARRAY' + str(self.location_ids.ids)
        if self.warehouse_ids:
            warehouse_ids = 'ARRAY' + str(self.warehouse_ids.ids)
        if self.user_ids:
            user_ids = 'ARRAY' + str(self.user_ids.ids)
        where_query = get_dynamic_query(
            'count_line.location_id', location_ids,
            'cou.approver_id', user_ids,
            'cou.warehouse_id', warehouse_ids
        )
        start_date = '1990-01-01'
        end_date = '2100-01-01'

        local_timezone = self.env.context.get('tz', 'UTC')
        if self.start_date:
            start_date = str(self.start_date)#change_time_zone(local_timezone, str(self.start_date) + ' 00:00:00')
        if self.end_date:
            end_date = str(self.end_date)#change_time_zone(local_timezone, str(self.end_date) + ' 23:59:59')
        self._cr.execute('delete from inventory_adjustment_report;')
        query = f"""
        select 
            count_line.product_id,
            cou.warehouse_id,
            count_line.location_id,
            si.date as adjustment_date,
            max(coalesce(count_line.qty_in_stock,0))as theoretical_qty,
            max(coalesce(count_line.counted_qty,0)) as counted_qty,
            abs(max(coalesce(count_line.qty_in_stock,0)) - max(coalesce(count_line.counted_qty,0))) as discrepancy_qty, 
            cou.approver_id as user_id,
            cou.id as count_id,
            case when coalesce(count_line.qty_in_stock,0) > coalesce(count_line.counted_qty,0) then 'OUT' else 'IN' end as adjustment_type

        from setu_stock_inventory_count_line count_line
        inner join setu_stock_inventory_count cou on cou.id = count_line.inventory_count_id
        inner join setu_stock_inventory si on si.inventory_count_id = cou.id  
        where cou.state = 'Inventory Adjusted'
        and count_line.is_discrepancy_found = 't'
        and si.date::date >= '{str(start_date)}' and si.date::date <= '{str(end_date)}'
        {where_query}
        group by
            count_line.product_id,
            cou.warehouse_id,
            count_line.location_id,
            si.date,
            cou.approver_id,
            cou.id,
            adjustment_type;
        """
        self._cr.execute(query)
        data_list = self._cr.dictfetchall()
        for data in data_list:
            self.create({
                'product_id': data['product_id'],
                'warehouse_id': data['warehouse_id'],
                'location_id': data['location_id'],
                'inventory_count_date': data['adjustment_date'],
                'theoretical_qty': data['theoretical_qty'],
                'counted_qty': data['counted_qty'],
                'discrepancy_qty': data['discrepancy_qty'],
                'user_id': data['user_id'],
                'count_id': data['count_id'],
                'adjustment_type': data['adjustment_type']
            })
        action = self.sudo().env.ref('setu_inventory_count_management_18.inventory_adjustment_report_act_window').read()[0]
        return action


class InvUserStatesReport(models.TransientModel):
    _name = 'inventory.user.states.report'
    _inherit = 'setu.inventory.reporting.template'
    _description = 'Inventory User Statistics Report'

    discrepancy_ratio = fields.Float(
        string="Discrepancy"
    )
    user_mistake_ratio = fields.Float(
        string="Calculation Mistake"
    )
    sessions = fields.Integer(
        string="Total Sessions"
    )

    def generate_report(self):
        self._cr.execute('delete from inventory_user_states_report;')
        query = """
        with mix_data as(
            select
                unnest(users) as user_id,
                --discrepancy,
                user_mistake,
                product_id,
                session_id
            from
                (select 
                    --bool_or(is_discrepancy_found)as discrepancy,
                    bool_or(user_calculation_mistake)as user_mistake,
                    product_id,
                    session_id,
                    users 
                from 
                    (select 
                        sl.id as line_id,
                        ses.id as session_id,
                        sl.product_id,
                        array_agg(rel.res_users_id) as users,
                        --sl.is_discrepancy_found,
                        sl.user_calculation_mistake
                    from 
                        setu_inventory_count_session_line sl
                        inner join setu_inventory_count_session ses on ses.id = sl.session_id and ses.state = 'Done'
                        inner join res_users_setu_inventory_count_session_rel rel on ses.id = setu_inventory_count_session_id
                        group by sl.id,ses.id,sl.product_id
                        order by sl.product_id
                    )session_lines
                group by 
                    product_id,
                    session_id,
                    users)data
        )
        select 
            user_id,
            --(select count(md2.*) from mix_data md2 where md2.user_id = md.user_id and md2.discrepancy = true)::float*100/
            --(select count(*) from mix_data where user_id = md.user_id)::float as discrepancy_ratio,
            (select count(md2.*) from mix_data md2 where md2.user_id = md.user_id and md2.user_mistake = true)::float*100/
            (select count(*) from mix_data where user_id = md.user_id)::float as user_mistake_ratio,
            count(distinct session_id) as sessions
        from 
            mix_data md
        group by 
            user_id;
        """
        self._cr.execute(query)
        data_list = self._cr.dictfetchall()
        for data in data_list:
            self.create({
                'user_id': data['user_id'],
                'user_mistake_ratio': round(data['user_mistake_ratio'], 2),
                'sessions': data['sessions'],
            })
        action = self.sudo().env.ref('setu_inventory_count_management_18.inventory_user_states_report_act_window').read()[0]
        return action


def get_dynamic_query(location, location_ids, user, user_ids, warehouse, warehouse_ids):
    where_query = ''
    if location_ids:
        where_query += f"""and  1 = case when array_length({location_ids},1) >= 1 then
                    case when {location} = ANY({location_ids}) then 1 else 0 end
                    else 1 end
"""
    if user_ids:
        where_query += f"""and 1 = case when array_length({user_ids},1) >= 1 then
                        case when {user} = ANY({user_ids}) then 1 else 0 end
                        else 1 end
"""
    if warehouse_ids:
        where_query += f"""and 1 = case when array_length({warehouse_ids},1) >= 1 then
                        case when {warehouse} = ANY({warehouse_ids}) then 1 else 0 end
                        else 1 end
"""
    return where_query


def change_time_zone(local_timezone, datetime_obj):
    local_timezone = pytz.timezone(local_timezone)
    datetime_obj = datetime.strptime(f"{datetime_obj}", "%Y-%m-%d %H:%M:%S")
    local_dt = local_timezone.localize(datetime_obj, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt
