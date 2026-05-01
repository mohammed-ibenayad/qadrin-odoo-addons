# Copyright 2024 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Resource Booking Public",
    "summary": "Allow public anonymous users to book resources via shared links",
    "version": "18.0.1.3.0",
    "development_status": "Alpha",
    "category": "Appointments",
    "website": "https://github.com/OCA/calendar",
    "author": "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "resource_booking",
        "portal",
        "website",
        "sale_management",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/resource_booking_type_views.xml",
        "views/resource_booking_views.xml",
        "templates/public_booking.xml",
    ],
}