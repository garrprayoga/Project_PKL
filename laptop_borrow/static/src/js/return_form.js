document.addEventListener('DOMContentLoaded', function () {
    const classSelect = document.getElementById('class_id');
    const studentSelect = document.getElementById('borrower_id');
    const borrowSelect = document.getElementById('borrow_id');

    // =============================
    // 1. LOAD STUDENT BY CLASS
    // =============================
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

    // =============================
    // 2. LOAD BORROW CODE BY STUDENT
    // =============================
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
});
