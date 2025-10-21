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

    # ===================== Data Peminjam =====================
    student_id = fields.Many2one('laptop.student', string="Siswa", required=True)
    class_room_id = fields.Many2one(related='student_id.class_room_id', string="Kelas", store=True)
    major_id = fields.Many2one(related='student_id.major_id', string="Jurusan", store=True)

    # ===================== Tujuan =====================
    loan_purpose = fields.Selection([
        ('study', 'KBM'),
        ('other', 'Lainnya')
    ], string="Tujuan Peminjaman", required=True)

    teacher_id = fields.Many2one('laptop.teacher', string="Guru Mata Pelajaran")
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

    # ===================== Info Laptop =====================
    total_laptops = fields.Integer(string="Total Laptop", compute="_compute_laptop_stock", store=False)
    available_laptops = fields.Integer(string="Laptop Tersedia", compute="_compute_laptop_stock", store=False)
    borrowed_laptops = fields.Integer(string="Laptop yang Sedang Dipinjam", compute="_compute_laptop_stock", store=False)

    # ===================== Dynamic UI =====================
    @api.onchange('loan_purpose')
    def _onchange_loan_purpose(self):
        if self.loan_purpose == 'study':
            self.other_reason = False
        elif self.loan_purpose == 'other':
            self.teacher_id = False

    # ===================== Nomor Otomatis =====================
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('laptop.loan') or 'New'
        record = super().create(vals)
        record._generate_laptop_lines()
        return record

    def write(self, vals):
        res = super().write(vals)
        if 'quantity' in vals:
            self._generate_laptop_lines()
        return res

    def _generate_laptop_lines(self):
        """Generate detail laptop sesuai jumlah (quantity)."""
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

    # ===================== Validasi =====================
    @api.constrains('loan_purpose', 'teacher_id', 'other_reason')
    def _check_purpose_fields(self):
        for record in self:
            if record.loan_purpose == 'study' and not record.teacher_id:
                raise ValidationError("Harap isi Guru Mata Pelajaran jika tujuan peminjaman adalah KBM.")
            if record.loan_purpose == 'other' and not record.other_reason:
                raise ValidationError("Harap isi keterangan lainnya jika tujuan peminjaman bukan KBM.")

    @api.constrains('loan_datetime', 'return_datetime')
    def _check_return_after_loan(self):
        for record in self:
            if record.return_datetime and record.return_datetime < record.loan_datetime:
                raise ValidationError("Waktu kembali tidak boleh lebih awal dari waktu pinjam.")

    # ===================== Hitung Laptop Tersedia =====================
    @api.depends('state', 'quantity')
    def _compute_laptop_stock(self):
        total = int(self.env['ir.config_parameter'].sudo().get_param('laptop_management.total_laptops', default=20))
        loaned_qty = sum(self.search([('state', '=', 'loaned')]).mapped('quantity'))
        for record in self:
            record.total_laptops = total
            record.borrowed_laptops = loaned_qty
            record.available_laptops = total - loaned_qty

    # ===================== Aksi Tombol =====================
    def action_confirm(self):
        for loan in self:
            if loan.state == 'draft':
                if loan.quantity > loan.available_laptops:
                    raise ValidationError("Jumlah laptop yang tersedia tidak mencukupi.")
                loan.state = 'loaned'
                loan.loan_datetime = fields.Datetime.now()
                if not loan.loan_line_ids:
                    loan._generate_laptop_lines()

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
