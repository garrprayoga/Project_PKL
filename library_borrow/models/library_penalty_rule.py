from odoo import models, fields

class LibraryPenaltyRule(models.Model):
    _name = 'library.penalty.rule'
    _description = 'Library Penalty Rule'

    name = fields.Char("Rule Name", required=True)

    line_ids = fields.One2many(
        'library.penalty.rule.line',   # model child
        'rule_id',                     # inverse field (M2O di child)
        string="Penalty Lines"
    )
