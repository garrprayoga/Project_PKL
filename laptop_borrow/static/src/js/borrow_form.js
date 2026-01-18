document.addEventListener('DOMContentLoaded', () => {

    const classSelect   = document.getElementById('class_id');
    const studentSelect = document.getElementById('borrower_id');
    const productSelect = document.getElementById('product_id');
    const jumlahInput   = document.getElementById('jumlah_pinjam');
    const serialBox     = document.getElementById('serial_container');
    const tujuanSelect  = document.getElementById('tujuan_peminjaman');
    const mapelField    = document.getElementById('mapel_field');
    const ketField      = document.getElementById('keterangan_field');
    const form          = document.getElementById('borrow-form');

    let classBlocked = false;

    /* ===============================
       LIMIT CHECKBOX SESUAI JUMLAH
    =============================== */
    function updateCheckboxLimit() {
        const max = parseInt(jumlahInput.value) || 0;
        const checked = serialBox.querySelectorAll('.laptop-checkbox:checked').length;

        serialBox.querySelectorAll('.laptop-checkbox').forEach(cb => {
            cb.disabled = checked >= max && !cb.checked;
        });
    }

    /* ===============================
       RENDER SERIAL
    =============================== */
    function renderSerials(serials) {
        serialBox.innerHTML = '';

        if (!serials.length) {
            serialBox.innerHTML = '<div class="list-group-item text-muted">Tidak ada serial tersedia</div>';
            return;
        }

        serials.forEach(s => {
            serialBox.insertAdjacentHTML('beforeend', `
                <label class="list-group-item d-flex align-items-center">
                    <input type="checkbox"
                           class="form-check-input me-2 laptop-checkbox"
                           name="lot_id"
                           value="${s.id}">
                    ${s.name}
                </label>
            `);
        });

        updateCheckboxLimit();
    }

    /* ===============================
       PILIH KELAS
    =============================== */
    classSelect?.addEventListener('change', async () => {
        const classId = classSelect.value;
        studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
        classBlocked = false;

        if (!classId) return;

        try {
            console.log('🔔 Checking class:', classId);
            
            // cek kelas dipinjam
            const res = await fetch('/check_class_borrow_status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ class_id: classId })
            });
            
            const text = await res.text();
            console.log('📥 Response:', text);
            
            const result = JSON.parse(text);

            if (result.blocked) {
                alert(result.message);
                classSelect.value = '';
                classBlocked = true;
                return;
            }

            // load siswa
            const sRes = await fetch('/get_students_by_class', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ class_id: classId })
            });
            
            const sText = await sRes.text();
            console.log('👥 Students:', sText);
            
            const students = JSON.parse(sText);

            students.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.textContent = s.name;
                studentSelect.appendChild(opt);
            });
            
            console.log('✅ Students loaded:', students.length);
        } catch (error) {
            console.error('❌ Error loading class data:', error);
            alert('Terjadi kesalahan saat memuat data. Silakan coba lagi.');
        }
    });

    /* ===============================
       PILIH BARANG → LOAD SERIAL
    =============================== */
    productSelect?.addEventListener('change', async () => {
        const productId = productSelect.value;
        serialBox.innerHTML = '<div class="list-group-item text-muted">Memuat...</div>';

        if (!productId) {
            serialBox.innerHTML = '<div class="list-group-item text-muted">Pilih jenis barang terlebih dahulu</div>';
            return;
        }

        try {
            console.log('🔔 Loading serials for product:', productId);
            
            const res = await fetch('/get_serials_by_product', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ product_id: productId })
            });

            const text = await res.text();
            console.log('📥 Serials response:', text);
            
            const serials = JSON.parse(text);
            
            console.log('📦 Serials loaded:', serials.length);
            renderSerials(serials);
        } catch (error) {
            console.error('❌ Error loading serials:', error);
            serialBox.innerHTML = '<div class="list-group-item text-danger">Gagal memuat data. Silakan refresh halaman.</div>';
        }
    });

    /* ===============================
       JUMLAH PINJAM
    =============================== */
    jumlahInput?.addEventListener('input', updateCheckboxLimit);

    document.addEventListener('change', e => {
        if (e.target.classList.contains('laptop-checkbox')) {
            updateCheckboxLimit();
        }
    });

    /* ===============================
       TUJUAN PEMINJAMAN
    =============================== */
    tujuanSelect?.addEventListener('change', () => {
        mapelField.style.display = 'none';
        ketField.style.display = 'none';

        if (tujuanSelect.value === 'kbm') {
            mapelField.style.display = 'block';
        }
        if (tujuanSelect.value === 'lainnya') {
            ketField.style.display = 'block';
        }
    });

    /* ===============================
       VALIDASI SUBMIT
    =============================== */
    form?.addEventListener('submit', e => {
        if (classBlocked) {
            alert('Kelas masih memiliki peminjaman aktif');
            e.preventDefault();
            return;
        }

        const max = parseInt(jumlahInput.value) || 0;
        const checked = serialBox.querySelectorAll('.laptop-checkbox:checked').length;

        if (checked !== max) {
            alert(`Pilih TEPAT ${max} serial (sekarang ${checked})`);
            e.preventDefault();
        }
    });

    console.log('✅ BORROW JS READY');
});