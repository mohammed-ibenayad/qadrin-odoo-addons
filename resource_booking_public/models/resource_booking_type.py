# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResourceBookingType(models.Model):
    _inherit = "resource.booking.type"

    is_public = fields.Boolean(
        string="Public Booking",
        default=False,
        help="If checked, this booking type can be booked via public link "
        "without requiring portal/login access.",
    )
    public_warning_msg = fields.Html(
        string="Public Booking Warning",
        translate=True,
        help="Optional warning message displayed on the public booking page "
        "(e.g., cancellation policy, terms of service).",
    )