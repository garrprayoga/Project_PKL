from odoo import http
from odoo.http import request
import json
import base64



class ReturnLaptopController(http.Controller):

    # ========== HIERARCHY ROUTES BARU ==========
    @http.route('/get_tingkat_return', type='http', auth='public', csrf=False, methods=['POST'])
    def get_tingkat_return(self, **kwargs):
        """AJAX load list tingkatan (X, XI, XII, XIII)"""
        tingkat = request.env['tingkat.sekolah'].sudo().search([('active', '=', True)])
        result = [{'id': t.id, 'name': t.name} for t in tingkat]
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/get_jurusan_return', type='http', auth='public', csrf=False, methods=['POST'])
    def get_jurusan_return(self, **kwargs):
        """AJAX load list jurusan by tingkatan"""
        body = request.httprequest.get_data(as_text=True)
        data = json.loads(body) if body else {}
        
        tingkat_id = data.get('tingkat_id')
        domain = [('active', '=', True)]
        if tingkat_id:
            domain.append(('id', '=', int(tingkat_id)))
            
        jurusan = request.env['jurusan.sekolah'].sudo().search(domain)
        result = [{'id': j.id, 'name': j.name} for j in jurusan]
        
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/get_kelas_return', type='http', auth='public', csrf=False, methods=['POST'])
    def get_kelas_return(self, **kwargs):
        """AJAX load kelas by tingkatan + jurusan"""
        body = request.httprequest.get_data(as_text=True)
        data = json.loads(body) if body else {}
        
        tingkat_id = data.get('tingkat_id')
        jurusan_id = data.get('jurusan_id')
        domain = []
        if tingkat_id:
            domain.append(('tingkat_id', '=', int(tingkat_id)))
        if jurusan_id:
            domain.append(('jurusan_id', '=', int(jurusan_id)))
            
        kelas = request.env['kelas'].sudo().search(domain)
        result = [{'id': k.id, 'name': k.name} for k in kelas]
        
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )
    # ==========================================

    # form
    @http.route('/form/pengembalian', auth='public', website=True)
    def return_form(self, **kwargs):
        classes = request.env['kelas'].sudo().search([])
        tingkat = request.env['tingkat.sekolah'].sudo().search([('active', '=', True)])
        jurusan = request.env['jurusan.sekolah'].sudo().search([('active', '=', True)])
        
        return request.render('laptop_borrow.return_form_template', {
            'classes': classes,
            'tingkat': tingkat,    # Tambahkan ini
            'jurusan': jurusan,    # Tambahkan ini
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

        # AMBIL FILE GAMBAR
        image_file = request.httprequest.files.get('image')
        image_data = base64.b64encode(image_file.read()) if image_file else None

        # CREATE RECORD RETURN
        return_laptop = request.env['return.laptop'].sudo().create({
            'class_id': class_id,
            'borrower_id': borrower_id,
            'borrow_id': borrow_id,
            'note': note,
            'image': image_data,  # field Binary untuk gambar
            # ========== HIERARCHY FIELDS ==========
            'tingkat_id': post.get('tingkat_id'),
            'jurusan_id': post.get('jurusan_id'),
            # =====================================
        })

        # KONFIRMASI PENGEMBALIAN
        return_laptop.action_confirm_return()

        return request.redirect('/form/pengembalian/success')

    # success
    @http.route('/form/pengembalian/success', auth='public', website=True)
    def return_success(self, **kwargs):
        return request.render('laptop_borrow.return_form_success', {})