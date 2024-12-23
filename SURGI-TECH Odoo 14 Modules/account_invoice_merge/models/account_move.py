# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2019 Okia SPRL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools import float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_invoice_key_cols_out(self):
        return [
            "partner_id",
            "move_type",
            "currency_id",
            "journal_id",
            "company_id",
            "bank_partner_id",
        ]

    @api.model
    def _get_invoice_key_cols_in(self):
        return [
            "partner_id",
            "move_type",
            "currency_id",
            "journal_id",
            "company_id",
            "bank_partner_id",
        ]

    @api.model
    def _get_invoice_line_key_cols(self):
        fields = [
            "discount",
            "tax_ids",
            "price_unit",
            "product_id",
            "account_id",
            "analytic_account_id",
            "product_uom_id",
        ]
        for field in ["sale_line_ids"]:
            if field in self.env["account.move.line"]._fields:
                fields.append(field)
        return fields

    @api.model
    def _get_first_invoice_fields(self, invoice):
        return {
            "invoice_origin": invoice.invoice_origin or "",
            "partner_id": invoice.partner_id.id,
            "journal_id": invoice.journal_id.id,
            "user_id": invoice.user_id.id,
            "currency_id": invoice.currency_id.id,
            "company_id": invoice.company_id.id,
            "move_type": invoice.move_type,
            # "account_id": invoice.account_id.id,
            "state": "draft",
            "ref": invoice.ref or "",
            "fiscal_position_id": invoice.fiscal_position_id.id,
            "invoice_payment_term_id": invoice.invoice_payment_term_id.id,
            "invoice_line_ids": {},
            "bank_partner_id": invoice.bank_partner_id.id,
        }

    def _get_draft_invoices(self):
        """Overridable function to return draft invoices to merge"""
        return self.filtered(lambda x: x.state == "draft")

    # flake8: noqa: C901 (is too complex)
    def do_merge(
        self, keep_references=True, date_invoice=False, remove_empty_invoice_lines=True,performa_seq=None
    ):
        """
        To merge similar type of account invoices.
        Invoices will only be merged if:
        * Account invoices are in draft
        * Account invoices belong to the same partner
        * Account invoices are have same company, partner, address, currency,
          journal, currency, salesman, account, move_type
        Lines will only be merged if:
        * Invoice lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param keep_references: If True, keep reference of original invoices

         @return: new account invoice id

        """

        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = br[field]
                if isinstance(field_val, models.BaseModel):
                    if br._fields.get(field).type in ("one2many", "many2many"):
                        field_val = tuple([(6, 0, tuple(field_val.ids))])
                    else:
                        field_val = field_val.id
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        # compute what the new invoices should contain
        new_invoices = {}
        seen_origins = {}
        seen_client_refs = {}

        for account_invoice in self._get_draft_invoices():
            if account_invoice.move_type in ("in_invoice", "in_refund"):
                invoice_key = make_key(account_invoice, self._get_invoice_key_cols_in())
            else:
                invoice_key = make_key(
                    account_invoice, self._get_invoice_key_cols_out()
                )
            new_invoice = new_invoices.setdefault(invoice_key, ({}, []))
            origins = seen_origins.setdefault(invoice_key, set())
            client_refs = seen_client_refs.setdefault(invoice_key, set())
            new_invoice[1].append(account_invoice.id)
            invoice_infos = new_invoice[0]
            if not invoice_infos:
                invoice_infos.update(self._get_first_invoice_fields(account_invoice))
                origins.add(account_invoice.invoice_origin)
                client_refs.add(account_invoice.ref)
            else:
                if (
                    account_invoice.invoice_origin
                    and account_invoice.invoice_origin not in origins
                ):
                    invoice_infos["invoice_origin"] = (
                        (invoice_infos["invoice_origin"] or "")
                        + " "
                        + account_invoice.invoice_origin
                    )
                    origins.add(account_invoice.invoice_origin)
                if account_invoice.ref and account_invoice.ref not in client_refs:
                    invoice_infos["ref"] = (
                        (invoice_infos["ref"] or "") + " " + account_invoice.ref
                    )
                    client_refs.add(account_invoice.ref)

            for invoice_line in account_invoice.invoice_line_ids:
                line_key = make_key(invoice_line, self._get_invoice_line_key_cols())

                o_line = invoice_infos["invoice_line_ids"].setdefault(line_key, {})

                if o_line:
                    # merge the line with an existing line
                    o_line["quantity"] += invoice_line.quantity
                else:
                    # append a new "standalone" line
                    o_line["quantity"] = invoice_line.quantity

        allinvoices = []
        allnewinvoices = []
        invoices_info = {}
        old_invoices = self.browse()
        qty_prec = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for _invoice_key, (invoice_data, old_ids) in new_invoices.items():
            # skip merges with only one invoice
            if len(old_ids) < 2:
                allinvoices += old_ids or []
                continue
            # cleanup invoice line data
            for key, value in invoice_data["invoice_line_ids"].items():
                value.update(dict(key))

            if remove_empty_invoice_lines:
                invoice_data["invoice_line_ids"] = [
                    (0, 0, value)
                    for value in invoice_data["invoice_line_ids"].values()
                    if not float_is_zero(value["quantity"], precision_digits=qty_prec)
                ]
            else:
                invoice_data["invoice_line_ids"] = [
                    (0, 0, value) for value in invoice_data["invoice_line_ids"].values()
                ]

            if date_invoice:
                invoice_data["date"] = date_invoice
            if performa_seq:
                invoice_data["account_performa_sequence"] = performa_seq
            # create the new invoice
            newinvoice = self.with_context(is_merge=True,stop_performa_sequence=True).create(invoice_data)
            invoices_info.update({newinvoice.id: old_ids})
            allinvoices.append(newinvoice.id)
            allnewinvoices.append(newinvoice)
            # cancel old invoices
            old_invoices = self.browse(old_ids)
            old_invoices.with_context(is_merge=True).button_cancel()

        # Make link between original sale order
        # None if sale is not installed
        invoice_line_obj = self.env["account.move.line"]
        for new_invoice_id in invoices_info:
            if "sale.order" in self.env.registry:
                sale_todos = old_invoices.mapped(
                    "invoice_line_ids.sale_line_ids.order_id"
                )
                for org_so in sale_todos:
                    for so_line in org_so.order_line:
                        invoice_line = invoice_line_obj.search(
                            [
                                ("id", "in", so_line.invoice_lines.ids),
                                ("move_id", "=", new_invoice_id),
                            ]
                        )
                        if invoice_line:
                            so_line.write({"invoice_lines": [(6, 0, invoice_line.ids)]})

        # recreate link (if any) between original analytic account line
        # (invoice time sheet for example) and this new invoice
        anal_line_obj = self.env["account.analytic.line"]
        if "move_id" in anal_line_obj._fields:
            for new_invoice_id in invoices_info:
                anal_todos = anal_line_obj.search(
                    [("move_id", "in", invoices_info[new_invoice_id])]
                )
                anal_todos.write({"move_id": new_invoice_id})

        for new_invoice in allnewinvoices:
            new_invoice._compute_amount()

        return invoices_info

