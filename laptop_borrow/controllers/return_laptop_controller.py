from odoo import http
from odoo.http import request
import json


class ReturnLaptopController(http.Controller):

    # form
    @http.route('/form/pengembalian', auth='public', website=True)
    def return_form(self, **kwargs):
        classes = request.env['kelas'].sudo().search([])
        return request.render('laptop_borrow.return_form_template', {
            'classes': classes,
        })

    # siswa per kelas
    @http.route('/get_students_by_class_return', type='http', auth='public', csrf=False)
    def get_students_by_class_return(self, **kwargs):

        body = request.httprequest.get_data(as_text=True)
        data = json.loads(body) if body else {}

        class_id = data.get('class_id')
        if not class_id:
            return request.make_response(
                json.dumps([]),
                headers=[('Content-Type', 'application/json')]
            )

        students = request.env['res.partner'].sudo().search([
            ('is_student', '=', True),
            ('class_id', '=', int(class_id)),
        ])

        result = [{'id': s.id, 'name': s.name} for s in students]

        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )

    # kode peminjaman per siswa
    @http.route('/get_borrows_by_student', type='http', auth='public', csrf=False)
    def get_borrows_by_student(self, **kwargs):

        body = request.httprequest.get_data(as_text=True)
        data = json.loads(body) if body else {}

        borrower_id = data.get('borrower_id')
        if not borrower_id:
            return request.make_response(
                json.dumps([]),
                headers=[('Content-Type', 'application/json')]
            )

        borrows = request.env['borrow.laptop'].sudo().search([
            ('borrower_id', '=', int(borrower_id)),
            ('status', '=', 'dipinjam')
        ])

        result = [{'id': b.id, 'name': b.name} for b in borrows]

        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )

    # submit
    @http.route(
        '/form/pengembalian/submit',
        type='http',
        auth='public',
        methods=['POST'],
        website=True,
        csrf=False
    )
    def submit_return_form(self, **post):

        class_id = int(post.get('class_id'))
        borrower_id = int(post.get('borrower_id'))
        borrow_id = int(post.get('borrow_id'))
        note = post.get('note')

        return_laptop = request.env['return.laptop'].sudo().create({
            'class_id': class_id,
            'borrower_id': borrower_id,
            'borrow_id': borrow_id,
            'note': note
        })

        return_laptop.action_confirm_return()

        return request.redirect('/form/pengembalian/success')

    # success
    @http.route('/form/pengembalian/success', auth='public', website=True)
    def return_success(self, **kwargs):
        return request.render('laptop_borrow.return_form_success', {})