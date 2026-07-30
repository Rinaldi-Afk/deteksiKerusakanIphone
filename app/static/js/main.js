/* ── JS utama NST Phone Repair (Unified Dashboard) ── */

// DOM Elements
const namaInput       = document.getElementById('nama-pelanggan');
const tipeHpSelect    = document.getElementById('tipe-hp');
const tipeHpCustomCon = document.getElementById('tipe-hp-custom-container');
const tipeHpCustomInput= document.getElementById('tipe-hp-custom');
const keluhanInput    = document.getElementById('keluhan-input');
const btnDiagnosa     = document.getElementById('btn-diagnosa');
const btnText         = document.getElementById('btn-text');
const spinner         = document.getElementById('spinner');
const normPreview     = document.getElementById('normalized-preview');
const featuresBody    = document.getElementById('features-body');
const resultPanel     = document.getElementById('result-panel');
const btnPrint        = document.getElementById('btn-print');

// Print Elements
const printNama       = document.getElementById('print-nama');
const printTipe       = document.getElementById('print-tipe');
const printWaktu      = document.getElementById('print-waktu');
const printKeluhan    = document.getElementById('print-keluhan');

// State terakhir untuk log pengembangan
window._lastResult = null;

// ============================================================
// Event Listeners untuk Validasi Form
// ============================================================

// Monitor perubahan tipe HP
tipeHpSelect.addEventListener('change', () => {
  if (tipeHpSelect.value === 'Lainnya') {
    tipeHpCustomCon.style.display = 'block';
    tipeHpCustomInput.focus();
  } else {
    tipeHpCustomCon.style.display = 'none';
    tipeHpCustomInput.value = '';
  }
  validateCustomerData();
});

// Monitor perubahan input nama dan input tipe HP custom
namaInput.addEventListener('input', validateCustomerData);
tipeHpCustomInput.addEventListener('input', validateCustomerData);

// Monitor keluhan input
keluhanInput.addEventListener('input', () => {
  const keluhan = keluhanInput.value.trim();
  if (keluhan.length >= 3) {
    btnDiagnosa.disabled = false;
  } else {
    btnDiagnosa.disabled = true;
  }
});

// Jalankan diagnosis jika tombol diklik atau Ctrl+Enter ditekan
btnDiagnosa.addEventListener('click', runDiagnosis);
keluhanInput.addEventListener('keydown', e => {
  if (e.ctrlKey && e.key === 'Enter' && !btnDiagnosa.disabled) {
    runDiagnosis();
  }
});

// Fungsi validasi data pelanggan
function validateCustomerData() {
  const nama = namaInput.value.trim();
  const tipeHp = tipeHpSelect.value;
  let isTipeHpValid = tipeHp !== "";

  if (tipeHp === 'Lainnya') {
    isTipeHpValid = tipeHpCustomInput.value.trim() !== "";
  }

  if (nama.length > 0 && isTipeHpValid) {
    keluhanInput.disabled = false;
    keluhanInput.placeholder = "Contoh: baterai drop cepat habis, layar gelap tidak nyala, tidak bisa dicas... (Ctrl+Enter untuk diagnosa)";
    
    // Jika keluhan sudah diisi sebelumnya
    if (keluhanInput.value.trim().length >= 3) {
      btnDiagnosa.disabled = false;
    }
  } else {
    keluhanInput.disabled = true;
    btnDiagnosa.disabled = true;
    keluhanInput.placeholder = "Isi nama pelanggan & tipe ponsel terlebih dahulu untuk mengaktifkan kolom keluhan...";
  }
}

// ============================================================
// Logika Diagnosis (POST Request)
// ============================================================
async function runDiagnosis() {
  const nama = namaInput.value.trim();
  let tipeHp = tipeHpSelect.value;
  if (tipeHp === 'Lainnya') {
    tipeHp = tipeHpCustomInput.value.trim();
  }
  const keluhan = keluhanInput.value.trim();

  if (!nama || !tipeHp || !keluhan) {
    return;
  }

  // Loading state
  btnDiagnosa.disabled = true;
  spinner.style.display = 'block';
  btnText.textContent = 'Menganalisis...';

  try {
    const res = await fetch('/diagnosa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nama, tipe_hp: tipeHp, keluhan }),
    });
    const data = await res.json();

    if (!data.success) {
      alert('Error: ' + (data.error || 'Terjadi kesalahan.'));
      return;
    }

    window._lastResult = data;
    
    // Tampilkan tombol cetak
    btnPrint.style.display = 'inline-flex';
    
    // Isi data cetak
    printNama.textContent = data.customer.nama;
    printTipe.textContent = data.customer.tipe_hp;
    printWaktu.textContent = new Date().toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' });
    printKeluhan.textContent = data.input.raw;

    // Render komponen visual
    renderFeatures(data.features);
    renderResult(data);
    renderNormalized(data.input.normalized);
    renderLastLog(data);

  } catch (err) {
    alert('Koneksi ke server gagal: ' + err.message);
  } finally {
    btnDiagnosa.disabled = false;
    spinner.style.display = 'none';
    btnText.textContent = 'Diagnosa Ulang';
  }
}

// ---- Normalized text preview ----
function renderNormalized(normalized) {
  normPreview.style.display = 'block';
  normPreview.innerHTML = `Teks ternormalisasi: <span>${escHtml(normalized)}</span>`;
}

// ---- Features table ----
function renderFeatures(features) {
  const NORMAL_VALS = ['Normal', '0,8 - 2,2'];
  featuresBody.innerHTML = '';
  Object.entries(features).forEach(([col, val]) => {
    const isActive = !NORMAL_VALS.includes(val);
    const badgeClass = isActive ? 'badge-active' : 'badge-normal';
    featuresBody.innerHTML += `
      <tr>
        <td><b>${escHtml(col)}</b></td>
        <td><span class="badge ${badgeClass}">${escHtml(val)}</span></td>
      </tr>`;
  });
}

// ---- Result panel ----
// ---- Result panel ----
function renderResult(data) {
  if (data.is_software) {
    resultPanel.innerHTML = `
      <div class="fallback-notice" id="fallback-notice" style="display: block; background: var(--primary-light); border-color: #BFDBFE; color: var(--primary-dark);">
        ℹ Masalah Sistem Operasi Terdeteksi (Software Gate Filter)
      </div>
      
      <div class="top-diagnosis-box" style="background: var(--success-light); border-color: #A7F3D0;">
        <div class="top-diag-icon" style="background: var(--success);">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
               fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </div>
        <div>
          <div class="top-diag-label" style="color: var(--success);">Kesimpulan Diagnosis</div>
          <div class="top-diag-name" style="color: #065F46;">${escHtml(data.top_diagnosis)}</div>
          <div class="top-diag-pct" style="color: #065F46;">Tingkat Keyakinan: <b>100.0%</b> · Deteksi Kata Kunci Sistem</div>
        </div>
      </div>
      
      <div class="card-title" style="font-size:12px; color:var(--gray-500); margin-bottom:10px;">
        Panduan Solusi Penanganan Software iPhone
      </div>
      <div style="font-size: 13px; color: var(--gray-700); line-height: 1.6; padding: 14px; background: var(--gray-50); border: 1px solid var(--gray-200); border-radius: 8px;">
        <p style="margin-bottom: 8px;"><b>Rekomendasi Tindakan Teknisi:</b></p>
        <ol style="margin-left: 20px;">
          <li style="margin-bottom: 4px;">Sambungkan iPhone ke PC/Mac menggunakan kabel Lightning/USB-C original.</li>
          <li style="margin-bottom: 4px;">Gunakan aplikasi resmi <b>Apple Devices / iTunes</b> atau tool pihak ketiga terpercaya seperti <b>3uTools</b>.</li>
          <li style="margin-bottom: 4px;">Lakukan proses <b>Flash / Restore</b> menggunakan firmware iOS (.ipsw) resmi paling baru yang ditandatangani oleh Apple.</li>
          <li style="margin-bottom: 4px;">Jika mengalami masalah aktivasi iCloud (Activation Lock), bantu pelanggan memulihkan Apple ID atau lakukan verifikasi kepemilikan.</li>
        </ol>
      </div>`;
    return;
  }

  const topPct   = data.top_percentage;
  const allDiag  = data.all_diagnoses;
  const maxPct   = allDiag[0].percentage;

  let barsHtml = allDiag.map((d, i) => {
    const pct  = d.percentage;
    const w    = maxPct > 0 ? (pct / maxPct * 100).toFixed(1) : 0;
    const cls  = i === 0 ? 'bar-top' : 'bar-low';
    return `
      <div class="bar-row">
        <span class="bar-label" title="${escHtml(d.damage)}">${escHtml(d.damage)}</span>
        <div class="bar-track">
          <div class="bar-fill ${cls}" style="width:${w}%"></div>
        </div>
        <span class="bar-pct">${pct.toFixed(1)}%</span>
      </div>`;
  }).join('');

  // Dropdown opsi feedback
  const DAMAGE_CLASSES = [
    "Antena Signal Rusak",
    "Antena Wifi Rusak",
    "Backdoor Rusak",
    "Baterai Rusak",
    "Housing Rusak",
    "IC Audio Rusak",
    "IC Cas Rusak",
    "IC Power Rusak",
    "IC WTR Rusak",
    "Kamera Rusak",
    "LCD Rusak",
    "Mikrofon Rusak",
    "Port Pengisian Rusak",
    "Speaker Rusak",
    "Tombol Rusak",
    "Touchscreen Rusak"
  ];
  
  const optionsHtml = DAMAGE_CLASSES.map(cls => 
    `<option value="${escHtml(cls)}">${escHtml(cls)}</option>`
  ).join('');

  resultPanel.innerHTML = `
    <div class="fallback-notice" id="fallback-notice" style="display:${data.used_fallback ? 'block' : 'none'}">
      ⚠ Tidak ada gejala spesifik terdeteksi. Klasifikasi dialihkan menggunakan probabilitas prior empiris model.
    </div>
    
    <div class="top-diagnosis-box">
      <div class="top-diag-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
             fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
      </div>
      <div>
        <div class="top-diag-label">Kesimpulan Diagnosis</div>
        <div class="top-diag-name">${escHtml(data.top_diagnosis)}</div>
        <div class="top-diag-pct">Tingkat Keyakinan: <b>${topPct.toFixed(1)}%</b> · ${data.active_rules_count} aturan terpicu</div>
      </div>
    </div>
    
    <div class="card-title" style="font-size:12px; color:var(--gray-500); margin-bottom:10px;">
      Distribusi Probabilitas Pignistik (Semua Kelas)
    </div>
    <div class="bar-list" style="margin-bottom: 20px;">${barsHtml}</div>
    
    <!-- Box Feedback / Pembelajaran Dinamis Model -->
    <div class="feedback-box print-hide" style="margin-top: 20px; padding: 16px; background: var(--gray-50); border: 1.5px dashed var(--gray-200); border-radius: 8px;">
      <div style="font-weight: 700; font-size: 12.5px; color: var(--gray-900); margin-bottom: 4px;">
        Diagnosis Kurang Tepat?
      </div>
      <div style="font-size: 11.5px; color: var(--gray-500); margin-bottom: 10px; line-height: 1.4;">
        Bantu model belajar dengan mengoreksi kerusakan yang sebenarnya terjadi. Prior empiris model akan langsung disesuaikan secara dinamis.
      </div>
      <div style="display: flex; gap: 8px; align-items: center;">
        <select id="feedback-select" style="flex: 1; padding: 8px 10px; font-size: 12.5px; border-radius: 6px; border: 1.5px solid var(--gray-200); outline: none; background: #fff;">
          <option value="" disabled selected>Pilih kerusakan yang benar...</option>
          ${optionsHtml}
        </select>
        <button class="btn-secondary" id="btn-submit-feedback" style="padding: 8px 14px; font-size: 12.5px; font-weight: 600;" onclick="submitFeedback()">
          Simpan Koreksi
        </button>
      </div>
      <div id="feedback-success-msg" style="display: none; margin-top: 8px; font-size: 12px; color: var(--success); font-weight: 600;">
        ✓ Sukses! Umpan balik dicatat dan prior empiris model diperbarui secara dinamis.
      </div>
    </div>`;
}

// Fungsi submit feedback ke backend secara asinkron
async function submitFeedback() {
  const selectEl = document.getElementById('feedback-select');
  const successEl = document.getElementById('feedback-success-msg');
  const btnEl = document.getElementById('btn-submit-feedback');
  
  const kerusakanSebenarnya = selectEl.value;
  if (!kerusakanSebenarnya) {
    alert("Silakan pilih jenis kerusakan yang benar terlebih dahulu.");
    return;
  }
  
  if (!window._lastResult) return;
  
  const payload = {
    nama: window._lastResult.customer.nama,
    tipe_hp: window._lastResult.customer.tipe_hp,
    keluhan: window._lastResult.input.raw,
    kerusakan_sebenarnya: kerusakanSebenarnya
  };
  
  btnEl.disabled = true;
  btnEl.textContent = "Menyimpan...";
  
  try {
    const res = await fetch('/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const resData = await res.json();
    
    if (resData.success) {
      successEl.style.display = "block";
      successEl.textContent = `✓ Sukses! Prior '${kerusakanSebenarnya}' kini diperbarui menjadi ${(resData.new_prior * 100).toFixed(2)}% (total ${resData.total_cases} kasus).`;
      
      // Muat ulang info model agar tabel prior di layar langsung sinkron
      await loadModelInfo();
    } else {
      alert("Gagal mengirim umpan balik: " + resData.error);
    }
  } catch (err) {
    alert("Koneksi gagal: " + err.message);
  } finally {
    btnEl.disabled = false;
    btnEl.textContent = "Simpan Koreksi";
  }
}

// ============================================================
// Model Info & Basis Pengetahuan
// ============================================================
async function loadModelInfo() {
  try {
    const res  = await fetch('/model-info');
    const data = await res.json();
    renderModelStats(data);
    renderBeliefTable(data.rules);
    renderPriorTable(data.class_priors);
  } catch (err) {
    console.error("Gagal memuat info model:", err);
  }
}

function renderModelStats(data) {
  document.getElementById('stat-rules').textContent   = data.total_rules;
  document.getElementById('stat-classes').textContent = data.total_classes;
  const dims = data.rules.reduce((s, r) => s + r.hypotheses.length, 0);
  document.getElementById('stat-dims').textContent    = dims;
}

function renderBeliefTable(rules) {
  const tbody = document.getElementById('belief-tbody');
  tbody.innerHTML = '';
  rules.forEach(rule => {
    rule.hypotheses.forEach((hyp, i) => {
      tbody.innerHTML += `
        <tr>
          ${i === 0 ? `<td rowspan="${rule.hypotheses.length}"><b>${escHtml(rule.symptom_col)}</b><br>
            <small style="color:var(--gray-500)">= ${escHtml(rule.symptom_val)}</small></td>` : ''}
          <td>${escHtml(hyp.damage)}</td>
          <td class="belief-val">${hyp.optimal_belief.toFixed(4)}</td>
          ${i === 0 ? `<td rowspan="${rule.hypotheses.length}" class="theta-val">${rule.uncertainty_theta.toFixed(4)}</td>` : ''}
        </tr>`;
    });
  });
}

function renderPriorTable(priors) {
  const tbody   = document.getElementById('prior-tbody');
  const sorted  = Object.entries(priors).sort((a, b) => b[1] - a[1]);
  const maxPrior = sorted[0][1];
  tbody.innerHTML = sorted.map(([cls, p]) => {
    const w = (p / maxPrior * 100).toFixed(1);
    const pct = (p * 100).toFixed(2);
    return `
      <tr>
        <td>${escHtml(cls)}</td>
        <td style="width:130px">
          <div style="display:flex;align-items:center;">
            <div class="prior-bar-track" style="flex:1">
              <div class="prior-bar-fill" style="width:${w}%"></div>
            </div>
          </div>
        </td>
        <td style="font-weight:600;color:var(--success)">${pct}%</td>
      </tr>`;
  }).join('');
}

// ---- Log Inferensi Terakhir ----
function renderLastLog(data) {
  const container = document.getElementById('last-inference-log');
  const devLog    = data.dev_log;

  let html = `
    <div class="log-card">
      <div class="log-header">📋 Log Inferensi & Langkah Kombinasi Dempster-Shafer</div>
      <div class="log-body">

        <div class="log-section-title">Informasi Kasus & Input</div>
        <div class="mass-grid" style="margin-bottom: 12px;">
          <div class="mass-row"><span class="mass-key">Nama Pelanggan</span><span class="mass-val">${escHtml(data.customer.nama)}</span></div>
          <div class="mass-row"><span class="mass-key">Tipe iPhone</span><span class="mass-val">${escHtml(data.customer.tipe_hp)}</span></div>
          <div class="mass-row"><span class="mass-key">Teks Keluhan</span><span class="mass-val" style="font-style: italic;">"${escHtml(data.input.raw)}"</span></div>
          <div class="mass-row"><span class="mass-key">Prapemrosesan</span><span class="mass-val">${escHtml(data.input.normalized)}</span></div>
        </div>

        <div class="log-section-title">Gejala Terdeteksi & Nilai Belief Pakar (${devLog.active_rules.length} Aturan Aktif)</div>`;

  if (devLog.active_rules.length === 0) {
    html += `<div style="color:var(--gray-400);font-size:12.5px;padding:8px 0;">
               Tidak ada gejala spesifik terdeteksi (semua bernilai 'Normal'). Model dialihkan ke mode fallback prior.
             </div>`;
  } else {
    devLog.active_rules.forEach(rule => {
      html += `<div class="log-rule-item">
        <div class="rule-head">${escHtml(rule.symptom_col)} = ${escHtml(rule.symptom_val)}</div>`;
      rule.hypotheses.forEach(hyp => {
        html += `<div class="hyp-row">
          <span>${escHtml(hyp.damage)}</span>
          <span class="belief-val">m({${escHtml(hyp.damage)}}) = ${hyp.optimal_belief.toFixed(4)}</span>
        </div>`;
      });
      html += `<div class="hyp-row" style="color:var(--gray-500); border-top:1px dashed rgba(0,0,0,0.06); padding-top:4px; margin-top:4px;">
                 <span>Uncertainty (Θ)</span>
                 <span>m(Θ) = ${rule.uncertainty_theta.toFixed(4)}</span>
               </div>
             </div>`;
    });
  }

  // Langkah kombinasi DS
  if (devLog.combination_steps.length > 1) {
    html += `<div class="log-section-title">Langkah Kombinasi Dempster-Shafer</div>
             <div class="mass-grid" style="margin-bottom:12px;">`;
    devLog.combination_steps.forEach((step, i) => {
      html += `<div class="mass-row" style="flex-direction:column;align-items:flex-start;gap:4px">
                 <span class="mass-key" style="font-weight:600; color:var(--primary-dark)">Sumber ${i+1}: ${escHtml(step.source)}</span>`;
      Object.entries(step.mass_function).forEach(([k, v]) => {
        html += `<span style="color:var(--gray-500); padding-left:10px;">  m(${escHtml(k)}) = <b>${v}</b></span>`;
      });
      html += `</div>`;
    });
    html += `</div>`;
  }

  // Mass function gabungan akhir
  if (Object.keys(devLog.final_mass_combined).length > 0) {
    html += `<div class="log-section-title">Fungsi Massa Gabungan Akhir m_combined</div>
             <div class="mass-grid" style="margin-bottom:12px;">`;
    Object.entries(devLog.final_mass_combined).forEach(([k, v]) => {
      html += `<div class="mass-row">
                 <span class="mass-key">m(${escHtml(k)})</span>
                 <span class="mass-val">${v}</span>
               </div>`;
    });
    html += `</div>`;
  }

  // Probabilitas Pignistik
  html += `<div class="log-section-title">Probabilitas Pignistik (BetP) Hasil Akhir</div>
           <div class="mass-grid">`;
  const sortedProbs = Object.entries(devLog.pignistic_probabilities)
                            .sort((a, b) => b[1] - a[1]);
  sortedProbs.forEach(([cls, p]) => {
    html += `<div class="mass-row">
               <span class="mass-key">${escHtml(cls)}</span>
               <span class="mass-val">${(p * 100).toFixed(2)}%</span>
             </div>`;
  });
  html += `</div>
      </div>
    </div>`;

  container.innerHTML = html;
}

// ============================================================
// Utilities & Startup
// ============================================================
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Load model info saat inisialisasi awal
window.addEventListener('DOMContentLoaded', loadModelInfo);
