from odoo import models, fields

class Kelas(models.Model):
    _name = 'kelas'
    _description = 'Data Kelas'

    name = fields.Char(string="Nama Kelas", required=True)
    status_pinjam = fields.Selection([
        ('boleh', 'Boleh Meminjam'),
        ('masih', 'Masih Ada Peminjaman')
    ], string="Status Peminjaman", default='boleh')
    student_ids = fields.One2many('res.partner', 'class_id', string="Daftar Siswa")