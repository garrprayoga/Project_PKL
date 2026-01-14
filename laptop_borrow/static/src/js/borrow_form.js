document.addEventListener('DOMContentLoaded', function () {

  const classSelect = document.getElementById('class_id');
  const studentSelect = document.getElementById('borrower_id');
  const tujuanSelect = document.getElementById('tujuan_peminjaman');
  const mapelField = document.getElementById('mapel_field');
  const ketField = document.getElementById('keterangan_field');
  const jumlahInput = document.getElementById('jumlah_pinjam');
  const checkboxes = document.querySelectorAll('.laptop-checkbox');
  const form = document.getElementById('borrow-form');

  let classBlocked = false;

   
  // CEK STATUS KELAS
  classSelect.addEventListener('change', async function () {
    const classId = this.value;
    classBlocked = false;

    studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';

    if (!classId) return;

    try {
      const response = await fetch('/check_class_borrow_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ class_id: classId })
      });

      const result = await response.json();

      if (result.blocked) {
        classBlocked = true;
        alert('⚠ ' + result.message);
      }

      const studentsRes = await fetch('/get_students_by_class', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ class_id: classId })
      });

      const students = await studentsRes.json();
      students.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.textContent = s.name;
        studentSelect.appendChild(opt);
      });

    } catch (err) {
      console.error(err);
      alert('Terjadi kesalahan saat cek status kelas');
    }
  });

 
  // TOGGLE TUJUAN
  tujuanSelect.addEventListener('change', function () {
    const guruInput = mapelField.querySelector('input');
    const ketInput = ketField.querySelector('textarea');

    mapelField.style.display = 'none';
    ketField.style.display = 'none';
    guruInput.required = false;
    ketInput.required = false;

    if (this.value === 'kbm') {
      mapelField.style.display = 'block';
      guruInput.required = true;
    } else if (this.value === 'lainnya') {
      ketField.style.display = 'block';
      ketInput.required = true;
    }
  });


  // BATASI JUMLAH CHECKBOX
  function updateCheckboxLimit() {
    const max = parseInt(jumlahInput.value) || 0;
    const checked = document.querySelectorAll('.laptop-checkbox:checked');

    checkboxes.forEach(cb => {
      cb.disabled = checked.length >= max && !cb.checked;
    });
  }

  jumlahInput.addEventListener('input', updateCheckboxLimit);
  checkboxes.forEach(cb => cb.addEventListener('change', updateCheckboxLimit));

 
  // FINAL VALIDASI (ALERT SAJA)
  form.addEventListener('submit', function (e) {

    if (classBlocked) {
      alert('⚠ Kelas ini masih memiliki peminjaman aktif.\nSilakan selesaikan peminjaman sebelumnya.');
      e.preventDefault();
      return;
    }

    const guruInput = mapelField.querySelector('input');
    const ketInput = ketField.querySelector('textarea');

    if (tujuanSelect.value === 'kbm' && !guruInput.value.trim()) {
      alert('⚠ Nama Guru Mapel wajib diisi');
      e.preventDefault();
      return;
    }

    if (tujuanSelect.value === 'lainnya' && !ketInput.value.trim()) {
      alert('⚠ Keterangan wajib diisi');
      e.preventDefault();
      return;
    }

    const max = parseInt(jumlahInput.value) || 0;
    const checked = document.querySelectorAll('.laptop-checkbox:checked');

    if (checked.length !== max) {
      alert(`⚠ Pilih tepat ${max} laptop`);
      e.preventDefault();
    }
  });

});
