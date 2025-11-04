/** @odoo-module **/

document.addEventListener('DOMContentLoaded', function() {
    const tujuanSelect = document.getElementById('tujuan_peminjaman');
    const mapelField = document.getElementById('mapel_field');
    const keteranganField = document.getElementById('keterangan_field');
    const classSelect = document.getElementById('class_id');
    const borrowerSelect = document.getElementById('borrower_id');

    // tampilkan field guru_mapel / keterangan tergantung pilihan
    if (tujuanSelect) {
        tujuanSelect.addEventListener('change', function() {
            const val = this.value;
            mapelField.style.display = (val === 'kbm') ? 'block' : 'none';
            keteranganField.style.display = (val === 'lainnya') ? 'block' : 'none';
        });
    }

    // ambil siswa berdasarkan kelas
    if (classSelect) {
        classSelect.addEventListener('change', async function() {
            const classId = this.value;
            borrowerSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';
            if (!classId) return;

            try {
                const res = await fetch('/get_students_by_class', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({class_id: classId})
                });
                const students = await res.json();

                students.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id;
                    opt.textContent = s.name;
                    borrowerSelect.appendChild(opt);
                });
            } catch (error) {
                console.error('Gagal ambil data siswa:', error);
            }
        });
    }
});