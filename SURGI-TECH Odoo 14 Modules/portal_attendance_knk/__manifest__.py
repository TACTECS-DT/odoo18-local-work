# -*- coding: utf-8 -*-
#################################################################################
# Author      : Kanak Infosystems LLP. (<https://www.kanakinfosystems.com/>)
# Copyright(c): 2012-Present Kanak Infosystems LLP.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.kanakinfosystems.com/license>
#################################################################################

{
    'name': 'Portal Employee Attendance',
    'version': '14.0',
    'summary': 'Portal Attendance Using this module user can see their attendance and also mark their attendance from portal as well.| Portal attendance | Portal Attendance filter | Portal Attendance groupby | Online Attendance | Portal attendance list | Website Attendance | Employee attendance | Website employee | Employee attendance | Employee Check In | Employee Checkout | Mobile attendance | Attendance Kiosk',
    'description': "Employee can see their attendance.Using filters Employee can easily find the attendance.Employee can also search the attendance.",
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'category': 'website',
    'depends': ['base', 'portal', 'website', 'web', 'hr', 'hr_attendance', 'emp_attendance_google_map_app',
                'ah_em_attendence_map', 'portal_custom'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/knk_res_config_view.xml',
        'views/pwa.xml',
        'views/templates.xml',
        'views/users.xml',

    ],
    'external_dependencies': {
        'python': ['googlegeocoder', 'googlemaps', 'geopy'],
    },
    'qweb': [
        "static/src/xml/pwa_install.xml",
        "static/src/xml/attendance.xml",
    ],
    'images': ['static/description/banner.gif'],
    'application': True,
    'price': 130,
    'currency': 'EUR',
}
