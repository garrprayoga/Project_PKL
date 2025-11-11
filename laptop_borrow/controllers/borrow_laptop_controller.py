from odoo import http
from odoo.http import request
import json

class BorrowLaptopController(http.Controller):

    @http.route('/form/peminjaman', type='http', auth='public', website=True)
    def borrow_form(self, **kwargs):
        # Ambil semua kelas
        kelas = request.env['kelas'].sudo().search([])

        # Ambil laptop yang sudah dicentang 'is_laptop'
        all_laptops = request.env['product.template'].sudo().search([('is_laptop', '=', True)])

        # Cari laptop yang sedang dipinjam (status 'dipinjam')
        borrowed_laptop_ids = request.env['borrow.laptop.line'].sudo().search([
            ('borrow_id.status', '=', 'dipinjam')
        ]).mapped('laptop_id.id')

        # Filter hanya laptop yang belum dipinjam
        available_laptops = all_laptops.filtered(lambda l: l.id not in borrowed_laptop_ids)

        return request.render('laptop_borrow.borrow_form_template', {
            'kelas': kelas,
            'laptop': available_laptops,
        })

    @http.route('/get_students_by_class', type='http', auth='public', csrf=False)
    def get_students_by_class(self, **kw):
        data = request.httprequest.get_data(as_text=True)
        try:
            json_data = json.loads(data) if data else {}
        except json.JSONDecodeError:
            json_data = {}

        class_id = json_data.get('class_id')
        if not class_id:
            return request.make_response(json.dumps([]), headers=[('Content-Type', 'application/json')])

        students = request.env['res.partner'].sudo().search([
            ('is_student', '=', True),
            ('class_id', '=', int(class_id))
        ])

        result = [{'id': s.id, 'name': s.name} for s in students]
        return request.make_response(json.dumps(result), headers=[('Content-Type', 'application/json')])

    @http.route('/form/peminjaman/submit', type='http', auth='public', website=True, methods=['POST'])
    def borrow_form_submit(self, **post):
        borrower_id = post.get('borrower_id')
        class_id = post.get('class_id')
        borrow_date = post.get('borrow_date')
        tujuan_peminjaman = post.get('tujuan_peminjaman')
        guru_mapel = post.get('guru_mapel')
        keterangan = post.get('keterangan')
        jumlah_pinjam = post.get('jumlah_pinjam')
        petugas_jaga = post.get('petugas_jaga')

        # Ambil semua checkbox laptop yang dicentang
        laptop_ids = request.httprequest.form.getlist('laptop_id')

        # Validasi peminjam (buat baru kalau belum ada)
        if borrower_id and borrower_id.isdigit():
            borrower = request.env['res.partner'].sudo().browse(int(borrower_id))
        else:
            borrower = request.env['res.partner'].sudo().create({
                'name': borrower_id,
                'is_student': True,
                'class_id': int(class_id)
            })

        # Buat record utama peminjaman
        borrow_record = request.env['borrow.laptop'].sudo().create({
            'borrower_id': borrower.id,
            'class_id': class_id,
            'borrow_date': borrow_date,
            'tujuan_peminjaman': tujuan_peminjaman,
            'guru_mapel': guru_mapel,
            'keterangan': keterangan,
            'jumlah_pinjam': jumlah_pinjam,
            'petugas_jaga': petugas_jaga,
            'status': 'dipinjam',
        })

        # Buat detail laptop (bisa banyak)
        for laptop_id in laptop_ids:
            request.env['borrow.laptop.line'].sudo().create({
                'borrow_id': borrow_record.id,
                'laptop_id': int(laptop_id),
            })

        return request.render('laptop_borrow.borrow_success_template')