"""
NST Phone Repair — Sistem Pakar Diagnosis Kerusakan iPhone
Flask Web Application Backend
"""
import json
import os
import sys
from threading import Lock
from flask import Flask, render_template, request, jsonify, send_from_directory

# Menambahkan direktori app ke sys.path agar import lokal berjalan di Vercel
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from core.llm_extractor import extract_features_llm
from core.ds_engine import DSEngine

db_lock = Lock()

# ---------------------------------------------------------------
# Path Setup
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
KB_PATH = os.path.join(DATA_DIR, 'optimal_knowledge_base.json')

# ---------------------------------------------------------------
# Load Knowledge Base saat startup
# ---------------------------------------------------------------
with open(KB_PATH, 'r', encoding='utf-8') as f:
    KNOWLEDGE_BASE = json.load(f)

engine = DSEngine(KNOWLEDGE_BASE)

# ---------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=os.path.join(APP_DIR, 'templates'),
    static_folder=os.path.join(APP_DIR, 'static')
)


@app.route('/')
@app.route('/api')
@app.route('/api/index')
def index():
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(APP_DIR, 'static'), filename)


@app.route('/diagnosa', methods=['POST'])
@app.route('/api/diagnosa', methods=['POST'])
@app.route('/api/index/diagnosa', methods=['POST'])
def diagnosa():
    """
    Menerima JSON: {"nama": "...", "tipe_hp": "...", "keluhan": "..."}
    Mengembalikan JSON hasil diagnosis lengkap + dev_log.
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Data tidak valid.'}), 400

    nama = data.get('nama', '').strip()
    tipe_hp = data.get('tipe_hp', '').strip()
    keluhan_raw = data.get('keluhan', '').strip()

    if not nama:
        return jsonify({'success': False, 'error': 'Nama pelanggan harus diisi.'}), 400
    if not tipe_hp:
        return jsonify({'success': False, 'error': 'Tipe ponsel harus diisi.'}), 400
    if not keluhan_raw:
        return jsonify({'success': False, 'error': 'Keluhan tidak boleh kosong.'}), 400

    keluhan_lower = keluhan_raw.lower()

    # ---------------------------------------------------------------
    # Pintu Gerbang Filter Software (Software Gate)
    # ---------------------------------------------------------------
    sw_keywords = [
        'lupa pola', 'flash ulang', 'flashing', 'diflash', 'software', 'sofware', 'instal ulang', 
        'icloud', 'stuck logo', 'bypass', 'downgrade', 'bootloop', 
        'restore ios', 'error itunes', 'itunes error', 'lupa sandi', 
        'lupa password', 'stuck apple', 'logo apple aja'
    ]
    
    is_software = any(k in keluhan_lower for k in sw_keywords)

    if is_software:
        # Default empty features
        empty_features = {
            "Signal": "Normal", "Baterai": "Normal", "LCD": "Normal", "Wifi": "Normal",
            "Touchscreen": "Normal", "Tegangan": "0,8 - 2,2", "Kamera": "Normal",
            "Konektor Cas": "Normal", "Speaker": "Normal", "Mikrofon": "Normal",
            "Backdoor": "Normal", "Housing": "Normal", "Tombol": "Normal"
        }
        return jsonify({
            'success': True,
            'customer': {
                'nama': nama,
                'tipe_hp': tipe_hp,
            },
            'input': {
                'raw': keluhan_raw,
            },
            'features': empty_features,
            'top_diagnosis': 'Masalah / Kerusakan Software',
            'top_probability': 1.0,
            'top_percentage': 100.0,
            'all_diagnoses': [
                {'damage': 'Masalah / Kerusakan Software', 'probability': 1.0, 'percentage': 100.0}
            ],
            'used_fallback': False,
            'active_rules_count': 0,
            'is_software': True,
            'dev_log': {
                'active_rules': [],
                'combination_steps': [],
                'final_mass_combined': {},
                'pignistic_probabilities': {'Masalah / Kerusakan Software': 1.0},
                'fallback_used': False,
                'software_detected': True
            }
        })

    # Jika bukan software, jalankan model Dempster-Shafer hardware
    features = extract_features_llm(keluhan_raw)
    result = engine.run_inference(features)

    return jsonify({
        'success': True,
        'customer': {
            'nama': nama,
            'tipe_hp': tipe_hp,
        },
        'input': {
            'raw': keluhan_raw,
        },
        'features': features,
        'is_software': False,
        **result,
    })


@app.route('/model-info')
@app.route('/api/model-info')
@app.route('/api/index/model-info')
def model_info():
    """Mengembalikan seluruh basis pengetahuan optimal (untuk menu Pengembangan)."""
    return jsonify({
        'rules': KNOWLEDGE_BASE['rules'],
        'class_priors': KNOWLEDGE_BASE['class_priors'],
        'total_rules': len(KNOWLEDGE_BASE['rules']),
        'total_classes': len(KNOWLEDGE_BASE['class_priors']),
    })


@app.route('/feedback', methods=['POST'])
@app.route('/api/feedback', methods=['POST'])
@app.route('/api/index/feedback', methods=['POST'])
def feedback():
    """
    Menerima JSON berisi data kasus baru:
    {"nama": "...", "tipe_hp": "...", "keluhan": "...", "kerusakan_sebenarnya": "..."}
    Memperbarui total_cases, class_counts, dan prior secara online.
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Data tidak valid.'}), 400

    nama = data.get('nama', '').strip()
    tipe_hp = data.get('tipe_hp', '').strip()
    keluhan = data.get('keluhan', '').strip()
    kerusakan = data.get('kerusakan_sebenarnya', '').strip()

    if not all([nama, tipe_hp, keluhan, kerusakan]):
        return jsonify({'success': False, 'error': 'Semua field (nama, tipe_hp, keluhan, kerusakan_sebenarnya) wajib diisi.'}), 400

    global KNOWLEDGE_BASE
    
    with db_lock:
        try:
            total_cases = KNOWLEDGE_BASE.get('total_cases', 736)
            class_counts = KNOWLEDGE_BASE.get('class_counts', {})
            
            if kerusakan not in class_counts:
                return jsonify({'success': False, 'error': f'Kelas kerusakan {kerusakan} tidak terdaftar.'}), 400

            class_counts[kerusakan] += 1
            total_cases += 1

            new_priors = {}
            for cls, cnt in class_counts.items():
                new_priors[cls] = cnt / total_cases

            KNOWLEDGE_BASE['total_cases'] = total_cases
            KNOWLEDGE_BASE['class_counts'] = class_counts
            KNOWLEDGE_BASE['class_priors'] = new_priors

            engine.priors = new_priors

            with open(KB_PATH, 'w', encoding='utf-8') as f:
                json.dump(KNOWLEDGE_BASE, f, indent=2, ensure_ascii=False)

            log_path = os.path.join(DATA_DIR, 'feedback_log.json')
            log_entry = {
                'nama': nama,
                'tipe_hp': tipe_hp,
                'keluhan': keluhan,
                'kerusakan_sebenarnya': kerusakan,
                'timestamp': '2026-06-29T20:20:00+07:00'
            }
            
            feedback_list = []
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8') as lf:
                        feedback_list = json.load(lf)
                except Exception:
                    feedback_list = []
            
            feedback_list.append(log_entry)
            with open(log_path, 'w', encoding='utf-8') as lf:
                json.dump(feedback_list, lf, indent=2, ensure_ascii=False)

            return jsonify({
                'success': True,
                'message': 'Pengetahuan model berhasil dimutakhirkan secara dinamis.',
                'new_prior': new_priors[kerusakan],
                'total_cases': total_cases
            })
        except Exception as e:
            return jsonify({'success': False, 'error': f'Gagal memutakhirkan model: {str(e)}'}), 500


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == '__main__':
    print("=" * 55)
    print("  NST Phone Repair — Sistem Pakar Kerusakan iPhone")
    print("  Buka browser: http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, port=5000)

