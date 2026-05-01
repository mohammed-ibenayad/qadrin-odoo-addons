# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.parser import isoparse

from odoo import fields, models
from odoo.exceptions import ValidationError
from odoo.http import request, route

from odoo.addons.portal.controllers import portal


class PublicBooking(portal.CustomerPortal):

    @route(
        ["/book/<int:type_id>", "/book/<int:type_id>/<int:year>/<int:month>"],
        type="http",
        auth="public",
    )
    def public_booking_page(
        self, type_id, year=None, month=None, error=None, **kwargs
    ):
        """Display public booking page with available slots."""
        type_obj = request.env["resource.booking.type"].sudo().browse(type_id)
        if not type_obj.exists() or not type_obj.is_public:
            return request.redirect("/")
        # Create a temporary booking record to use _get_available_slots()
        booking_sudo = (
            request.env["resource.booking"]
            .sudo()
            .new(
                {
                    "type_id": type_id,
                    "duration": type_obj.duration,
                    "combination_auto_assign": True,
                }
            )
        )
        values = booking_sudo._get_calendar_context(year, month)
        values.update(
            {
                "booking_type": type_obj,
                "error": error,
                "page_name": "public_booking",
            }
        )
        return request.render(
            "resource_booking_public.public_booking_page", values
        )

    @route(
        ["/book/<int:type_id>/confirm"],
        type="http",
        auth="public",
        methods=["POST"],
    )
    def public_booking_confirm(self, type_id, slot, name, email, phone=None, **kwargs):
        """Process public booking form submission."""
        type_obj = request.env["resource.booking.type"].sudo().browse(type_id)
        if not type_obj.exists() or not type_obj.is_public:
            return request.redirect("/")
        # Parse slot datetime
        slot_dt = isoparse(slot)
        slot_naive = datetime.utcfromtimestamp(slot_dt.timestamp())
        # Find or create partner by email
        Partner = request.env["res.partner"].sudo()
        partner = Partner.search([("email", "=", email)], limit=1)
        if not partner:
            partner_vals = {"name": name, "email": email}
            if phone:
                partner_vals["phone"] = phone
            partner = Partner.create(partner_vals)
        elif not partner.name or partner.name == email.split("@")[0]:
            # Update name if it was auto-generated from email
            partner.name = name
            if phone:
                partner.phone = phone
        # Create booking with sudo (public user cannot create normally)
        booking_sudo = (
            request.env["resource.booking"]
            .sudo()
            .create(
                {
                    "type_id": type_id,
                    "partner_ids": [(4, partner.id)],
                    "anonymous_partner_name": name,
                    "start": slot_naive,
                    "combination_auto_assign": True,
                }
            )
        )
        # _sync_meeting() was called in create(), now confirm immediately
        booking_sudo.action_confirm()
        return request.render(
            "resource_booking_public.public_booking_success",
            {
                "booking_type": type_obj,
                "booking": booking_sudo,
            },
        )