from odoo import models, fields

class ProductInherit(models.Model):
    _inherit = 'product.template'

    is_laptop = fields.Boolean(string="Laptop", help="Centang jika produk ini adalah laptop.")
