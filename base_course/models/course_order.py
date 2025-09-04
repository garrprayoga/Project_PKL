from odoo import _, api, fields, models

class CourseOrder(models.Model):
    _name = 'course.order'
    _description = 'Course Order'
    
    name = fields.Char('Name', required=True, default="New", copy=False)
    student_id = fields.Many2one('res.partner', string='Student')
    line_ids = fields.One2many('course.order.line', 'course_order_id', string='Line')
    total_price = fields.Float(compute='_compute_total_price', string='Total Price', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='state', default="draft")

    @api.depends('line_ids.price')
    def _compute_total_price(self):
        for record in self:
            record.total_price = sum(line.price for line in record.line_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('course_order') or _('New')
        return super(CourseOrder, self).create(vals)
    
    def button_confirm(self):
        self.ensure_one()
        self.state = 'confirm'

    def button_done(self):
        self.ensure_one()
        self.state = 'done'

    def button_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def button_cancel(self):
        self.ensure_one()
        self.state = 'cancel'