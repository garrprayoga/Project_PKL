from odoo import models, fields

class Student(models.Model):
    _name = 'laptop.student'
    _description = 'Siswa'

    name = fields.Char(string="Nama Siswa", required=True)
    nis = fields.Char(string="NIS", required=True)
    class_room_id = fields.Many2one('laptop.class.room', string="Kelas", required=True)
    major_id = fields.Many2one(related='class_room_id.major_id', string="Jurusan", store=True)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Nomor Telepon")

    loan_count = fields.Integer(string="Jumlah Peminjaman", compute='_compute_loan_count')

    def _compute_loan_count(self):
        for record in self:
            record.loan_count = self.env['laptop.loan'].search_count([('student_id', '=', record.id)])
