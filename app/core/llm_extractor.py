import os
import json
import urllib.request
import urllib.error
import re

# Load manual dari file .env (tanpa dependensi eksternal)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

# Mengambil API Key dari Environment Variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

PROMPT_TEMPLATE = """
Anda adalah asisten ahli teknisi iPhone. Tugas Anda adalah mengekstrak gejala kerusakan dari keluhan pelanggan ke dalam format JSON terstruktur.
Terdapat 13 kategori gejala. Anda harus memilih SATU nilai yang paling tepat untuk setiap kategori berdasarkan keluhan.
Jika keluhan tidak menyebutkan gejala yang berkaitan dengan kategori tersebut, pilih nilai defaultnya (misal: "Normal").

Daftar Kategori dan Pilihan Nilai yang Diizinkan:
1. Signal: "Normal", "Hilang Total", "Bar Rendah"
2. Baterai: "Normal", "Daya Tahan Rendah/Gembung"
3. LCD: "Normal", "Greenscreen", "Gelap"
4. Wifi: "Normal", "Hilang Timbul"
5. Touchscreen: "Normal", "Tidak bisa disentuh"
6. Tegangan: "0,8 - 2,2", "0,6", "0,0" (Catatan: Default "0,8 - 2,2". Pilih "0,0" jika mati total/konslet/masuk air/korosi. Pilih "0,6" jika vcc main)
7. Kamera: "Normal", "Blank"
8. Konektor Cas: "Normal", "Tidak Ngecas", "Keluar masuk"
9. Speaker: "Normal", "Rusak" (Untuk suara dering/musik/audio tidak keluar atau pecah)
10. Mikrofon: "Normal", "Tidak Berfungsi" (Untuk rekam suara rusak, atau lawan bicara telepon tidak bisa mendengar)
11. Backdoor: "Normal", "Pecah/Retak"
12. Housing: "Normal", "Pecah/Retak/Bengkok"
13. Tombol: "Normal", "Tidak Berfungsi"

Keluhan Pelanggan: "{keluhan}"

Outputkan HANYA JSON murni (tanpa block markdown, tanpa penjelasan lain) dengan struktur persis seperti ini:
{{
  "Signal": "Normal",
  "Baterai": "Normal",
  "LCD": "Normal",
  "Wifi": "Normal",
  "Touchscreen": "Normal",
  "Tegangan": "0,8 - 2,2",
  "Kamera": "Normal",
  "Konektor Cas": "Normal",
  "Speaker": "Normal",
  "Mikrofon": "Normal",
  "Backdoor": "Normal",
  "Housing": "Normal",
  "Tombol": "Normal"
}}
"""

def extract_features_llm(keluhan: str) -> dict:
    """
    Mengirimkan keluhan ke Gemini API dan mengembalikan dictionary fitur.
    Jika API gagal atau API Key tidak ada, gunakan default fallback.
    """
    default_features = {
        "Signal": "Normal", "Baterai": "Normal", "LCD": "Normal",
        "Wifi": "Normal", "Touchscreen": "Normal", "Tegangan": "0,8 - 2,2",
        "Kamera": "Normal", "Konektor Cas": "Normal", "Speaker": "Normal",
        "Mikrofon": "Normal", "Backdoor": "Normal", "Housing": "Normal",
        "Tombol": "Normal"
    }

    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY tidak diatur. Menggunakan fitur default.")
        return default_features

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = PROMPT_TEMPLATE.format(keluhan=keluhan)
    
    payload_dict = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
        }
    }
    
    payload_data = json.dumps(payload_dict).encode('utf-8')
    req = urllib.request.Request(url, data=payload_data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        text_output = data['candidates'][0]['content']['parts'][0]['text']

        
        # Bersihkan jika LLM masih mengembalikan markdown block
        text_output = re.sub(r'^```json', '', text_output, flags=re.IGNORECASE).strip()
        text_output = re.sub(r'^```', '', text_output).strip()
        text_output = re.sub(r'```$', '', text_output).strip()
        
        features = json.loads(text_output)
        
        # Merge dengan default untuk memastikan semua key ada (kalau LLM salah format)
        final_features = default_features.copy()
        for k, v in features.items():
            if k in final_features:
                final_features[k] = v
                
        return final_features
        
    except Exception as e:
        print(f"ERROR LLM API: {e}")
        return default_features
