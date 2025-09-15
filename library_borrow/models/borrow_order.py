from odoo import _, api, fields, models
from odoo.exceptions import UserError 

class BorrowOrder(models.Model):
    _name = 'borrow.order'
    _description = 'Book Borrowing Order'
    _order = 'borrow_date desc'

    name = fields.Char(
        'Reference',
        default='New',
        readonly=True, 
        copy=False,
        required=True   
    )
    partner_id = fields.Many2one('res.partner', string='Borrower', required=True)
    book_id = fields.Many2one(
        'book.data',
        string='Book',
        required=True,
        domain="[('available_copies', '>', 0)]", 
    )
    penalty_rule_id = fields.Many2one(
        'library.penalty.rule',
        string="Penalty Rule",
        help="Pilih aturan penalty yang berlaku untuk peminjaman ini."
    )
    borrow_date = fields.Date('Borrow Date', default=fields.Date.today, required=True)
    due_date = fields.Date('Due Date', required=True)
    return_date = fields.Date(
        'Return Date',
        states={
            'draft': [('readonly', True)],
            'borrowed': [('readonly', True)],
            'overdue': [('readonly', True)],
            'returned': [('readonly', False)],
        },
    )

    duration_days = fields.Integer(
        'Duration (days)',
        compute='_compute_duration',
        store=True,
    )

    late_days = fields.Integer(
        string="Late Days",
        compute="_compute_penalty",
        store=True
    )
    penalty_per_day = fields.Integer(
        string="Penalty per Day",
        default=5000,
        readonly=True
    )
    penalty_amount = fields.Monetary(
        string="Total Penalty",
        compute="_compute_penalty",
        store=True,
        currency_field="currency_id"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env.company.currency_id.id
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ], string='Status', default='draft', readonly=True)

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)

    @api.depends('borrow_date', 'return_date')
    def _compute_duration(self):
        for rec in self:
            if rec.borrow_date and rec.return_date:
                diff = rec.return_date - rec.borrow_date
                rec.duration_days = diff.days
            else:
                rec.duration_days = 0
        
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code('borrow.order')
            if sequence:
                vals['name'] = sequence
            else:
                vals['name'] = 'BOR-' + str(int(fields.Datetime.now().timestamp()))
        
        return super(BorrowOrder, self).create(vals)

    @api.depends('due_date', 'return_date', 'penalty_per_day', 'penalty_rule_id')
    def _compute_penalty(self):
        for rec in self:
            rec.late_days = 0
            rec.penalty_amount = 0

            # Harus ada penalty rule dan tanggal lengkap
            if not rec.penalty_rule_id or not rec.due_date or not rec.return_date:
                continue

            if rec.return_date > rec.due_date:
                rec.late_days = (rec.return_date - rec.due_date).days
                total_penalty = 0.0

                # Urutkan line supaya logika jelas
                lines = rec.penalty_rule_id.line_ids.sorted(key=lambda l: l.min_days)

                remaining_days = rec.late_days
                for line in lines:
                    if remaining_days <= 0:
                        break

                    # Tentukan rentang hari yang kena di line ini
                    start_day = line.min_days
                    end_day = line.max_days
                    if rec.late_days < start_day:
                        continue  # belum sampai range ini

                    # Hitung jumlah hari dalam range ini
                    applicable_days = min(remaining_days, end_day - start_day + 1)
                    total_penalty += applicable_days * rec.penalty_per_day * line.multiplier

                    remaining_days -= applicable_days

                rec.penalty_amount = total_penalty


    def action_borrow(self):
        for order in self:
            active_borrows = self.search([
                ('partner_id', '=', order.partner_id.id),
                ('state', '=', 'borrowed')
            ])
            if active_borrows:
                raise UserError(_(
                    "Gagal Meminjam!\n\n"
                    "🚫 Siswa '%s' masih meminjam buku: %s"
                ) % (order.partner_id.name, active_borrows[0].name))

            if order.book_id and order.book_id.available_copies <= 0:
                raise UserError(_(
                    "Stok Habis!\n\n"
                    "📚 Buku '%s' saat ini tidak tersedia.\n"
                    "Silakan pilih buku lain."
                ) % order.book_id.name)

            order.book_id.available_copies -= 1
            order.state = 'borrowed'

    def action_return(self):
        """Kembalikan buku dan otomatis buat invoice denda"""
        self.ensure_one()

        if not self.return_date:
            raise UserError(_("⚠ Harap isi Return Date terlebih dahulu sebelum mengembalikan buku."))

        self.state = 'returned'

        if self.penalty_amount > 0 and not self.invoice_id:
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': self.partner_id.id,
                'invoice_date': fields.Date.today(),
                'name': self.name,  
                'invoice_line_ids': [(0, 0, {
                    'name': _("Denda Peminjaman Buku (%s hari x %s)") % (self.late_days, self.penalty_per_day),
                    'quantity': 1,
                    'price_unit': self.penalty_amount,
                })],
            }

            invoice = self.env['account.move'].create(invoice_vals)
            invoice.action_post()
            self.invoice_id = invoice.id

    def action_draft(self):
        """Set kembali ke Draft"""
        for rec in self:
            rec.state = 'draft'

    def action_create_invoice(self):
        """Buat invoice denda peminjaman"""
        self.ensure_one()
        if self.penalty_amount <= 0:
            raise UserError(_("✅ Tidak ada denda. Buku dikembalikan tepat waktu."))

        move_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'name': self.name,  
            'invoice_line_ids': [(0, 0, {
                'name': "Denda Peminjaman Buku (%s hari x %s)" % (self.late_days, self.penalty_per_day),
                'quantity': 1,
                'price_unit': self.penalty_amount,
            })],
        }
        invoice = self.env['account.move'].create(move_vals)
        self.invoice_id = invoice.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }

    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_("Belum ada invoice untuk order ini."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
        }
