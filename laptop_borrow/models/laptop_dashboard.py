from odoo import models, fields, api

class LaptopDashboard(models.Model):
    _name = 'laptop.dashboard'
    _description = 'Dashboard Monitoring Laptop'
    
    total_laptop = fields.Integer(compute='_compute_stats')
    available_laptop = fields.Integer(compute='_compute_stats')
    borrowed_laptop = fields.Integer(compute='_compute_stats')
    
    @api.depends()
    def _compute_stats(self):
        for rec in self:
            total = self.env['product.template'].search_count([('is_laptop', '=', True)])
            borrowed = self.env['borrow.laptop.line'].search_count([('borrow_id.status', '=', 'dipinjam')])
            rec.total_laptop = total
            rec.borrowed_laptop = borrowed
            rec.available_laptop = total - borrowed
