# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.parser import isoparse

from odoo.http import request, route

from odoo.addons.portal.controllers import portal


class PublicBooking(portal.CustomerPortal):

    def _get_public_type_by_token(self, token):
        if not token:
            return request.env["resource.booking.type"]
        return (
            request.env["resource.booking.type"]
            .sudo()
            .search(
                [("access_token", "=", token), ("is_public", "=", True)],
                limit=1,
            )
        )

    @route(
        ["/book/<string:token>", "/book/<string:token>/<int:year>/<int:month>"],
        type="http",
        auth="public",
        website=False,
    )
    def public_booking_page(
        self, token, year=None, month=None, error=None, **kwargs
    ):
        """Display public booking page with available slots."""
        type_obj = self._get_public_type_by_token(token)
        if not type_obj:
            return request.redirect("/")
        booking_sudo = (
            request.env["resource.booking"]
            .sudo()
            .new(
                {
                    "type_id": type_obj.id,
                    "duration": type_obj.duration,
                    "combination_auto_assign": True,
                }
            )
        )
        values = booking_sudo._get_calendar_context(year, month)
        values.update(
            {
                "booking_type": type_obj,
                "access_token": token,
                "error": error,
                "page_name": "public_booking",
            }
        )
        return request.render(
            "resource_booking_public.public_booking_page", values
        )

    @route(
        ["/book/<string:token>/confirm"],
        type="http",
        auth="public",
        methods=["POST"],
    )
    def public_booking_confirm(
        self, token, slot, name, email, phone=None, **kwargs
    ):
        """Process public booking form submission."""
        type_obj = self._get_public_type_by_token(token)
        if not type_obj:
            return request.redirect("/")
        slot_dt = isoparse(slot)
        slot_naive = datetime.utcfromtimestamp(slot_dt.timestamp())
        Partner = request.env["res.partner"].sudo()
        partner = Partner.search([("email", "=", email)], limit=1)
        if not partner:
            partner_vals = {"name": name, "email": email}
            if phone:
                partner_vals["phone"] = phone
            partner = Partner.create(partner_vals)
        elif not partner.name or partner.name == email.split("@")[0]:
            partner.name = name
            if phone:
                partner.phone = phone
        booking_sudo = (
            request.env["resource.booking"]
            .sudo()
            .create(
                {
                    "type_id": type_obj.id,
                    "partner_ids": [(4, partner.id)],
                    "anonymous_partner_name": name,
                    "start": slot_naive,
                    "combination_auto_assign": True,
                }
            )
        )
        booking_sudo.action_confirm()
        return request.render(
            "resource_booking_public.public_booking_success",
            {
                "booking_type": type_obj,
                "booking": booking_sudo,
            },
        )
