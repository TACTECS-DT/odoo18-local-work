# -*- coding: utf-8 -*-
{
    'name': "elearning student progress",

    'summary': """elearning student progress""",

    'description': """
       elearning student progress
       video
       school
       
    """,
    'author': 'David Montero Crespo',
    'license': 'AGPL-3',
    'category': 'Website',
    'version': '13.0',
'website': "https://softwareescarlata.com/",
    # any module necessary for this one to work correctly
    'images': ['static/description/1.png'],
    'depends': ['base','website_slides'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',

    ],
    'currency': 'EUR',
    'price': 20,
    # only loaded in demonstration mode

}