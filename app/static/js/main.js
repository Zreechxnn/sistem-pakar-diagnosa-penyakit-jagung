// ============= STATE =============
let allSymptoms = [];
const GROUP_COLORS = ['bulai','blight','leafrust','burn','stemborer','cobborer'];
const GROUP_NAMES_LOWER = {
  'Bulai': 'bulai',
  'Blight': 'blight',
  'Leaf Rust': 'leafrust',
  'Burn': 'burn',
  'Stem Borer': 'stemborer',
  'Cob Borer': 'cobborer',
};

// ============= LOAD SYMPTOMS =============
async function loadSymptoms() {
  try {
    const res = await fetch('/api/symptoms');
    const data = await res.json();
    allSymptoms = data;
    renderSymptoms(data);
  } catch (err) {
    document.getElementById('symptoms-container').innerHTML = `
      <div style="padding:32px;background:var(--white);border:3px solid var(--black);box-shadow:5px 5px 0 var(--black);">
        <p style="font-family:'Archivo Black',sans-serif;font-size:18px;color:var(--red);text-transform:uppercase;">
          ⚠️ Gagal memuat gejala. Pastikan server berjalan.
        </p>
      </div>`;
  }
}

function renderSymptoms(groups) {
  const container = document.getElementById('symptoms-container');
  container.innerHTML = '';

  let totalCount = 0;
  groups.forEach((group, gi) => {
    totalCount += group.symptoms.length;
    const colorClass = GROUP_COLORS[gi] || 'bulai';

    const groupDiv = document.createElement('div');
    groupDiv.className = 'disease-group';
    groupDiv.dataset.group = gi;

    // Header
    const header = document.createElement('div');
    header.className = 'disease-group-header';
    header.innerHTML = `
      <span class="group-color ${colorClass}"></span>
      <span class="group-name">${group.disease}</span>
      <span class="group-check-count" id="count-group-${gi}">0 dipilih</span>
      <span class="group-chevron">▼</span>
    `;
    header.addEventListener('click', () => {
      groupDiv.classList.toggle('collapsed');
    });
    groupDiv.appendChild(header);

    // Grid
    const grid = document.createElement('div');
    grid.className = 'checkbox-grid';

    group.symptoms.forEach(symptom => {
      const label = document.createElement('label');
      label.className = 'checkbox-item';
      label.htmlFor = `cb-${symptom.code}`;

      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.id = `cb-${symptom.code}`;
      cb.value = symptom.code;
      cb.name = 'gejala';
      cb.addEventListener('change', onCheckboxChange);

      const codeSpan = document.createElement('span');
      codeSpan.className = 'gejala-code';
      codeSpan.textContent = symptom.code;

      const textNode = document.createTextNode(symptom.description);

      label.appendChild(cb);
      label.appendChild(codeSpan);
      label.appendChild(textNode);
      grid.appendChild(label);
    });

    groupDiv.appendChild(grid);
    container.appendChild(groupDiv);
  });

  document.getElementById('total-symptoms-count').textContent = `${totalCount} gejala`;
}

// ============= CHECKBOX CHANGE =============
function onCheckboxChange() {
  const allChecked = document.querySelectorAll('input[name="gejala"]:checked');
  const count = allChecked.length;

  // Update selected bar
  const bar = document.getElementById('selected-bar');
  bar.style.display = count > 0 ? 'flex' : 'none';
  document.getElementById('selected-count').textContent = count;

  // Update per-group counts
  allSymptoms.forEach((group, gi) => {
    const groupDiv = document.querySelector(`[data-group="${gi}"]`);
    if (!groupDiv) return;
    const countEl = document.getElementById(`count-group-${gi}`);
    const groupChecked = groupDiv.querySelectorAll('input:checked').length;
    if (countEl) {
      countEl.textContent = `${groupChecked} dipilih`;
      countEl.classList.toggle('visible', groupChecked > 0);
    }
  });
}

// ============= DIAGNOSE =============
document.getElementById('btn-diagnose').addEventListener('click', async () => {
  // Periksa apakah user sudah login
  if (!currentUser) {
    showError('Akses ditolak. Anda harus masuk (login) terlebih dahulu sebelum dapat melakukan diagnosa.');
    openModal('modal-login');
    return;
  }

  const checked = document.querySelectorAll('input[name="gejala"]:checked');
  const selected = Array.from(checked).map(cb => cb.value);

  if (selected.length === 0) {
    showError('Pilih minimal satu gejala terlebih dahulu!');
    return;
  }

  hideResult();
  hideError();
  showLoading(true);
  document.getElementById('btn-diagnose').disabled = true;

  try {
    const res = await fetch('/api/diagnose', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms: selected })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'Gagal melakukan diagnosa.');
    }

    const data = await res.json();
    displayResult(data);
  } catch (err) {
    showError(err.message);
  } finally {
    showLoading(false);
    document.getElementById('btn-diagnose').disabled = false;
  }
});

// ============= DISPLAY RESULT =============
function displayResult(data) {
  // Reported symptoms
  const tagsContainer = document.getElementById('symptom-tags');
  tagsContainer.innerHTML = '';
  if (data.reported_symptoms && data.reported_symptoms.length > 0) {
    data.reported_symptoms.forEach(s => {
      const tag = document.createElement('div');
      tag.className = 'symptom-tag';
      tag.innerHTML = `<code>${s.code}</code>${s.description}`;
      tagsContainer.appendChild(tag);
    });
    document.getElementById('reported-box').style.display = 'block';
  }

  // Total detected
  document.getElementById('total-detected').textContent = data.total_penyakit_terdeteksi;

  // Diagnosis list
  const list = document.getElementById('diagnosis-list');
  list.innerHTML = '';

  if (!data.diagnosis || data.diagnosis.length === 0) {
    list.innerHTML = `
      <div class="no-result">
        <div class="no-result-icon">🔬</div>
        <div class="no-result-title">Tidak ada penyakit terdeteksi</div>
        <p class="no-result-sub">Coba pilih lebih banyak gejala yang sesuai dengan kondisi tanaman Anda.</p>
      </div>`;
  } else {
    data.diagnosis.forEach((d, i) => {
      const rankClass = i === 0 ? 'rank-1' : i === 1 ? 'rank-2' : 'rank-3';
      const rankBadgeClass = i === 0 ? 'top' : '';
      const rankLabel = i === 0 ? '🥇 TERATAS' : `#${i + 1}`;
      const conf = d.confidence || 0;

      const card = document.createElement('div');
      card.className = `diagnosis-card ${rankClass}`;
      card.innerHTML = `
        <div class="diagnosis-card-header">
          <span class="rank-badge ${rankBadgeClass}">${rankLabel}</span>
          <span class="disease-name">${d.nama}</span>
          <div class="confidence-wrapper">
            <div class="confidence-num">${conf}%</div>
            <div class="confidence-label">Keyakinan</div>
            <div class="confidence-bar-track">
              <div class="confidence-bar-fill" style="width:${conf}%"></div>
            </div>
          </div>
        </div>
        <div class="diagnosis-card-body">
          <div class="info-block">
            <div class="info-block-title">📖 Deskripsi</div>
            <div class="info-block-text">${d.deskripsi}</div>
          </div>
          <div class="info-block">
            <div class="info-block-title">💊 Rekomendasi Penanganan</div>
            <div class="info-block-text">${d.rekomendasi}</div>
          </div>
        </div>
      `;
      list.appendChild(card);
    });
  }

  document.getElementById('result').classList.add('active');
  // Scroll to result
  setTimeout(() => {
    document.getElementById('result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

// ============= RESET =============
document.getElementById('btn-reset').addEventListener('click', () => {
  document.querySelectorAll('input[name="gejala"]:checked').forEach(cb => {
    cb.checked = false;
  });
  onCheckboxChange();
  hideResult();
  hideError();
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ============= HELPERS =============
function hideResult() {
  document.getElementById('result').classList.remove('active');
  document.getElementById('reported-box').style.display = 'none';
}
function showLoading(show) {
  document.getElementById('loading').classList.toggle('active', show);
}
function showError(msg) {
  const el = document.getElementById('error-message');
  document.getElementById('error-text').textContent = msg;
  el.classList.add('active');
}
function hideError() {
  document.getElementById('error-message').classList.remove('active');
}

// ============= AUTH & ADMIN LOGIC =============
let currentUser = null;

function openModal(modalId) {
  document.getElementById(modalId).classList.add('active');
  if (modalId === 'modal-admin') {
    loadUsers();
  } else if (modalId === 'modal-history') {
    loadHistory();
  }
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove('active');
  // Reset forms and errors when closed
  if (modalId === 'modal-login') {
    document.getElementById('form-login').reset();
    document.getElementById('login-error').classList.remove('active');
  } else if (modalId === 'modal-register') {
    document.getElementById('form-register').reset();
    document.getElementById('reg-error').classList.remove('active');
    document.getElementById('reg-success').style.display = 'none';
  } else if (modalId === 'modal-admin') {
    document.getElementById('admin-error').classList.remove('active');
  } else if (modalId === 'modal-history') {
    document.getElementById('history-error').classList.remove('active');
  }
}

function switchModal(fromId, toId) {
  closeModal(fromId);
  setTimeout(() => {
    openModal(toId);
  }, 200);
}

async function checkSession() {
  try {
    const res = await fetch('/api/auth/session');
    const data = await res.json();
    if (data.logged_in) {
      currentUser = data.user;
    } else {
      currentUser = null;
    }
    updateAuthUI();
  } catch (err) {
    console.error('Gagal mengecek sesi:', err);
  }
}

function updateNavbar() {
  const container = document.getElementById('auth-nav-container');
  if (!container) return;

  if (!currentUser) {
    container.innerHTML = `
      <button class="btn-auth" onclick="openModal('modal-login')">Masuk</button>
      <button class="btn-auth" onclick="openModal('modal-register')" style="background:var(--lime);">Daftar</button>
    `;
  } else {
    let adminBtn = '';
    if (currentUser.role === 'admin') {
      adminBtn = `<button class="btn-auth btn-admin" onclick="openModal('modal-admin')">Admin Panel</button>`;
    }
    container.innerHTML = `
      <span class="user-greeting">Halo, ${currentUser.username}</span>
      <button class="btn-auth" onclick="openModal('modal-history')" style="background:var(--cyan); color:var(--black);">Riwayat</button>
      ${adminBtn}
      <button class="btn-auth btn-logout" onclick="handleLogout()">Keluar</button>
    `;
  }
}

function updateAuthUI() {
  updateNavbar();

  const loginPrompt = document.getElementById('login-required-prompt');
  const symptomsContainer = document.getElementById('symptoms-container');
  const btnDiagnose = document.getElementById('btn-diagnose');
  const selectedBar = document.getElementById('selected-bar');

  if (!currentUser) {
    if (loginPrompt) loginPrompt.style.display = 'block';
    if (symptomsContainer) symptomsContainer.style.display = 'none';
    if (btnDiagnose) btnDiagnose.style.display = 'none';
    if (selectedBar) selectedBar.style.display = 'none';
  } else {
    if (loginPrompt) loginPrompt.style.display = 'none';
    if (symptomsContainer) symptomsContainer.style.display = 'block';
    if (btnDiagnose) btnDiagnose.style.display = 'block';
    onCheckboxChange(); // updates display of selectedBar depending on check counts
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const usernameInput = document.getElementById('reg-username').value;
  const passwordInput = document.getElementById('reg-password').value;
  const errorDiv = document.getElementById('reg-error');
  const errorText = document.getElementById('reg-error-text');
  const successDiv = document.getElementById('reg-success');

  errorDiv.classList.remove('active');
  successDiv.style.display = 'none';

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: usernameInput, password: passwordInput })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Gagal mendaftar.');
    }

    successDiv.style.display = 'block';
    document.getElementById('form-register').reset();
    setTimeout(() => {
      switchModal('modal-register', 'modal-login');
    }, 1500);
  } catch (err) {
    errorText.textContent = err.message;
    errorDiv.classList.add('active');
  }
}

async function handleLogin(e) {
  e.preventDefault();
  const usernameInput = document.getElementById('login-username').value;
  const passwordInput = document.getElementById('login-password').value;
  const errorDiv = document.getElementById('login-error');
  const errorText = document.getElementById('login-error-text');

  errorDiv.classList.remove('active');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: usernameInput, password: passwordInput })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Gagal login.');
    }

    currentUser = data.user;
    updateAuthUI();
    closeModal('modal-login');
  } catch (err) {
    errorText.textContent = err.message;
    errorDiv.classList.add('active');
  }
}

async function handleLogout() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
    currentUser = null;
    updateAuthUI();
    // Redirect ke home / reset diagnosa jika perlu
    document.getElementById('btn-reset').click();
  } catch (err) {
    console.error('Gagal logout:', err);
  }
}

async function loadUsers() {
  const tbody = document.getElementById('admin-table-body');
  const errorDiv = document.getElementById('admin-error');
  const errorText = document.getElementById('admin-error-text');

  tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Memuat data user...</td></tr>';
  errorDiv.classList.remove('active');

  try {
    const res = await fetch('/api/auth/users');
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || 'Gagal memuat data user.');
    }

    const users = await res.json();
    tbody.innerHTML = '';
    if (users.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Tidak ada user terdaftar.</td></tr>';
      return;
    }

    users.forEach(u => {
      const tr = document.createElement('tr');
      const roleClass = u.role === 'admin' ? 'role-admin' : 'role-user';
      
      // Format tanggal agar lebih rapi
      const regDate = new Date(u.created_at);
      const formattedDate = regDate.toLocaleString('id-ID', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });

      tr.innerHTML = `
        <td>${u.id}</td>
        <td>${u.username}</td>
        <td><span class="badge-role ${roleClass}">${u.role}</span></td>
        <td>${formattedDate}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--red);">Gagal memuat data.</td></tr>';
    errorText.textContent = err.message;
    errorDiv.classList.add('active');
  }
}

// ============= RIWAYAT DIAGNOSA LOGIC =============
async function loadHistory() {
  const container = document.getElementById('history-list-container');
  const errorDiv = document.getElementById('history-error');
  const errorText = document.getElementById('history-error-text');

  container.innerHTML = '<div style="text-align:center; padding: 24px; font-weight: 700;">⏳ Memuat riwayat...</div>';
  errorDiv.classList.remove('active');

  try {
    const res = await fetch('/api/diagnoses');
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || 'Gagal memuat riwayat.');
    }

    const data = await res.json();
    container.innerHTML = '';

    if (data.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding: 40px 20px; border: 3px dashed var(--black); background: var(--bg);">
          <span style="font-size:48px;">🔬</span>
          <p style="font-family:'Archivo Black', sans-serif; font-size:18px; margin-top:12px; text-transform:uppercase;">Belum Ada Riwayat</p>
          <p style="font-size:14px; font-weight:600; margin-top:6px; color:var(--dark-gray);">Lakukan diagnosa saat login untuk menyimpan riwayat Anda.</p>
        </div>`;
      return;
    }

    data.forEach(item => {
      // Format date
      const dDate = new Date(item.created_at);
      const formattedDate = dDate.toLocaleString('id-ID', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });

      // Symptoms list
      let symptomsHtml = '';
      if (item.symptoms && item.symptoms.length > 0) {
        item.symptoms.forEach(s => {
          symptomsHtml += `
            <div class="history-tag">
              <code>${s.code}</code>
              <span>${s.description}</span>
            </div>`;
        });
      } else {
        symptomsHtml = 'Tidak ada gejala dilaporkan.';
      }

      // Results list
      let resultsHtml = '';
      if (item.result && item.result.length > 0) {
        item.result.forEach((d, i) => {
          const isTop = i === 0;
          const cardClass = isTop ? 'history-result-card top-rank' : 'history-result-card';
          const badgePrefix = isTop ? '🥇 ' : '';
          resultsHtml += `
            <div class="${cardClass}">
              <span class="history-result-name">${badgePrefix}${d.nama} (${d.code})</span>
              <span class="history-result-conf">${d.confidence}%</span>
            </div>`;
        });
      } else {
        resultsHtml = `
          <div class="history-result-card">
            <span class="history-result-name">Tidak ada penyakit terdeteksi</span>
            <span class="history-result-conf" style="background:var(--gray)">-</span>
          </div>`;
      }

      const itemDiv = document.createElement('div');
      itemDiv.className = 'history-item';
      itemDiv.id = `history-item-${item.id}`;
      itemDiv.innerHTML = `
        <div class="history-item-header">
          <span class="history-date">📅 ${formattedDate}</span>
          <button class="btn-delete-history" onclick="deleteHistory(${item.id})">🗑️ Hapus</button>
        </div>
        <div class="history-item-body">
          <div class="history-section">
            <div class="history-section-title">📋 Gejala yang Dipilih:</div>
            <div class="history-tags">
              ${symptomsHtml}
            </div>
          </div>
          <div class="history-section" style="margin-top: 12px;">
            <div class="history-section-title">🔬 Hasil Diagnosa:</div>
            <div class="history-results">
              ${resultsHtml}
            </div>
          </div>
        </div>
      `;
      container.appendChild(itemDiv);
    });
  } catch (err) {
    container.innerHTML = '<div style="text-align:center; padding: 24px; color: var(--red); font-weight:700;">Gagal memuat riwayat.</div>';
    errorText.textContent = err.message;
    errorDiv.classList.add('active');
  }
}

async function deleteHistory(id) {
  if (!confirm('Apakah Anda yakin ingin menghapus riwayat diagnosa ini?')) {
    return;
  }

  try {
    const res = await fetch(`/api/diagnoses/${id}`, {
      method: 'DELETE'
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || 'Gagal menghapus riwayat.');
    }

    // Hapus elemen dari DOM
    const el = document.getElementById(`history-item-${id}`);
    if (el) {
      el.remove();
    }

    // Cek jika tidak ada riwayat tersisa, muat ulang untuk menampilkan placeholder
    const container = document.getElementById('history-list-container');
    if (container.children.length === 0) {
      loadHistory();
    }
  } catch (err) {
    alert(err.message);
  }
}

// ============= INIT =============
loadSymptoms();
checkSession();
