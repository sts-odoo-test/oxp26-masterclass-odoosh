from odoo import fields, models


class ConferenceSession(models.Model):
    _name = 'conference.session'
    _description = 'Conference Session'
    _order = 'date, name'

    name = fields.Char(string='Title', required=True)
    speaker = fields.Char(string='Speaker')           # ← will be renamed 'presenter' in v19
    duration = fields.Integer(string='Duration (min)')  # ← will become Float (hours) in v19
    room = fields.Char(string='Room')
    notes = fields.Text(string='Notes')
    date = fields.Date(string='Date')
