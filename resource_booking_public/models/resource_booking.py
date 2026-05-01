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
    sale_order_ids = fields.One2many(
        "sale.order",
        inverse_name="booking_id",
        string="Sale Orders",
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

    def action_confirm(self):
        result = super().action_confirm()
        template = self.env.ref(
            "resource_booking_public.mail_template_booking_confirmation",
            raise_if_not_found=False,
        )
        if template:
            for booking in self:
                if booking.type_id.is_public and booking.partner_ids:
                    template.sudo().send_mail(
                        booking.id,
                        force_send=False,
                        email_layout_xmlid="mail.mail_notification_light",
                    )
        return result
