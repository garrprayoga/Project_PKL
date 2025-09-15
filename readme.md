run odoo :
C:\odoo17-venv\Scripts\activate
python C:\odoo17\odoo-bin -c C:\odoo17\odoo.conf -d odoo17 --log-level=debug
03/09/2025
## Latihan Odoo PKL SMK AS Habil

1. Membuat repository baru di github lalu di commit dan di push ke github
2. membuat module baru base_course 
3. menambahkan scaffold ke dalam module tersebut
4. membuat models baru yaitu course_subject, course_order, course_order line
5. membuat view dari course_subject dan course order
6. belajar fungsi dari jenis tipe view seperti tree, notebook,

04/09/2025

1. membuat fields.float untuk angka
2. membuat fields.selection untuk pilihan kayak opsi dengan 4 pilihan yaitu done,confirm,draft,cancel
3. membuat button dari 4 state di atas lalu d hubungkan ke status bar
4. lalu di filter berdasarkan tiap state dan di group by state

09/09/2025
1. membuat module extend dan inherite dari course subject
2. nambahin category nya dan waktu nya berapa lama
3. yang course order inherite ke model res partner terus tambahin field is_student(boolean) agar yang tampil student nya hanya yang true

10/10/2025
1. Membuat Module Peminjaman Buku 
2. Dengan fungsi tidak bisa minjam sebelum mengembalikan buku sebelumnya 
3. Dan ada stok buku nya yang tersedia jika buku nya tidak tersedia stok nya maka tidak muncul nama buku tersebut

15/09/2025
Membuat smart button invoice lalu mengubah logika penalty rules per range rules