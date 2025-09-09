from odoo import fields, models

class CourseSubject(models.Model):
    _inherit = 'course.subject'

    category = fields.Selection([
        ('odoo', 'Odoo'),
        ('Laravel', 'Laravel'),
        ('javascript', 'Javascript'),
        ('other', 'Other'),
    ], string="Category")

    duration = fields.Integer("Duration (hours)")