from odoo import http
from odoo.http import request

class LaptopHomepageController(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        return request.render('laptop_borrow.homepage_template')