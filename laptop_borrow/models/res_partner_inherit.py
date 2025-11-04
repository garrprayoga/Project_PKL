from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean(string="Student")
    class_id = fields.Many2one('kelas', string="Kelas") 