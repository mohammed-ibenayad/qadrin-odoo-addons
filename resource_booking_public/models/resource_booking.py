# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResourceBooking(models.Model):
    _inherit = "resource.booking"

    anonymous_partner_name = fields.Char(
        string="Anonymous Bookee Name",
        help="Name of the anonymous person who made this booking.",
    )