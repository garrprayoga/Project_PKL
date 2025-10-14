from odoo import models, fields

class ClassRoom(models.Model):
    _name = 'laptop.class.room'
    _description = 'Kelas'

    name = fields.Char(string="Nama Kelas", required=True)
    grade = fields.Char(string="Tingkat", required=True)
    major_id = fields.Many2one('laptop.major', string="Jurusan", required=True)

    student_ids = fields.One2many('laptop.student', 'class_room_id', string="Daftar Siswa")
