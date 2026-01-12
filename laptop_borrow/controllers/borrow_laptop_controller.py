from odoo import http, fields
from odoo.http import request
import json


class BorrowLaptopController(http.Controller):
    def _render_form_with_error(self, error_message):

        borrowed_class_ids = request.env['borrow.laptop'].sudo().search([
            ('status', '=', 'dipinjam')
        ]).mapped('class_id.id')

        kelas = request.env['kelas'].sudo().search([
            ('id', 'not in', borrowed_class_ids)
        ])

        laptop_product = request.env['product.template'].sudo().search([
            ('name', '=', 'Laptop')
        ], limit=1)

        all_serials = request.env['stock.lot'].sudo().search([
            ('product_id.product_tmpl_id', '=', laptop_product.id)
        ])

        borrowed_lot_ids = request.env['borrow.laptop.line'].sudo().search([
            ('borrow_id.status', '=', 'dipinjam')
        ]).mapped('laptop_serial_id.id')

        available_serials = all_serials.filtered(
            lambda l: l.id not in borrowed_lot_ids
        )

        return request.render('laptop_borrow.borrow_form_template', {
            'error': error_message,
            'kelas': kelas,
            'lots': available_serials,
        })

    # form peminjaman
    @http.route('/form/peminjaman', type='http', auth='public', website=True)
    def borrow_form(self, **kwargs):

        borrowed_class_ids = request.env['borrow.laptop'].sudo().search([
            ('status', '=', 'dipinjam')
        ]).mapped('class_id.id')

        kelas = request.env['kelas'].sudo().search([
            ('id', 'not in', borrowed_class_ids)
        ])

        laptop_product = request.env['product.template'].sudo().search([
            ('name', '=', 'Laptop')
        ], limit=1)

        all_serials = request.env['stock.lot'].sudo().search([
            ('product_id.product_tmpl_id', '=', laptop_product.id)
        ])

        borrowed_lot_ids = request.env['borrow.laptop.line'].sudo().search([
            ('borrow_id.status', '=', 'dipinjam')
        ]).mapped('laptop_serial_id.id')

        available_serials = all_serials.filtered(
            lambda l: l.id not in borrowed_lot_ids
        )

        return request.render('laptop_borrow.borrow_form_template', {
            'kelas': kelas,
            'lots': available_serials,
        })

    # cek kelas
    @http.route('/check_class_borrow_status', type='http', auth='public', csrf=False)
    def check_class_borrow_status(self, **kwargs):

        body = request.httprequest.get_data(as_text=True)
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}

        class_id = data.get('class_id')
        if not class_id:
            return request.make_response(
                json.dumps({'blocked': False}),
                headers=[('Content-Type', 'application/json')]
            )

        existing = request.env['borrow.laptop'].sudo().search([
            ('class_id', '=', int(class_id)),
            ('status', '=', 'dipinjam')
        ], limit=1)

        if existing:
            return request.make_response(
                json.dumps({
                    'blocked': True,
                    'message': f"Kelas {existing.class_id.name} masih memiliki peminjaman aktif."
                }),
                headers=[('Content-Type', 'application/json')]
            )

        return request.make_response(
            json.dumps({'blocked': False}),
            headers=[('Content-Type', 'application/json')]
        )

    # siswa ambil dri kelas
    @http.route('/get_students_by_class', type='http', auth='public', csrf=False)
    def get_students_by_class(self, **kw):

        body = request.httprequest.get_data(as_text=True)
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}

        class_id = data.get('class_id')
        if not class_id:
            return request.make_response(
                json.dumps([]),
                headers=[('Content-Type', 'application/json')]
            )

        students = request.env['res.partner'].sudo().search([
            ('is_student', '=', True),
            ('class_id', '=', int(class_id))
        ])

        result = [{'id': s.id, 'name': s.name} for s in students]

        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )

    # submit
    @http.route(
        '/form/peminjaman/submit',
        type='http',
        auth='public',
        website=True,
        methods=['POST']
    )
    def borrow_form_submit(self, **post):

        borrower_id = post.get('borrower_id')
        class_id = post.get('class_id')
        tujuan = post.get('tujuan_peminjaman')
        guru_mapel = post.get('guru_mapel') or False
        keterangan = post.get('keterangan') or False
        jumlah_pinjam = post.get('jumlah_pinjam')
        lot_ids = request.httprequest.form.getlist('lot_id')

        existing_borrow = request.env['borrow.laptop'].sudo().search([
            ('class_id', '=', int(class_id)),
            ('status', '=', 'dipinjam')
        ], limit=1)

        if existing_borrow:
            return self._render_form_with_error(
                f"Kelas {existing_borrow.class_id.name} masih memiliki peminjaman aktif."
            )

        if tujuan == 'kbm' and not guru_mapel:
            return self._render_form_with_error("Guru Mapel wajib diisi.")

        if tujuan == 'lainnya' and not keterangan:
            return self._render_form_with_error("Keterangan wajib diisi.")

        borrow_date = fields.Datetime.now()

        if borrower_id and borrower_id.isdigit():
            borrower = request.env['res.partner'].sudo().browse(int(borrower_id))
        else:
            borrower = request.env['res.partner'].sudo().create({
                'name': borrower_id,
                'is_student': True,
                'class_id': int(class_id)
            })

        borrow_record = request.env['borrow.laptop'].sudo().create({
            'borrower_id': borrower.id,
            'class_id': int(class_id),
            'borrow_date': borrow_date,
            'tujuan_peminjaman': tujuan,
            'guru_mapel': guru_mapel,
            'keterangan': keterangan,
            'jumlah_pinjam': jumlah_pinjam,
            'status': 'dipinjam',
        })

        for lot_id in lot_ids:
            request.env['borrow.laptop.line'].sudo().create({
                'borrow_id': borrow_record.id,
                'laptop_serial_id': int(lot_id),
            })

        return request.render('laptop_borrow.borrow_success_template', {
            'borrower_name': borrower.name,
            'borrow_code': borrow_record.name,
        })