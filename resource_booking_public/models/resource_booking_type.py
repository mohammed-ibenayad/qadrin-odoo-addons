# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import secrets

from odoo import api, fields, models


def _default_access_token():
    return secrets.token_urlsafe(20)


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
    access_token = fields.Char(
        string="Access Token",
        copy=False,
        readonly=True,
        default=lambda self: _default_access_token(),
        help="Secret token used in the public share URL. "
        "Regenerate it to invalidate previously shared links.",
    )
    public_url = fields.Char(
        string="Public Share Link",
        compute="_compute_public_url",
    )

    @api.depends("access_token", "is_public")
    def _compute_public_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param(
            "web.base.url", default=""
        )
        for rec in self:
            if rec.is_public and rec.access_token:
                rec.public_url = "%s/book/%s" % (base_url, rec.access_token)
            else:
                rec.public_url = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("access_token"):
                vals["access_token"] = _default_access_token()
        return super().create(vals_list)

    def action_regenerate_access_token(self):
        for rec in self:
            rec.access_token = _default_access_token()
        return True
