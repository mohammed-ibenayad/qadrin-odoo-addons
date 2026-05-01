# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.parser import isoparse

from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request, route

from odoo.addons.portal.controllers import portal


class PublicBooking(portal.CustomerPortal):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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

    def _get_booking_by_token(self, token):
        if not token:
            return request.env["resource.booking"]
        booking = (
            request.env["resource.booking"]
            .sudo()
            .search([("access_token", "=", token)], limit=1)
        )
        if booking and not booking.type_id.is_public:
            return request.env["resource.booking"]
        return booking

    def _calendar_values(self, booking_type, year=None, month=None):
        booking_sudo = (
            request.env["resource.booking"]
            .sudo()
            .new(
                {
                    "type_id": booking_type.id,
                    "duration": booking_type.duration,
                    "combination_auto_assign": True,
                }
            )
        )
        return booking_sudo._get_calendar_context(year, month)

    def _parse_slot(self, slot):
        slot_dt = isoparse(slot)
        return datetime.utcfromtimestamp(slot_dt.timestamp())

    def _upsert_partner(self, name, email, phone=None):
        Partner = request.env["res.partner"].sudo()
        partner = Partner.search([("email", "=", email)], limit=1)
        if not partner:
            vals = {"name": name, "email": email}
            if phone:
                vals["phone"] = phone
            partner = Partner.create(vals)
        elif not partner.name or partner.name == email.split("@")[0]:
            partner.name = name
            if phone and not partner.phone:
                partner.phone = phone
        return partner

    # ------------------------------------------------------------------
    # Step 1 — Date & time
    # ------------------------------------------------------------------

    @route(
        ["/book/<string:token>", "/book/<string:token>/<int:year>/<int:month>"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def public_booking_calendar(
        self, token, year=None, month=None, error=None, **kwargs
    ):
        booking_type = self._get_public_type_by_token(token)
        if not booking_type:
            return request.redirect("/")
        values = self._calendar_values(booking_type, year, month)
        values.update(
            {
                "booking_type": booking_type,
                "access_token": token,
                "step": "date",
                "form_action": "/book/%s/details" % token,
                "calendar_url_pattern": "/book/%s" % token,
                "error": error,
                "page_name": "public_booking",
            }
        )
        return request.render(
            "resource_booking_public.public_booking_calendar", values
        )

    # ------------------------------------------------------------------
    # Step 2 — Details
    # ------------------------------------------------------------------

    @route(
        ["/book/<string:token>/details"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def public_booking_details(
        self, token, slot=None, name=None, email=None, phone=None, **kwargs
    ):
        booking_type = self._get_public_type_by_token(token)
        if not booking_type:
            return request.redirect("/")
        if not slot:
            return request.redirect("/book/%s" % token)
        selected_slot = self._parse_slot(slot)
        return request.render(
            "resource_booking_public.public_booking_details",
            {
                "booking_type": booking_type,
                "access_token": token,
                "step": "details",
                "selected_slot": selected_slot,
                "slot": slot,
                "name": name or "",
                "email": email or "",
                "phone": phone or "",
                "form_action": "/book/%s/confirm" % token,
                "back_url": "/book/%s" % token,
                "page_name": "public_booking",
            },
        )

    # ------------------------------------------------------------------
    # Step 3 — Confirm (creates the booking)
    # ------------------------------------------------------------------

    @route(
        ["/book/<string:token>/confirm"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def public_booking_confirm(
        self, token, slot, name, email, phone=None, **kwargs
    ):
        booking_type = self._get_public_type_by_token(token)
        if not booking_type:
            return request.redirect("/")
        slot_naive = self._parse_slot(slot)
        partner = self._upsert_partner(name, email, phone)
        try:
            booking_sudo = (
                request.env["resource.booking"]
                .sudo()
                .create(
                    {
                        "type_id": booking_type.id,
                        "partner_ids": [(4, partner.id)],
                        "start": slot_naive,
                        "combination_auto_assign": True,
                    }
                )
            )
            booking_sudo.action_confirm()
        except (UserError, ValidationError) as exc:
            return request.render(
                "resource_booking_public.public_booking_details",
                {
                    "booking_type": booking_type,
                    "access_token": token,
                    "step": "details",
                    "selected_slot": slot_naive,
                    "slot": slot,
                    "name": name,
                    "email": email,
                    "phone": phone or "",
                    "form_action": "/book/%s/confirm" % token,
                    "back_url": "/book/%s" % token,
                    "error": exc.args[0] if exc.args else _("Could not confirm booking."),
                    "page_name": "public_booking",
                },
            )
        return request.redirect("/book/manage/%s" % booking_sudo.access_token)

    # ------------------------------------------------------------------
    # Manage — view, reschedule, cancel
    # ------------------------------------------------------------------

    @route(
        ["/book/manage/<string:token>"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def public_booking_manage(self, token, message=None, **kwargs):
        booking = self._get_booking_by_token(token)
        if not booking:
            return request.redirect("/")
        return request.render(
            "resource_booking_public.public_booking_manage",
            {
                "booking": booking,
                "booking_type": booking.type_id,
                "access_token": token,
                "selected_slot": booking.start,
                "step": "done",
                "message": message,
                "page_name": "public_booking_manage",
            },
        )

    @route(
        [
            "/book/manage/<string:token>/reschedule",
            "/book/manage/<string:token>/reschedule/<int:year>/<int:month>",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def public_booking_reschedule(
        self, token, year=None, month=None, error=None, **kwargs
    ):
        booking = self._get_booking_by_token(token)
        if not booking:
            return request.redirect("/")
        values = self._calendar_values(booking.type_id, year, month)
        values.update(
            {
                "booking": booking,
                "booking_type": booking.type_id,
                "access_token": token,
                "selected_slot": booking.start,
                "step": "date",
                "form_action": "/book/manage/%s/reschedule/save" % token,
                "calendar_url_pattern": "/book/manage/%s/reschedule" % token,
                "back_url": "/book/manage/%s" % token,
                "is_reschedule": True,
                "error": error,
                "page_name": "public_booking_reschedule",
            }
        )
        return request.render(
            "resource_booking_public.public_booking_calendar", values
        )

    @route(
        ["/book/manage/<string:token>/reschedule/save"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def public_booking_reschedule_save(self, token, slot=None, **kwargs):
        booking = self._get_booking_by_token(token)
        if not booking:
            return request.redirect("/")
        if not slot:
            return request.redirect("/book/manage/%s/reschedule" % token)
        slot_naive = self._parse_slot(slot)
        try:
            booking.sudo().write({"start": slot_naive})
        except (UserError, ValidationError) as exc:
            return request.redirect(
                "/book/manage/%s/reschedule?error=%s"
                % (token, exc.args[0] if exc.args else "")
            )
        return request.redirect(
            "/book/manage/%s?message=rescheduled" % token
        )

    @route(
        ["/book/manage/<string:token>/cancel"],
        type="http",
        auth="public",
        methods=["GET", "POST"],
        website=True,
        sitemap=False,
    )
    def public_booking_cancel(self, token, **kwargs):
        booking = self._get_booking_by_token(token)
        if not booking:
            return request.redirect("/")
        if request.httprequest.method == "POST":
            try:
                booking.sudo().action_cancel()
            except (UserError, ValidationError):
                pass
            return request.render(
                "resource_booking_public.public_booking_cancelled",
                {
                    "booking": booking,
                    "booking_type": booking.type_id,
                    "page_name": "public_booking_cancelled",
                },
            )
        return request.render(
            "resource_booking_public.public_booking_cancel_confirm",
            {
                "booking": booking,
                "booking_type": booking.type_id,
                "access_token": token,
                "selected_slot": booking.start,
                "back_url": "/book/manage/%s" % token,
                "page_name": "public_booking_cancel",
            },
        )
