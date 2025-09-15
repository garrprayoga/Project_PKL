from odoo import models, fields

class LibraryPenaltyRuleLine(models.Model):
    _name = 'library.penalty.rule.line'
    _description = 'Library Penalty Rule Line'

    rule_id = fields.Many2one(
        'library.penalty.rule',        # harus sama dengan parent
        string="Penalty Rule",
        ondelete='cascade',
        required=True
    )

    min_days = fields.Integer("Min Days", required=True)
    max_days = fields.Integer("Max Days", required=True)
    multiplier = fields.Float("Multiplier", default=1.0)
