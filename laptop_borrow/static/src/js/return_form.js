document.addEventListener('DOMContentLoaded', function () {

    // ========== HIERARCHY ELEMENTS ==========
    const tingkatSelect = document.getElementById('tingkat_id');
    const jurusanSelect = document.getElementById('jurusan_id');
    const classSelect   = document.getElementById('class_id');
    // ========================================

    const studentSelect = document.getElementById('borrower_id');
    const borrowSelect  = document.getElementById('borrow_id');
    const imageInput    = document.getElementById('image');
    const imagePreview  = document.getElementById('image_preview');

    /* ===============================
       HIERARCHY CASCADE FUNCTIONS
    =============================== */
    async function loadJurusanReturn() {
        if (!tingkatSelect.value) {
            jurusanSelect.innerHTML = '<option value="">-- Pilih Jurusan --</option>';
            classSelect.innerHTML = '<option value="">-- Pilih Kelas --</option>';
            return;
        }

        jurusanSelect.innerHTML = '<option value="">Memuat...</option>';
        
        try {
            const res = await fetch('/get_jurusan_return', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ tingkat_id: tingkatSelect.value })
            });
            const jurusans = await res.json();
            
            jurusanSelect.innerHTML = '<option value="">-- Pilih Jurusan --</option>';
            jurusans.forEach(j => {
                const opt = document.createElement('option');
                opt.value = j.id;
                opt.textContent = j.name;
                jurusanSelect.appendChild(opt);
            });
            
            // Reset kelas & siswa
            classSelect.innerHTML = '<option value="">-- Pilih Kelas --</option>';
            studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
            borrowSelect.innerHTML = '<option value="">-- Pilih Kode Peminjaman --</option>';
        } catch (error) {
            console.error('❌ Error loading jurusan:', error);
            jurusanSelect.innerHTML = '<option value="">Error loading jurusan</option>';
        }
    }

    async function loadKelasReturn() {
        if (!tingkatSelect.value || !jurusanSelect.value) {
            classSelect.innerHTML = '<option value="">-- Pilih Kelas --</option>';
            return;
        }

        classSelect.innerHTML = '<option value="">Memuat...</option>';
        
        try {
            const res = await fetch('/get_kelas_return', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    tingkat_id: tingkatSelect.value, 
                    jurusan_id: jurusanSelect.value 
                })
            });
            const kelasList = await res.json();
            
            classSelect.innerHTML = '<option value="">-- Pilih Kelas --</option>';
            kelasList.forEach(k => {
                const opt = document.createElement('option');
                opt.value = k.id;
                opt.textContent = k.name;
                classSelect.appendChild(opt);
            });
            
            // Reset siswa & borrow
            studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
            borrowSelect.innerHTML = '<option value="">-- Pilih Kode Peminjaman --</option>';
        } catch (error) {
            console.error('❌ Error loading kelas:', error);
            classSelect.innerHTML = '<option value="">Error loading kelas</option>';
        }
    }

    /* ===============================
       HIERARCHY EVENT LISTENERS
    =============================== */
    tingkatSelect?.addEventListener('change', loadJurusanReturn);
    jurusanSelect?.addEventListener('change', loadKelasReturn);

    // 1. LOAD STUDENT BY CLASS (REMAIN SAME)
    classSelect?.addEventListener('change', async function () {
        const classId = this.value;
        studentSelect.innerHTML = '<option value="">-- Memuat... --</option>';
        borrowSelect.innerHTML = '<option value="">-- Pilih Kode Peminjaman --</option>';

        if (!classId) {
            studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
            return;
        }

        try {
            const response = await fetch('/get_students_by_class_return', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ class_id: classId })
            });

            const students = await response.json();
            studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
            if (students.length > 0) {
                students.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id;
                    opt.textContent = s.name;
                    studentSelect.appendChild(opt);
                });
            } else {
                studentSelect.innerHTML = '<option value="">(Tidak ada siswa)</option>';
            }
        } catch (error) {
            console.error(error);
            studentSelect.innerHTML = '<option value="">(Gagal memuat siswa)</option>';
        }
    });

    // 2. LOAD BORROW CODE BY STUDENT (REMAIN SAME)
    studentSelect?.addEventListener('change', async function () {
        const borrowerId = this.value;
        borrowSelect.innerHTML = '<option value="">-- Memuat... --</option>';

        if (!borrowerId) {
            borrowSelect.innerHTML = '<option value="">-- Pilih Kode Peminjaman --</option>';
            return;
        }

        try {
            const response = await fetch('/get_borrows_by_student', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ borrower_id: borrowerId })
            });

            const borrows = await response.json();
            borrowSelect.innerHTML = '<option value="">-- Pilih Kode Peminjaman --</option>';
            if (borrows.length > 0) {
                borrows.forEach(b => {
                    const opt = document.createElement('option');
                    opt.value = b.id;
                    opt.textContent = b.name;
                    borrowSelect.appendChild(opt);
                });
            } else {
                borrowSelect.innerHTML = '<option value="">(Tidak ada peminjaman aktif)</option>';
            }
        } catch (error) {
            console.error(error);
            borrowSelect.innerHTML = '<option value="">(Gagal memuat kode)</option>';
        }
    });

    // 3. PREVIEW IMAGE DARI KAMERA (REMAIN SAME)
    imageInput?.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            // Pastikan file memang gambar
            if (!file.type.startsWith('image/')) {
                alert('File harus berupa gambar!');
                this.value = '';
                imagePreview.style.display = 'none';
                return;
            }
            // Preview
            imagePreview.src = URL.createObjectURL(file);
            imagePreview.style.display = 'block';
        } else {
            imagePreview.style.display = 'none';
            alert('Foto wajib diambil dari kamera langsung!');
        }
    });

    console.log('✅ RETURN JS READY - HIERARCHY ACTIVE');
});
