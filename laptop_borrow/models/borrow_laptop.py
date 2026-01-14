from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date

class BorrowLaptop(models.Model):
    _name = 'borrow.laptop'
    _description = 'Peminjaman Laptop'

    name = fields.Char(
        string="Kode Peminjaman",
        readonly=True,
        copy=False,
        default=lambda self: "New"
    )

    class_id = fields.Many2one(
        'kelas',
        string="Kelas",
        required=True,
        help="Pilih kelas terlebih dahulu."
    )

    borrower_id = fields.Many2one(
        'res.partner',
        string="Nama Peminjam",
        required=True,
        domain="[('is_student','=',True),('class_id','=',class_id)]",
        help="Pilih peminjam yang terdaftar di kelas ini."
    )

    tujuan_peminjaman = fields.Selection([
        ('kbm', 'KBM'),
        ('lainnya', 'Lainnya'),
    ], string="Tujuan Peminjaman", required=True)

    guru_mapel = fields.Char(
        string="Guru Mapel",
        help="Masukkan nama guru mata pelajaran jika KBM."
    )

    keterangan = fields.Text(
        string="Keterangan ",
        help="Tambahkan catatan jika tujuan bukan KBM."
    )

    jumlah_pinjam = fields.Integer(
        string="Jumlah Pinjam",
        default=1,
        help="Masukkan jumlah laptop yang dipinjam."
    )

    borrow_date = fields.Datetime(
        string="Waktu Pinjam",
        required=True,
        default=fields.Datetime.now
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('dipinjam', 'Dipinjam'),
        ('dikembalikan', 'Dikembalikan'),
    ], string="Status", default='draft', tracking=True)

    line_ids = fields.One2many(
        'borrow.laptop.line',
        'borrow_id',
        string="Daftar Laptop Dipinjam"
    )

    # VALIDASI WAJIB DIISI
    @api.constrains('tujuan_peminjaman', 'guru_mapel', 'keterangan')
    def _check_required_fields(self):
        for rec in self:
            if rec.tujuan_peminjaman == 'kbm' and not rec.guru_mapel:
                raise ValidationError("Guru Mapel wajib diisi jika tujuan adalah KBM.")
            if rec.tujuan_peminjaman == 'lainnya' and not rec.keterangan:
                raise ValidationError("Keterangan wajib diisi jika tujuan adalah Lainnya.")


    # GENERATE CODE
    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            today_str = date.today().strftime("%Y%m%d")
            prefix = f"BRW-{today_str}-"

            last_record = self.search([
                ('name', 'like', prefix + '%')
            ], order='name desc', limit=1)

            if last_record:
                try:
                    last_number = int(last_record.name.split('-')[-1])
                except ValueError:
                    last_number = 0
                new_number = f"{last_number + 1:02d}"
            else:
                new_number = "01"

            vals['name'] = prefix + new_number

        return super(BorrowLaptop, self).create(vals)


    # STATUS PINJAM/KEMBALIKAN
    def action_dynamic_borrow_return(self):
        for rec in self:

            if rec.status in ['draft', 'dikembalikan']:

                kelas_borrowing = self.env['borrow.laptop'].search([
                    ('class_id', '=', rec.class_id.id),
                    ('status', '=', 'dipinjam'),
                    ('id', '!=', rec.id)
                ], limit=1)

                if kelas_borrowing:
                    raise UserError(
                        f"Kelas {rec.class_id.name} masih memiliki siswa yang meminjam laptop."
                    )

                existing_borrower = self.env['borrow.laptop'].search([
                    ('borrower_id', '=', rec.borrower_id.id),
                    ('status', '=', 'dipinjam'),
                    ('id', '!=', rec.id)
                ], limit=1)

                if existing_borrower:
                    raise UserError(
                        f"{rec.borrower_id.name} masih memiliki pinjaman aktif."
                    )

                rec.status = 'dipinjam'

            elif rec.status == 'dipinjam':
                rec.status = 'dikembalikan'

    @api.onchange('tujuan_peminjaman')
    def _onchange_tujuan_peminjaman(self):
        if self.tujuan_peminjaman == 'kbm':
            self.keterangan = False
        elif self.tujuan_peminjaman == 'lainnya':
            self.guru_mapel = False
