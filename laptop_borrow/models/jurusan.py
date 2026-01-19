from odoo import models, fields


class JurusanSekolah(models.Model):
    _name = 'jurusan.sekolah'
    _description = 'Jurusan Sekolah'
    
    name = fields.Char(string="Jurusan", required=True, help="RPL, IPA, IPS, TKRO")
    active = fields.Boolean(string="Aktif", default=True)
