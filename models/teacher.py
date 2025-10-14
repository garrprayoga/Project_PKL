from odoo import models, fields
from odoo.exceptions import ValidationError

class Teacher(models.Model):
    _name = 'laptop.teacher'
    _description = 'Guru Mata Pelajaran'
    _sql_constraints = [
        ('unique_teacher_code', 'unique(code)', 'Kode guru harus unik!')
    ]

    code = fields.Char(string="Kode Guru", required=True)
    name = fields.Char(string="Nama Guru", required=True)
    subject = fields.Char(string="Mata Pelajaran")

    # Menampilkan nama + kode di dropdown (optional tapi berguna)
    def name_get(self):
        result = []
        for rec in self:
            display_name = f"[{rec.code}] {rec.name}"
            result.append((rec.id, display_name))
        return result
