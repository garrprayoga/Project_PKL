document.addEventListener('DOMContentLoaded', function () {
    const classSelect = document.getElementById('class_id');
    const studentSelect = document.getElementById('borrower_id');
    const tujuanSelect = document.getElementById('tujuan_peminjaman');
    const mapelField = document.getElementById('mapel_field');
    const ketField = document.getElementById('keterangan_field');
    const jumlahInput = document.getElementById('jumlah_pinjam');
    const checkboxes = document.querySelectorAll('.laptop-checkbox');

    // 🔹 Load siswa by class (AJAX)
    classSelect?.addEventListener('change', async function () {
        const classId = this.value;
        studentSelect.innerHTML = '<option value="">-- Memuat... --</option>';
        if (classId) {
            try {
                const response = await fetch('/get_students_by_class', {
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
            } catch (err) {
                console.error('Error:', err);
                studentSelect.innerHTML = '<option value="">(Gagal memuat data)</option>';
            }
        } else {
            studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
        }
    });

    // 🔹 Toggle field berdasarkan tujuan
    tujuanSelect?.addEventListener('change', function () {
        mapelField.style.display = this.value === 'kbm' ? 'block' : 'none';
        ketField.style.display = this.value === 'lainnya' ? 'block' : 'none';
    });

    // 🔹 Batasi jumlah checkbox sesuai input jumlah
    function updateCheckboxLimit() {
        const maxAllowed = parseInt(jumlahInput.value) || 0;
        const checkedBoxes = document.querySelectorAll('.laptop-checkbox:checked');

        if (checkedBoxes.length >= maxAllowed) {
            checkboxes.forEach(cb => {
                if (!cb.checked) cb.disabled = true;
            });
        } else {
            checkboxes.forEach(cb => cb.disabled = false);
        }
    }

    jumlahInput?.addEventListener('input', updateCheckboxLimit);
    checkboxes.forEach(cb => cb.addEventListener('change', updateCheckboxLimit));
});