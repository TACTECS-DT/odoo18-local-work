# -*- coding: utf-8 -*-
{
    'name': "Surgi Operation Tracking",

    'description': """
        Surgi Operation Tracking
    """,
    'author': "Surgi Tech",

    'category': 'Sales',
    'version': '14.0',

    'depends': ['base','surgi_operation','surgi_collection_rep'],

    'data': [
        'security/access_group.xml',
        'views/operation_tracking.xml',
        'views/operation.xml',
        # 'views/payment.xml',
    ],

}
