# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "HR Attendance Reason - Employee Check In / Check Out Reason",
    "summary": """
        This module helps the Employees to log their Check In / Check Out Reasons while using attendance check in /  check out.
    """,
    "version": "14.0.1",
    "description": """
        This module helps the Employees to log their Check In / Check Out Reasons while using attendance check in /  check out.

    """,
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/attendance_reason.png"],
    "category": "Point of Sale",
    "depends": [
        "base",
        "hr_attendance"
    ],
    "data": [
        "security/ir.model.access.csv",
        # "views/assets.xml",
        "views/hr_attendance_reasons_view.xml",
        "views/hr_attendance_view.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],
    "assets":{
        "web.assets_backend" : [
            "attendance_reason/static/src/css/style.css",
            "attendance_reason/static/src/js/my_attendances.js",
            "attendance_reason/static/src/js/kiosk_confirm.js"
        ]
    },
    "installable": True,
    "application": True,
    "price"                 :  22.00,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
}
