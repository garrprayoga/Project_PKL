from odoo import _, api, fields, models

class CourseSubject(models.Model):
    _name = 'course.subject'
    _description = 'Course Subject'
    
    name = fields.Char('Name', required=True)