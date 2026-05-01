# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    booking_id = fields.Many2one(
        "resource.booking",
        string="Resource Booking",
        ondelete="set null",
        index=True,
        copy=False,
    )

    def action_confirm(self):
        result = super().action_confirm()
        for order in self:
            booking = order.booking_id
            if booking and booking.state in ("pending", "scheduled"):
                booking.sudo().action_confirm()
        return result
