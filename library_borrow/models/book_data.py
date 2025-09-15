from odoo import models, fields, api

class BookData(models.Model):
    _name = 'book.data'
    _description = 'Data Buku Perpustakaan'

    name = fields.Char('Title', required=True)
    author = fields.Char('Author')
    total_copies = fields.Integer('Total Copies', default=1)

    borrowed_count = fields.Integer(
        'Currently Borrowed',
        compute='_compute_borrowed_count',
        store=True,
    )

    available_copies = fields.Integer(
        'Available Copies',
        compute='_compute_available_copies',
        store=True,
    )
    borrow_order_ids = fields.One2many(
        'borrow.order',
        'book_id',
        string="Borrow Orders"
    )

    @api.depends('borrow_order_ids.state')  
    def _compute_borrowed_count(self):
        for book in self:
            active_orders = self.env['borrow.order'].search([
                ('book_id', '=', book.id),
                ('state', '=', 'borrowed')
            ])
            book.borrowed_count = len(active_orders)

    @api.depends('total_copies', 'borrowed_count')
    def _compute_available_copies(self):
        for book in self:
            book.available_copies = book.total_copies - book.borrowed_count
