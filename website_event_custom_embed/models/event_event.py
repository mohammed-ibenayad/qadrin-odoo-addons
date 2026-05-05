# -*- coding: utf-8 -*-
from odoo import fields, models


class EventEvent(models.Model):
    _inherit = 'event.event'

    # NOTE: this is intentionally a Text field, NOT an Html field.
    #
    # Why: Odoo's Html field is bound to a rich-text editor (Wysiwyg/OWL)
    # that aggressively re-processes content on save: it strips <style>,
    # <link>, <script>, escapes raw HTML pasted in Code View mode, and
    # wraps loose text in <p> tags. Even with sanitize=False on the model,
    # the *editor* on the client side still mangles the value before it
    # reaches the server. Switching to Text bypasses the editor entirely:
    # the value is a plain string, stored verbatim.
    #
    # The frontend QWeb template renders this with t-out + Markup() so
    # it's emitted as raw HTML on the public page (see event_templates.xml).
    embed_html = fields.Text(
        string='Embed HTML',
        translate=True,
        help=(
            "Raw HTML / iframe / embed content rendered in the main column "
            "of the public event page, below the description. Stored "
            "verbatim — paste only trusted markup. Use a textarea (not the "
            "rich-text editor) so <style>, <link>, and <script> tags survive."
        ),
    )
