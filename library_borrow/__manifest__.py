{
    'name': 'Library Borrow System',
    'version': '1.0',
    "author": "Habil",
    "maintainers": ["{Habil}"],
    "website": "",
    'summary': 'Sistem Peminjaman dan Pengembalian Buku',
    'description': """
        Modul Ini Memungkinkan Untuk Meminjam Buku dan Mengembalikan Buku
    """,
    'category': 'Education',
    'depends': ['base', 'contacts', 'account'], 
    'data': [
        'security/ir.model.access.csv', 
        'data/ir_sequence_data.xml',  
        'views/borrow_order_view.xml',
        'views/book_data_view.xml',
        'views/library_penalty_rule_view.xml',
        'views/menuitems.xml',
        
    ],
    'installable': True,
    'application': True,
}