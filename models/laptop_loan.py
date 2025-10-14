from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LaptopLoan(models.Model):
    _name = 'laptop.loan'
    _description = 'Peminjaman Laptop'

    name = fields.Char(
        string="No Peminjaman",
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    _rec_name = 'name'

    student_id = fields.Many2one('laptop.student', string="Siswa", required=True)
    class_room_id = fields.Many2one(related='student_id.class_room_id', string="Kelas", store=True)
    major_id = fields.Many2one(related='student_id.major_id', string="Jurusan", store=True)

    # 🔹 Tujuan peminjaman
    loan_purpose = fields.Selection([
        ('study', 'KBM'),
        ('other', 'Lainnya')
    ], string="Tujuan Peminjaman", required=True)

    # 🔹 Guru mata pelajaran (muncul hanya jika tujuan belajar)
    teacher_id = fields.Many2one('laptop.teacher', string="Guru Mata Pelajaran")

    # 🔹 Keterangan lain (muncul hanya jika tujuan lainnya)
    other_reason = fields.Char(string="Keterangan Lainnya")

    quantity = fields.Integer(string="Jumlah Laptop", required=True, default=1)
    loan_line_ids = fields.One2many('laptop.loan.line', 'loan_id', string="Detail Laptop")

    loan_datetime = fields.Datetime(string="Waktu Pinjam", required=True, default=fields.Datetime.now)
    return_datetime = fields.Datetime(string="Waktu Kembali")
    notes = fields.Text(string="Catatan")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('loaned', 'Dipinjam'),
        ('returned', 'Dikembalikan')
    ], string="Status", default='draft', required=True)

    # Generate nomor otomatis
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('laptop.loan') or 'New'
        record = super(LaptopLoan, self).create(vals)
        record._generate_laptop_lines()
        return record

    # Jika jumlah laptop berubah, sesuaikan detail
    def write(self, vals):
        res = super(LaptopLoan, self).write(vals)
        if 'quantity' in vals:
            self._generate_laptop_lines()
        return res

    # Otomatis menyesuaikan detail laptop dengan jumlah yang diinput
    def _generate_laptop_lines(self):
        for loan in self:
            current = len(loan.loan_line_ids)
            desired = loan.quantity

            if desired > current:
                for i in range(current + 1, desired + 1):
                    self.env['laptop.loan.line'].create({
                        'loan_id': loan.id,
                        'laptop_name': f"Laptop-{i:02d}"
                    })
            elif desired < current:
                lines_to_remove = loan.loan_line_ids[-(current - desired):]
                lines_to_remove.unlink()

    # 🔸 Validasi tambahan: tujuan pinjam
    @api.constrains('loan_purpose', 'teacher_id', 'other_reason')
    def _check_purpose_fields(self):
        for record in self:
            if record.loan_purpose == 'study' and not record.teacher_id:
                raise ValidationError("Harap isi Guru Mata Pelajaran jika tujuan peminjaman adalah KBM.")
            if record.loan_purpose == 'other' and not record.other_reason:
                raise ValidationError("Harap isi keterangan lainnya jika tujuan peminjaman bukan KBM.")

    # 🔸 Validasi kelas yang masih punya pinjaman aktif
    @api.constrains('class_room_id', 'state')
    def _check_borrower_loans(self):
        for loan in self:
            if loan.state in ['draft', 'loaned']:
                existing_loans = self.search([
                    ('class_room_id', '=', loan.class_room_id.id),
                    ('state', '=', 'loaned'),
                    ('id', '!=', loan.id)
                ])
                if existing_loans:
                    raise ValidationError(
                        f"Kelas {loan.class_room_id.name} masih punya pinjaman yang belum dikembalikan!"
                    )

    # 🔸 Validasi waktu pengembalian
    @api.constrains('loan_datetime', 'return_datetime')
    def _check_return_after_loan(self):
        for record in self:
            if record.return_datetime and record.return_datetime < record.loan_datetime:
                raise ValidationError("Waktu kembali tidak boleh lebih awal dari waktu pinjam.")

    # Konfirmasi peminjaman
    def action_confirm(self):
        for loan in self:
            if loan.state == 'draft':
                loan.state = 'loaned'
                loan.loan_datetime = fields.Datetime.now()
                if not loan.loan_line_ids:
                    loan._generate_laptop_lines()

    # Tandai pengembalian
    def action_return(self):
        for loan in self:
            if loan.state == 'loaned':
                loan.state = 'returned'
                if not loan.return_datetime:
                    loan.return_datetime = fields.Datetime.now()


class LaptopLoanLine(models.Model):
    _name = 'laptop.loan.line'
    _description = 'Detail Laptop Dipinjam'

    loan_id = fields.Many2one('laptop.loan', string="Peminjaman", ondelete='cascade')
    laptop_name = fields.Char(string="Nomor Laptop", required=True)


