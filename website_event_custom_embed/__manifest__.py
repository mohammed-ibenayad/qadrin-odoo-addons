# -*- coding: utf-8 -*-
{
    'name': 'Website Event Custom Embed',
    'summary': 'Replace the event description with custom HTML/embed content',
    'description': """
Adds an unsanitized HTML field on each event so editors can paste
iframes, custom designs, or embed snippets that render in the main
column of the event detail page.

When an embed is set on an event, it REPLACES the event description
on the public page (the description is hidden but still stored in
the database). When no embed is set, the description renders
normally — events without custom embeds are unaffected.

The sidebar (Register button, dates, Location, Organizer, Share)
keeps its normal position to the right of the main column.

Stored as a plain Text field (no rich-text editor) so pasted HTML is
preserved exactly as-is. A computed Html field wraps the raw text in
markupsafe.Markup() server-side so QWeb renders it verbatim on the
public page.
    """,
    'author': 'Custom',
    'version': '18.0.1.3.0',
    'license': 'LGPL-3',
    'category': 'Marketing/Events',
    'depends': ['website_event'],
    'data': [
        'views/event_views.xml',
        'views/event_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_event_custom_embed/static/src/scss/embed.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
