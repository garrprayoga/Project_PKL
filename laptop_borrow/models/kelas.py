from odoo import models, fields, api


class Kelas(models.Model):
    _name = 'kelas'
    _description = 'Data Kelas'

    # ========== HIERARCHY FIELDS ==========
    tingkat_id = fields.Many2one('tingkat.sekolah', string='Tingkatan', required=True)
    jurusan_id = fields.Many2one('jurusan.sekolah', string='Jurusan', required=True)
    # ======================================

    name = fields.Char(string="Nama Kelas", required=True)
    status_pinjam = fields.Selection([
        ('boleh', 'Boleh Meminjam'),
        ('masih', 'Masih Ada Peminjaman')
    ], string="Status Peminjaman", compute="_compute_status_pinjam", store=True)
    student_ids = fields.One2many('res.partner', 'class_id', string="Daftar Siswa")

    @api.depends('student_ids', 'student_ids.borrow_laptop_ids.status')
    def _compute_status_pinjam(self):
        borrow_model = self.env['borrow.laptop']
        for kelas in self:
            # Cari apakah ada peminjaman aktif dari siswa di kelas ini
            active_borrow = borrow_model.search([
                ('borrower_id', 'in', kelas.student_ids.ids),
                ('status', '=', 'dipinjam')
            ], limit=1)
            
            if active_borrow:
                kelas.status_pinjam = 'masih'
            else:
                kelas.status_pinjam = 'boleh'
