from odoo import http
from odoo.http import request

class ReturnLaptopController(http.Controller):

    @http.route('/form/pengembalian', auth='public', website=True)
    def return_form(self, **kwargs):
        classes = request.env['kelas'].sudo().search([])
        borrowers = request.env['res.partner'].sudo().search([('is_student', '=', True)])
        borrows = request.env['borrow.laptop'].sudo().search([('status', '=', 'dipinjam')])
        return request.render('laptop_borrow.return_form_template', {
            'classes': classes,
            'borrowers': borrowers,
            'borrows': borrows,
        })

    @http.route('/form/pengembalian/submit', auth='public', type='http', methods=['POST'], website=True, csrf=False)
    def submit_return_form(self, **post):
        class_id = int(post.get('class_id'))
        borrower_id = int(post.get('borrower_id'))
        borrow_id = int(post.get('borrow_id'))

        # Buat record pengembalian baru
        return_laptop = request.env['return.laptop'].sudo().create({
            'class_id': class_id,
            'borrower_id': borrower_id,
            'borrow_id': borrow_id,
        })

        # Jalankan aksi konfirmasi pengembalian
        return_laptop.action_confirm_return()

        return request.redirect('/form/pengembalian/success')

    @http.route('/form/pengembalian/success', auth='public', website=True)
    def return_success(self, **kwargs):
        return request.render('laptop_borrow.return_form_success', {})
