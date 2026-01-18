{
    'name': 'Laptop Borrow System',
    'version': '1.0',
    'author': 'Habil',
    'maintainers': ['Habil'],
    'website': '',
    'summary': 'Sistem Peminjaman dan Pengembalian Laptop Sekolah',
    'description': """
        Modul ini memungkinkan untuk melakukan pencatatan peminjaman dan pengembalian laptop
        di lingkungan sekolah. Data mencakup nama peminjam, kelas, jurusan, mata pelajaran,
        guru mata pelajaran, serta petugas yang berjaga.
    """,
    'category': 'Education',
    'depends': ['base', 'stock', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/borrow_laptop_view.xml',
        'views/return_laptop_view.xml',
        'views/kelas_view.xml',
        'views/product_view.xml',
        'views/stock_view.xml',
        'views/menuitems.xml',
        'views/borrow_form_template.xml',
        'views/return_form_template.xml',
        'views/homepage_template.xml',
        'views/res_partner_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/laptop_borrow/static/src/css/homepage.css',
            # '/laptop_borrow/static/src/js/borrow_form.js',
            '/laptop_borrow/static/src/js/return_form.js',
        ],
    },
    'installable': True,
    'application': True,
}