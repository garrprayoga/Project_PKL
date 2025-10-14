from odoo import models, fields

class Major(models.Model):
    _name = 'laptop.major'
    _description = 'Jurusan'

    name = fields.Char(string="Nama Jurusan", required=True)
    code = fields.Char(string="Kode Jurusan", required=True)
    description = fields.Text(string="Deskripsi")

    class_room_ids = fields.One2many('laptop.class.room', 'major_id', string="Daftar Kelas")
    