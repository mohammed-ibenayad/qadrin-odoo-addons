# -*- coding: utf-8 -*-
{
    'name': 'Website Event Custom Embed',
    'summary': 'Replace the event description with custom HTML/embed content',
    'description': """
Replaces the event description on the public event page with
custom raw HTML pasted into a per-event field. The sidebar
(Register button, dates, Location, Organizer, Share) keeps its
normal position to the right.
    """,
    'author': 'Custom',
    'version': '18.0.1.5.3',
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
