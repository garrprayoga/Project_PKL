from odoo import _, api, fields, models

class CourseOrder(models.Model):
    _name = 'course.order.line'
    _description = 'Course Order Line'

    course_order_id = fields.Many2one('course.order', string='Course Order')
    course_id = fields.Many2one('course.subject', string='Course')
    price = fields.Float('Price')

