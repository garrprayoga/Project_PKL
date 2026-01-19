from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date


class BorrowLaptop(models.Model):
    _name = 'borrow.laptop'
    _description = 'Peminjaman Asset'

    name = fields.Char(string="Kode Peminjaman", readonly=True, copy=False, default=lambda self: "New")
    
    # ========== HIERARCHY BARU ==========
    tingkat_id = fields.Many2one('tingkat.sekolah', string="Tingkat", required=True)
    jurusan_id = fields.Many2one('jurusan.sekolah', string="Jurusan", required=True)
    # ===================================
    
    class_id = fields.Many2one('kelas', string="Kelas", required=True,
    )
    

    borrower_id = fields.Many2one(
        'res.partner', 
        string="Nama Peminjam", 
        required=True, 
        domain="[('is_student','=',True),('class_id','=',class_id)]"
    )

    product_tmpl_id = fields.Many2one(
        'product.template', 
        string="Jenis Barang", 
        required=True,
        domain="[('is_borrowable', '=', True)]"
    )
    
    tujuan_peminjaman = fields.Selection([
        ('kbm', 'KBM'), ('lainnya', 'Lainnya'),
    ], string="Tujuan Peminjaman", required=True)
    
    guru_mapel = fields.Char(string="Guru Mapel")
    keterangan = fields.Text(string="Keterangan")
    jumlah_pinjam = fields.Integer(string="Jumlah Pinjam", default=1)
    borrow_date = fields.Datetime(string="Waktu Pinjam", required=True, default=fields.Datetime.now)
    
    status = fields.Selection([
        ('draft', 'Draft'), ('dipinjam', 'Dipinjam'), ('dikembalikan', 'Dikembalikan'),
    ], string="Status", default='draft', tracking=True)
    
    line_ids = fields.One2many('borrow.laptop.line', 'borrow_id', string="Daftar Asset Dipinjam")

    @api.constrains('tujuan_peminjaman', 'guru_mapel', 'keterangan')
    def _check_required_fields(self):
        for rec in self:
            if rec.tujuan_peminjaman == 'kbm' and not rec.guru_mapel:
                raise ValidationError("Guru Mapel wajib diisi jika tujuan adalah KBM.")
            if rec.tujuan_peminjaman == 'lainnya' and not rec.keterangan:
                raise ValidationError("Keterangan wajib diisi jika tujuan adalah Lainnya.")

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            today_str = date.today().strftime("%Y%m%d")
            prefix = f"BRW-{today_str}-"
            last_record = self.search([('name', 'like', prefix + '%')], order='name desc', limit=1)
            last_number = int(last_record.name.split('-')[-1]) if last_record else 0
            vals['name'] = prefix + f"{last_number + 1:02d}"
        return super(BorrowLaptop, self).create(vals)

    def action_dynamic_borrow_return(self):
        for rec in self:
            if rec.status in ['draft', 'dikembalikan']:
                kelas_borrowing = self.search([
                    ('class_id', '=', rec.class_id.id), ('status', '=', 'dipinjam'), ('id', '!=', rec.id)
                ], limit=1)
                if kelas_borrowing:
                    raise UserError(f"Kelas {rec.class_id.name} masih memiliki peminjaman aktif.")
                rec.status = 'dipinjam'
            elif rec.status == 'dipinjam':
                rec.status = 'dikembalikan'

    @api.onchange('tujuan_peminjaman')
    def _onchange_tujuan_peminjaman(self):
        if self.tujuan_peminjaman == 'kbm':
            self.keterangan = False
        elif self.tujuan_peminjaman == 'lainnya':
            self.guru_mapel = False