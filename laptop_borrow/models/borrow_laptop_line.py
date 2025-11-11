from odoo import models, fields

class BorrowLaptopLine(models.Model):
    _name = 'borrow.laptop.line'
    _description = 'Detail Laptop yang Dipinjam'

    borrow_id = fields.Many2one(
        'borrow.laptop',
        string="Peminjaman",
        ondelete='cascade'
    )

    laptop_serial_id = fields.Many2one(
        'stock.lot',
        string="Nomor Laptop (Serial)",
        required=True,
        domain="[('product_id.product_tmpl_id.is_laptop', '=', True)]"
    )