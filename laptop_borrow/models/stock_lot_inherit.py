from odoo import models, fields, api

class StockLotInherit(models.Model):
    _inherit = 'stock.lot'

    is_available = fields.Boolean(
        string="Tersedia",
        compute="_compute_is_available"
    )

    def _compute_is_available(self):
        BorrowLine = self.env['borrow.laptop.line']
        for lot in self:
            conflict = BorrowLine.search([
                ('laptop_serial_id', '=', lot.id),
                ('borrow_id.status', '=', 'dipinjam')
            ], limit=1)
            lot.is_available = not bool(conflict)