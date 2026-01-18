from odoo import models, fields, api

class ProductInherit(models.Model):
    _inherit = 'product.template'
    
    is_borrowable = fields.Boolean(
        string="Bisa Dipinjam", 
        default=False,
        help="Centang jika produk ini bisa dipinjam"
    )
