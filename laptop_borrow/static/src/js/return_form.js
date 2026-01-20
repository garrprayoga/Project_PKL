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

    console.log('🚀 Return Elements found:', {
        tingkat: !!tingkatSelect,
        jurusan: !!jurusanSelect,
        class: !!classSelect
    });

    /* ===============================
       LOAD TINGKAT (OTOMATIS SAAT LOAD)
    =============================== */
    async function loadTingkat() {
        if (!tingkatSelect) return;
        
        tingkatSelect.innerHTML = '<option value="">-- Loading... --</option>';
        
        try {
            console.log('🔔 Loading tingkat...');
            const res = await fetch('/get_tingkat_return', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            
            const text = await res.text();
            console.log('📥 Tingkat response:', text);
            
            const tingkats = JSON.parse(text);
            
            tingkatSelect.innerHTML = '<option value="">-- Pilih Tingkat --</option>';
            tingkats.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.id;
                opt.textContent = t.name;
                tingkatSelect.appendChild(opt);
            });
            
            console.log('✅ Tingkat loaded:', tingkats.length);
        } catch (error) {
            console.error('❌ Error loading tingkat:', error);
            tingkatSelect.innerHTML = '<option value="">-- Error loading --</option>';
        }
    }

    /* ===============================
       LOAD JURUSAN (OTOMATIS SAAT LOAD - INDEPENDENT)
    =============================== */
    async function loadJurusan() {
        if (!jurusanSelect) return;
        
        jurusanSelect.innerHTML = '<option value="">-- Loading... --</option>';
        
        try {
            console.log('🔔 Loading jurusan (independent)...');
            const res = await fetch('/get_jurusan_return', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({}) // Empty body = load semua jurusan
            });
            
            const text = await res.text();
            console.log('📥 Jurusan response:', text);
            
            const jurusans = JSON.parse(text);
            
            jurusanSelect.innerHTML = '<option value="">-- Pilih Jurusan --</option>';
            jurusans.forEach(j => {
                const opt = document.createElement('option');
                opt.value = j.id;
                opt.textContent = j.name;
                jurusanSelect.appendChild(opt);
            });
            
            console.log('✅ Jurusan loaded:', jurusans.length);
        } catch (error) {
            console.error('❌ Error loading jurusan:', error);
            jurusanSelect.innerHTML = '<option value="">-- Error loading --</option>';
        }
    }

    /* ===============================
       LOAD KELAS (TINGKAT + JURUSAN - SAMA SEPERTI BORROW)
    =============================== */
    async function loadKelas() {
        const tingkatId = tingkatSelect?.value;
        const jurusanId = jurusanSelect?.value;
        
        if (!classSelect) return;
        
        classSelect.innerHTML = '<option value="">-- Loading... --</option>';
        studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
        borrowSelect.innerHTML = '<option value="">-- Pilih Kode Peminjaman --</option>';
        
        if (!tingkatId || !jurusanId) {
            classSelect.innerHTML = '<option value="">-- Pilih Tingkat & Jurusan --</option>';
            return;
        }

        try {
            console.log('🔔 Loading kelas for tingkat:', tingkatId, 'jurusan:', jurusanId);
            const res = await fetch('/get_kelas_return', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    tingkat_id: tingkatId, 
                    jurusan_id: jurusanId 
                })
            });
            
            const text = await res.text();
            console.log('📥 Kelas response:', text);
            
            const kelasList = JSON.parse(text);
            
            classSelect.innerHTML = '<option value="">-- Pilih Kelas --</option>';
            kelasList.forEach(k => {
                const opt = document.createElement('option');
                opt.value = k.id;
                opt.textContent = k.name;
                classSelect.appendChild(opt);
            });
            
            console.log('✅ Kelas loaded:', kelasList.length);
        } catch (error) {
            console.error('❌ Error loading kelas:', error);
            classSelect.innerHTML = '<option value="">-- Error loading --</option>';
        }
    }

    /* ===============================
       INISIALISASI OTOMATIS (TINGKAT + JURUSAN LOAD BERSAMA)
    =============================== */
    Promise.all([loadTingkat(), loadJurusan()]).then(() => {
        console.log('🎉 Tingkat & Jurusan fully loaded!');
    });

    /* ===============================
       EVENT LISTENERS (HANYA UNTUK KELAS)
    =============================== */
    // Tingkat/Jurusan change → load kelas (sama seperti borrow)
    tingkatSelect?.addEventListener('change', loadKelas);
    jurusanSelect?.addEventListener('change', loadKelas);

    /* ===============================
       LOAD STUDENT BY CLASS
    =============================== */
    classSelect?.addEventListener('change', async () => {
        const classId = classSelect.value;
        studentSelect.innerHTML = '<option value="">-- Loading... --</option>';
        borrowSelect.innerHTML = '<option value="">-- Pilih Kode Peminjaman --</option>';

        if (!classId) {
            studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
            return;
        }

        try {
            console.log('🔔 Loading students for class:', classId);
            const sRes = await fetch('/get_students_by_class_return', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ class_id: classId })
            });
            
            const sText = await sRes.text();
            const students = JSON.parse(sText);

            studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
            students.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.textContent = s.name;
                studentSelect.appendChild(opt);
            });
            
            console.log('✅ Students loaded:', students.length);
        } catch (error) {
            console.error('❌ Error loading students:', error);
            studentSelect.innerHTML = '<option value="">-- Error loading --</option>';
        }
    });

    /* ===============================
       LOAD BORROW BY STUDENT
    =============================== */
    studentSelect?.addEventListener('change', async () => {
        const borrowerId = studentSelect.value;
        borrowSelect.innerHTML = '<option value="">-- Loading... --</option>';

        if (!borrowerId) {
            borrowSelect.innerHTML = '<option value="">-- Pilih Kode Peminjaman --</option>';
            return;
        }

        try {
            console.log('🔔 Loading borrows for student:', borrowerId);
            const res = await fetch('/get_borrows_by_student', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ borrower_id: borrowerId })
            });
            
            const text = await res.text();
            const borrows = JSON.parse(text);

            borrowSelect.innerHTML = '<option value="">-- Pilih Kode Peminjaman --</option>';
            borrows.forEach(b => {
                const opt = document.createElement('option');
                opt.value = b.id;
                opt.textContent = b.name;
                borrowSelect.appendChild(opt);
            });
            
            console.log('✅ Borrows loaded:', borrows.length);
        } catch (error) {
            console.error('❌ Error loading borrows:', error);
            borrowSelect.innerHTML = '<option value="">-- Error loading --</option>';
        }
    });

    /* ===============================
       IMAGE PREVIEW
    =============================== */
    imageInput?.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            if (!file.type.startsWith('image/')) {
                alert('File harus berupa gambar!');
                this.value = '';
                imagePreview.style.display = 'none';
                return;
            }
            imagePreview.src = URL.createObjectURL(file);
            imagePreview.style.display = 'block';
        } else {
            imagePreview.style.display = 'none';
        }
    });

    console.log('✅ RETURN JS READY - TINGKAT & JURUSAN AUTO LOADED');
});