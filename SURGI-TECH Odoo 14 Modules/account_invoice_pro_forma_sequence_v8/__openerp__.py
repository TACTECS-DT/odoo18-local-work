# -*- coding: utf-8 -*-
# Copyright 2019 ALLA  Yoboue Parfait
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Pro forma invoice sequence",
    "summary": "Bind a sequence to pro-forma invoices",
    "version": "8.0",
    "sequence":1,
    "category": "Accounting",
    "website": "https://github.com/allan225/account_invoice_proforma_sequence_v8/tree/8.0"
               "account_invoice_pro_forma_sequence_v8",
    "author": "Parfait ALLA",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account.xml",
        "views/account_config_settings.xml",
        "views/account_invoice_workflow.xml",
        "views/account_report.xml"
    ]
}
