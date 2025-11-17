# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "GS Hr Attendance",
    "summary": "Module to check attendance",
    "author": "Gloobal Smart",
    "website": "https://gloobalsmart.com",
    "category": "Reporting",
    "version": "15.0.1.0.1",
    "depends": ["base", "hr_attendance",'report_xlsx'],
    "data":[
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/res_config_settings.xml',
        'views/hr_employee_inh.xml',
        'views/hr_attendance_inh.xml',
        'wizard/hr_attendance_report_wizard.xml',
        'report/report_report.xml',
    ],
    "demo": [""],
    "installable": True,
    "assets": {
    },
}
