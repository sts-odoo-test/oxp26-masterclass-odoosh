from odoo import api, fields, models


class ConferenceSession(models.Model):
    _name = 'conference.session'
    _description = 'Conference Session'
    _order = 'date, name'

    name = fields.Char(string='Title', required=True)
    speaker = fields.Char(string='Speaker')           # ← will be renamed 'presenter' in v19
    duration = fields.Integer(string='Duration (min)')  # ← will become Float (hours) in v19
    duration_in_hours = fields.Float(
        string='Duration (h)',
        compute='_compute_duration_in_hours',
        store=True,
    )
    room = fields.Char(string='Room')
    notes = fields.Text(string='Notes')
    date = fields.Date(string='Date')

    @api.depends('duration')
    def _compute_duration_in_hours(self):
        for session in self:
            session.duration_in_hours = session.duration / 60.0
