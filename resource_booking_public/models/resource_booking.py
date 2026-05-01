# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import secrets

from odoo import api, fields, models


def _default_access_token():
    return secrets.token_urlsafe(20)


class ResourceBooking(models.Model):
    _inherit = "resource.booking"

    manage_url = fields.Char(
        string="Manage Link",
        compute="_compute_manage_url",
    )

    @api.depends("access_token")
    def _compute_manage_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param(
            "web.base.url", default=""
        )
        for rec in self:
            if rec.access_token:
                rec.manage_url = "%s/book/manage/%s" % (base_url, rec.access_token)
            else:
                rec.manage_url = False

    @api.model_create_multi
    def create(self, vals_list):
        # access_token is inherited from portal.mixin but not auto-populated;
        # ensure every booking has one so the public manage URL works
        # immediately after creation.
        for vals in vals_list:
            if not vals.get("access_token"):
                vals["access_token"] = _default_access_token()
        return super().create(vals_list)
