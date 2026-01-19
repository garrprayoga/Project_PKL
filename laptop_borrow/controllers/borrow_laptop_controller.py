from odoo import http, fields
from odoo.http import request
import json


class BorrowLaptopController(http.Controller):
    
    # ========== HIERARCHY ROUTES ==========
    @http.route('/get_tingkat', type='http', auth='public', csrf=False, methods=['POST'])
    def get_tingkat(self, **kwargs):
        """AJAX load list tingkatan (X, XI, XII, XIII)"""
        tingkat = request.env['tingkat.sekolah'].sudo().search([('active', '=', True)])
        result = [{'id': t.id, 'name': t.name} for t in tingkat]
        return json.dumps(result)

    @http.route('/get_jurusan', type='http', auth='public', csrf=False, methods=['POST'])
    def get_jurusan(self, **kwargs):
        """AJAX load list jurusan (RPL, IPA, IPS, dll)"""
        # ✅ FIX: Jurusan tidak perlu filter by tingkat
        jurusan = request.env['jurusan.sekolah'].sudo().search([('active', '=', True)])
        result = [{'id': j.id, 'name': j.name} for j in jurusan]
        return json.dumps(result)

    @http.route('/get_kelas_by_tingkat_jurusan', type='http', auth='public', csrf=False, methods=['POST'])
    def get_kelas_by_tingkat_jurusan(self, **kwargs):
        """AJAX load kelas by tingkatan + jurusan"""
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            tingkat_id = data.get('tingkat_id')
            jurusan_id = data.get('jurusan_id')
        except:
            return json.dumps([])
        
        # ✅ Harus ada minimal salah satu filter
        if not tingkat_id and not jurusan_id:
            return json.dumps([])
        
        domain = []
        if tingkat_id:
            domain.append(('tingkat_id', '=', int(tingkat_id)))
        if jurusan_id:
            domain.append(('jurusan_id', '=', int(jurusan_id)))
        
        # ✅ Exclude kelas yang sedang dipinjam
        borrowed_class_ids = request.env['borrow.laptop'].sudo().search([
            ('status', '=', 'dipinjam')
        ]).mapped('class_id.id')
        
        if borrowed_class_ids:
            domain.append(('id', 'not in', borrowed_class_ids))
            
        kelas = request.env['kelas'].sudo().search(domain)
        result = [{'id': k.id, 'name': k.name} for k in kelas]
        return json.dumps(result)
    # ==========================================
    
    def _render_form_with_error(self, error_message, products):
        """Render form dengan error message"""
        return request.render('laptop_borrow.borrow_form_template', {
            'error': error_message,
            'products': products,
        })

    @http.route('/form/peminjaman', type='http', auth='public', website=True)
    def borrow_form(self, **kwargs):
        """Main borrow form - load products borrowable"""
        products = request.env['product.template'].sudo().search([
            ('is_borrowable', '=', True)
        ])
        
        # ✅ TAMBAHKAN INI:
        tingkat = request.env['tingkat.sekolah'].sudo().search([('active', '=', True)])
        jurusan = request.env['jurusan.sekolah'].sudo().search([('active', '=', True)])

        return request.render('laptop_borrow.borrow_form_template', {
            'products': products,
            'tingkat': tingkat,   # ✅ TAMBAHKAN
            'jurusan': jurusan,   # ✅ TAMBAHKAN
        })

    @http.route('/check_class_borrow_status', type='http', auth='public', csrf=False, methods=['POST'])
    def check_class_borrow_status(self, **kwargs):
        """AJAX check kelas masih pinjam atau tidak"""
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            class_id = data.get('class_id')
        except:
            return json.dumps({'blocked': False})

        if not class_id:
            return json.dumps({'blocked': False})

        existing = request.env['borrow.laptop'].sudo().search([
            ('class_id', '=', int(class_id)),
            ('status', '=', 'dipinjam')
        ], limit=1)

        if existing:
            return json.dumps({
                'blocked': True,
                'message': f"Kelas {existing.class_id.name} masih memiliki peminjaman aktif."
            })

        return json.dumps({'blocked': False})

    @http.route('/get_students_by_class', type='http', auth='public', csrf=False, methods=['POST'])
    def get_students_by_class(self, **kwargs):
        """AJAX load siswa by kelas"""
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            class_id = data.get('class_id')
        except:
            return json.dumps([])

        if not class_id:
            return json.dumps([])

        students = request.env['res.partner'].sudo().search([
            ('is_student', '=', True),
            ('class_id', '=', int(class_id))
        ])

        result = [{'id': s.id, 'name': s.name} for s in students]
        return json.dumps(result)

    @http.route('/get_serials_by_product', type='http', auth='public', csrf=False, methods=['POST'])
    def get_serials_by_product(self, **kwargs):
        """AJAX load serial numbers by product template"""
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            product_id = data.get('product_id')
        except:
            return json.dumps([])

        if not product_id:
            return json.dumps([])

        # Get all serials for this product
        all_serials = request.env['stock.lot'].sudo().search([
            ('product_id.product_tmpl_id', '=', int(product_id))
        ])

        # Exclude borrowed serials
        borrowed_serials = request.env['borrow.laptop.line'].sudo().search([
            ('borrow_id.status', '=', 'dipinjam'),
            ('borrow_id.product_tmpl_id', '=', int(product_id))
        ]).mapped('laptop_serial_id.id')

        available_serials = all_serials.filtered(lambda l: l.id not in borrowed_serials)
        result = [{'id': s.id, 'name': s.name} for s in available_serials]
        
        return json.dumps(result)

    @http.route('/form/peminjaman/submit', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def borrow_form_submit(self, **post):
        """Submit form peminjaman"""
        borrower_id = post.get('borrower_id')
        class_id = post.get('class_id')
        tingkat_id = post.get('tingkat_id')
        jurusan_id = post.get('jurusan_id')
        product_id = post.get('product_id')
        tujuan = post.get('tujuan_peminjaman')
        guru_mapel = post.get('guru_mapel') or False
        keterangan = post.get('keterangan') or False
        jumlah_pinjam = post.get('jumlah_pinjam')
        lot_ids = request.httprequest.form.getlist('lot_id')

        # VALIDASI 1: Kelas sudah ada peminjaman
        existing_borrow = request.env['borrow.laptop'].sudo().search([
            ('class_id', '=', int(class_id)),
            ('status', '=', 'dipinjam')
        ], limit=1)
        
        if existing_borrow:
            products = request.env['product.template'].sudo().search([('is_borrowable', '=', True)])
            return self._render_form_with_error(
                f"Kelas {existing_borrow.class_id.name} masih memiliki peminjaman aktif.",
                products
            )

        # VALIDASI 2: Field required
        if tujuan == 'kbm' and not guru_mapel:
            products = request.env['product.template'].sudo().search([('is_borrowable', '=', True)])
            return self._render_form_with_error("Guru Mapel wajib diisi.", products)

        if tujuan == 'lainnya' and not keterangan:
            products = request.env['product.template'].sudo().search([('is_borrowable', '=', True)])
            return self._render_form_with_error("Keterangan wajib diisi.", products)

        borrow_date = fields.Datetime.now()

        # CREATE/GET BORROWER
        if borrower_id and borrower_id.isdigit():
            borrower = request.env['res.partner'].sudo().browse(int(borrower_id))
        else:
            borrower = request.env['res.partner'].sudo().create({
                'name': borrower_id,
                'is_student': True,
                'class_id': int(class_id)
            })

        # CREATE BORROW RECORD
        borrow_record = request.env['borrow.laptop'].sudo().create({
            'borrower_id': borrower.id,
            'tingkat_id': int(tingkat_id),
            'jurusan_id': int(jurusan_id),
            'class_id': int(class_id),
            'product_tmpl_id': int(product_id),
            'borrow_date': borrow_date,
            'tujuan_peminjaman': tujuan,
            'guru_mapel': guru_mapel,
            'keterangan': keterangan,
            'jumlah_pinjam': int(jumlah_pinjam),
            'status': 'dipinjam',
        })

        # CREATE SERIAL LINES
        for lot_id in lot_ids:
            request.env['borrow.laptop.line'].sudo().create({
                'borrow_id': borrow_record.id,
                'laptop_serial_id': int(lot_id),
            })

        return request.render('laptop_borrow.borrow_success_template', {
            'borrower_name': borrower.name,
            'borrow_code': borrow_record.name,
            'product_name': borrow_record.product_tmpl_id.name,
        })