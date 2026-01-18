from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BorrowLaptopLine(models.Model):
    _name = 'borrow.laptop.line'
    _description = 'Detail Barang yang Dipinjam'

    borrow_id = fields.Many2one(
        'borrow.laptop',
        string="Peminjaman",
        ondelete='cascade',
        required=True
    )

    laptop_serial_id = fields.Many2one(
        'stock.lot',
        string="Nomor Serial Barang",
        required=True,
        domain="[('product_id.product_tmpl_id.is_borrowable','=',True)]"
    )

  
    # VALIDASI: Cek asset tidak double dipinjam
    @api.constrains('laptop_serial_id')
    def _check_laptop_not_double(self):
        for line in self:
            if not line.laptop_serial_id or not line.borrow_id:
                continue

            conflict = self.env['borrow.laptop.line'].search([
                ('laptop_serial_id', '=', line.laptop_serial_id.id),
                ('borrow_id.status', '=', 'dipinjam'),
                ('id', '!=', line.id)
            ], limit=1)

            if conflict:
                raise ValidationError(
                    f"Barang dengan serial '{line.laptop_serial_id.name}' "
                    f"sedang dipinjam dan tidak bisa dipilih."
                )