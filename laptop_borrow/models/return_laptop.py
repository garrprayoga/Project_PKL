from odoo import models, fields, api
from odoo.exceptions import UserError

class ReturnLaptop(models.Model):
    _name = 'return.laptop'
    _description = 'Pengembalian Laptop'

    class_id = fields.Many2one(
        'kelas',
        string="Kelas",
        required=True
    )

    borrower_id = fields.Many2one(
        'res.partner',
        string="Nama Peminjam",
        required=True,
        domain="[('is_student','=',True),('class_id','=',class_id)]"
    )

    borrow_id = fields.Many2one(
        'borrow.laptop',
        string="Kode Peminjaman",
        required=True,
        domain="[('borrower_id','=',borrower_id),('status','=','dipinjam')]"
    )

    return_date = fields.Datetime(
        string="Tanggal Pengembalian",
        default=fields.Datetime.now
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Selesai'),
    ], string="Status", default='draft', tracking=True)

    def action_confirm_return(self):
        """Ubah status peminjaman jadi dikembalikan"""
        for rec in self:
            if rec.borrow_id.status != 'dipinjam':
                raise UserError("Peminjaman ini sudah dikembalikan atau belum valid.")
            rec.borrow_id.status = 'dikembalikan'
            rec.borrow_id.class_id.status_pinjam = 'boleh'
            rec.state = 'done'