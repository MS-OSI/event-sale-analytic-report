# -*- coding: utf-8 -*-

from odoo import fields, models, tools


class EventSaleReport(models.Model):
    _inherit = "event.sale.report"

    stage_id = fields.Many2one("event.stage", readonly=True)
    product_category_id = fields.Many2one("product.category", readonly=True)
    # ==== Analytic fields ====
    account_id = fields.Many2one(
        "account.analytic.account", string="Analytic account", readonly=True
    )
    analytic_amount = fields.Float("Analytic amount", readonly=True)

    # ==== Event duration (in hours) ====
    event_duration = fields.Float("Event Duration (Hours)", readonly=True)

    def _select_clause(self, *select):
        return super()._select_clause(
            """
            event_event.stage_id AS stage_id,
            template.categ_id AS product_category_id,
            aal.account_id AS account_id,
            (aal.amount / NULLIF(sol_reg_count.count, 0)) AS analytic_amount,
            (ROUND(EXTRACT(EPOCH FROM (event_event.date_end - event_event.date_begin)) / NULLIF(sol_reg_count.count * 3600.0, 0), 2)) AS event_duration
            """,
            *select
        )

    def _from_clause(self, *join_):
        return super()._from_clause(
            """
            LEFT JOIN product_product product ON sale_order_line.product_id = product.id
            LEFT JOIN product_template template ON product.product_tmpl_id = template.id
            LEFT JOIN product_category category ON template.categ_id = category.id
            LEFT JOIN sale_order_line_invoice_rel rel ON rel.order_line_id = sale_order_line.id 
            LEFT JOIN account_move_line aml ON aml.id = rel.invoice_line_id
            LEFT JOIN account_analytic_line aal ON aal.move_line_id = aml.id
            LEFT JOIN LATERAL (
                SELECT COUNT(*) AS count
                FROM event_registration erc
                WHERE erc.sale_order_line_id = sale_order_line.id
            ) sol_reg_count ON TRUE
            """,
            *join_
        )
