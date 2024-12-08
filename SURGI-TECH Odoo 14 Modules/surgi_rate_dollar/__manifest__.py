# -*- coding: utf-8 -*-
{
    'name': "Surgi Rate Dollar",
    'author': "Surgi",
    'category': 'Stock',
    'version': '14',

    'depends': ['base','stock','surgi_inventory_changes'],

    'data': [
        'security/ir.model.access.csv',
        'views/dollar_value.xml',
        'demo/dollar_rate.xml',
        'views/stock_quant.xml',
    ],

}
