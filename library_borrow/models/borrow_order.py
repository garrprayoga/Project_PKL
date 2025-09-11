from odoo import _, api, fields, models
from datetime import timedelta
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
    partner_id = fields.Many2one(
        'res.partner',
        string='Borrower',
        required=True,
    )
    book_id = fields.Many2one(
        'book.data',
        string='Book',
        required=True,
        domain="[('available_copies', '>', 0)]"
    )
    borrow_date = fields.Date('Borrow Date', default=fields.Date.today, required=True)
    return_date = fields.Date('Return Date')
    duration_days = fields.Integer(
        'Duration (days)',
        compute='_compute_duration',
        store=True,
        help='Number of days the book was borrowed'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ], string='Status', default='draft', readonly=True)

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

            order.state = 'borrowed'

    def action_return(self):
        """Kembalikan buku"""
        self.ensure_one()
        self.return_date = fields.Date.today()
        self.state = 'returned'

    def action_draft(self):
        self.state = 'draft'

    def action_overdue_check(self):
        """Optional: cek overdue (bisa dijadwalkan)"""
        today = fields.Date.today()
        overdue = self.search([
            ('state', '=', 'borrowed'),
            ('return_date', '=', False),
            ('borrow_date', '<', today - timedelta(days=14))  
        ])
        for rec in overdue:
            rec.state = 'overdue'

    def write(self, vals):
        res = super(BorrowOrder, self).write(vals)
        if 'state' in vals:
            book_ids = self.mapped('book_id')
            if book_ids:
                book_ids._compute_borrowed_count()
        return res