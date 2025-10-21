from odoo import models, fields, api


class LaptopConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    total_laptops = fields.Integer(string="Total Laptop Sekolah", default=20)

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('laptop_management.total_laptops', self.total_laptops)

    @api.model
    def get_values(self):
        res = super().get_values()
        total = int(self.env['ir.config_parameter'].sudo().get_param('laptop_management.total_laptops', default=30))
        res.update(total_laptops=total)
        return res
