from odoo import _, api, fields, models

class CourseOrder(models.Model):
    _name = 'course.order'
    _description = 'Course Order'
    
    name = fields.Char('Name', required=True)
    student_id = fields.Many2one('res.partner', string='Student')
    line_ids = fields.One2many('course.order.line', 'course_order_id', string='Line')