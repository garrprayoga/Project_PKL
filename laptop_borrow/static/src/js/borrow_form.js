document.addEventListener('DOMContentLoaded', function() {
  const classSelect = document.getElementById('class_id');
  const studentSelect = document.getElementById('borrower_id');
  const tujuanSelect = document.getElementById('tujuan_peminjaman');
  const mapelField = document.getElementById('mapel_field');
  const ketField = document.getElementById('keterangan_field');
  const jumlahInput = document.getElementById('jumlah_pinjam');
  const checkboxes = document.querySelectorAll('.laptop-checkbox');
  const form = document.getElementById('borrow-form');

  // Load siswa
  classSelect.addEventListener('change', async function() {
    const classId = this.value;
    studentSelect.innerHTML = '<option value="">-- Memuat... --</option>';
    if (classId) {
      const response = await fetch('/get_students_by_class', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ class_id: classId })
      });
      const students = await response.json();
      studentSelect.innerHTML = '<option value="">-- Pilih Nama --</option>';

      students.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.textContent = s.name;
        studentSelect.appendChild(opt);
      });
    }
  });

  // Toggle dan required dinamis
  tujuanSelect.addEventListener('change', function() {
    const guruInput = mapelField.querySelector('input');
    const ketInput = ketField.querySelector('textarea');

    if (this.value === 'kbm') {
      mapelField.style.display = 'block';
      ketField.style.display = 'none';

      guruInput.required = true;
      ketInput.required = false;

    } else if (this.value === 'lainnya') {
      mapelField.style.display = 'none';
      ketField.style.display = 'block';

      guruInput.required = false;
      ketInput.required = true;

    } else {
      mapelField.style.display = 'none';
      ketField.style.display = 'none';

      guruInput.required = false;
      ketInput.required = false;
    }
  });

  // Batasi checkbox
  function updateCheckboxLimit() {
    const maxAllowed = parseInt(jumlahInput.value) || 0;
    const checked = document.querySelectorAll('.laptop-checkbox:checked');

    if (checked.length >= maxAllowed) {
      checkboxes.forEach(cb => {
        if (!cb.checked) cb.disabled = true;
      });
    } else {
      checkboxes.forEach(cb => cb.disabled = false);
    }
  }

  jumlahInput.addEventListener('input', updateCheckboxLimit);
  checkboxes.forEach(cb => cb.addEventListener('change', updateCheckboxLimit));

  // Validasi tambahan
  form.addEventListener('submit', function(e) {
    const guruInput = mapelField.querySelector('input');
    const ketInput = ketField.querySelector('textarea');

    if (tujuanSelect.value === 'kbm' && !guruInput.value.trim()) {
      alert('⚠ Mohon isi Nama Guru Mapel!');
      guruInput.focus();
      e.preventDefault();
      return;
    }

    if (tujuanSelect.value === 'lainnya' && !ketInput.value.trim()) {
      alert('⚠ Mohon isi Keterangan!');
      ketInput.focus();
      e.preventDefault();
      return;
    }

    const maxAllowed = parseInt(jumlahInput.value) || 0;
    const checkedBoxes = document.querySelectorAll('.laptop-checkbox:checked');
    if (checkedBoxes.length !== maxAllowed) {
      alert(`⚠ Silakan pilih tepat ${maxAllowed} laptop.`);
      e.preventDefault();
    }
  });
}); 
