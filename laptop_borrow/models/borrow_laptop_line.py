from odoo import models, fields

class BorrowLaptopLine(models.Model):
    _name = 'borrow.laptop.line'
    _description = 'Detail Laptop yang Dipinjam'

    borrow_id = fields.Many2one(
        'borrow.laptop',
        string="Peminjaman",
        ondelete='cascade'
    )

    laptop_id = fields.Many2one(
        'product.template',
        string="Nomor Laptop",
        required=True,
        domain="[('is_laptop', '=', True)]"
    )