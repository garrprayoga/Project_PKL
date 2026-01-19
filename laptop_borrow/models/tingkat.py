from odoo import models, fields


class TingkatSekolah(models.Model):
    _name = 'tingkat.sekolah'
    _description = 'Tingkatan Sekolah'
    
    name = fields.Char(string="Tingkat", required=True, help="X, XI, XII, XIII")
    active = fields.Boolean(string="Aktif", default=True)
