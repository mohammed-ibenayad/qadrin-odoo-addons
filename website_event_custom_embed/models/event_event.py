# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = 'event.event'

    # Raw input field. Plain Text (not Html) so the rich-text editor
    # doesn't mangle pasted markup: <style>, <link>, and <script> tags
    # all survive verbatim. Editors paste body-content HTML here.
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

    # Render-time field. We can't use markupsafe.Markup() inside QWeb
    # expressions (`markupsafe` isn't exposed in the QWeb evaluation
    # context), so we wrap it server-side here. Sanitize=False because
    # the whole point is to emit the raw HTML the editor pasted; the
    # source value lives in `embed_html` which is intentionally not
    # sanitized either.
    embed_html_safe = fields.Html(
        string='Embed HTML (rendered)',
        compute='_compute_embed_html_safe',
        sanitize=False,
        sanitize_attributes=False,
        sanitize_form=False,
        strip_style=False,
        strip_classes=False,
        compute_sudo=False,
    )

    @api.depends('embed_html')
    def _compute_embed_html_safe(self):
        for event in self:
            event.embed_html_safe = (
                Markup(event.embed_html) if event.embed_html else False
            )
