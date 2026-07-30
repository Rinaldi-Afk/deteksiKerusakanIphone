import re

# ---------------------------------------------------------------
# Feature Extractor v2.1 - NST Phone Repair
# Mengekstrak 12 kolom gejala terstruktur dari teks keluhan bebas.
# Logika disalin dan diperbaiki dari map_row() di preprocessing.ipynb.
# Perbaikan v2.1:
#   - Fix bug 'turun' trigger baterai saat konteks sinyal
#   - Fix bug 'pecah' trigger LCD saat konteks speaker/audio
#   - Tambah kolom 'Mikrofon' untuk class Mikrofon Rusak
# ---------------------------------------------------------------


def _match(text: str, keywords: list) -> bool:
    """Cek apakah salah satu keyword ditemukan dalam teks."""
    patterns = []
    for k in keywords:
        escaped = re.escape(k).replace(r'\ ', r'\s+')
        patterns.append(rf'\b{escaped}\b')
    pattern = '|'.join(patterns)
    return bool(re.search(pattern, text, re.IGNORECASE))



def _match_negative(text: str, keywords: list) -> bool:
    """
    Versi improvisasi v2.4 (Negasi + Clause Breaker):
    Mencocokkan keyword dalam teks, namun memastikan:
    1. Keyword TIDAK dikaitkan dengan kata normal (misal: "baterai normal") dalam radius 3 kata.
    2. Keyword masalah TIDAK didahului/diikuti kata negasi (misal: "tidak boros", "baterai ga drop").
    3. Konteks window dibatasi oleh pemisah klausa (koma, titik, dan, tapi) agar negasi tidak melompat.
    """
    normal_words = ['normal', 'aman', 'sehat', 'bagus', 'baik', 'awet', 'oke', 'ok', 'lancar', 'mulus']
    negation_words = ['tidak', 'gak', 'ga', 'ndak', 'enggak', 'tdk', 'bukan', 'belom', 'belum']
    problem_words = ['drop', 'boros', 'pecah', 'retak', 'kembung', 'rusak', 'mati', 'gelap', 'buram', 'jamur', 'getar', 'freeze', 'hilang', 'putus', 'panas', 'ngefreeze', 'goyang']
    clause_breakers = [',', '.', ';', 'tapi', 'tetapi', 'dan', 'sedangkan', 'namun', 'cuma', 'cuman']

    if not _match(text, keywords):
        return False

    for kw in keywords:
        escaped = re.escape(kw).replace(r'\ ', r'\s+')
        matches = list(re.finditer(rf'\b{escaped}\b', text, re.IGNORECASE))
        
        for m in matches:
            start, end = m.start(), m.end()
            
            context_before = text[max(0, start - 40):start].strip()
            context_after = text[end:min(len(text), end + 40)].strip()
            
            # Batasi context dengan punctuation / conjunction agar tidak lompat klausa
            for cb in clause_breakers:
                if cb in [',', '.', ';']:
                    idx = context_before.rfind(cb)
                    if idx != -1:
                        context_before = context_before[idx+1:]
                else:
                    parts = re.split(rf'\b{cb}\b', context_before, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        context_before = parts[-1]

            for cb in clause_breakers:
                if cb in [',', '.', ';']:
                    idx = context_after.find(cb)
                    if idx != -1:
                        context_after = context_after[:idx]
                else:
                    parts = re.split(rf'\b{cb}\b', context_after, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        context_after = parts[0]
            
            words_before = [w.lower() for w in re.findall(r'\b\w+\b', context_before)]
            words_after = [w.lower() for w in re.findall(r'\b\w+\b', context_after)]
            
            window_before = words_before[-3:] if words_before else []
            window_after = words_after[:3] if words_after else []
            
            is_negated = False
            
            # 1. Apakah ada kata "normal" / "aman" di sekitarnya?
            if any(nw in window_before for nw in normal_words) or any(nw in window_after for nw in normal_words):
                is_negated = True
                
            # 2. Apakah keyword ini adalah "kata masalah" yang didahului negasi? (misal: "tidak drop")
            if kw in problem_words and any(neg in window_before for neg in negation_words):
                is_negated = True
            
            # 3. Apakah keyword ini adalah komponen yang diikuti negasi dan kata masalah? (misal: "LCD tidak pecah")
            if not is_negated:
                for i, w in enumerate(window_after):
                    if w in negation_words:
                        if i + 1 < len(window_after) and window_after[i+1] in problem_words:
                            is_negated = True
                            break
                            
            if not is_negated:
                return True # Jika ditemukan SATU SAJA keyword yang tidak dinegasi (berarti benar rusak)
                
    return False

def extract_features(normalized_text: str) -> dict:
    """
    Menerima teks yang sudah dinormalisasi,
    mengembalikan dict 12 gejala terstruktur.
    """
    t = normalized_text.lower()

    # ----------------------------------------------------------------
    # Konteks getaran/mesin hidup saat dicas (mesin sehat, cuma layar/baterai)
    # ----------------------------------------------------------------
    has_vibe_on_charge_kw = _match(t, [
        'bergetar saat dicas', 'bergetar saat dicharge', 'bergetar pas dicas',
        'bergetar saat cas', 'getar saat cas', 'ada getaran saat cas',
        'getar saat dicas', 'getar saat dicharge', 'ada getaran saat dicas',
        'ada getaran saat dicharge', 'indicator bergetar', 'dicas bergetar',
        'dicharge bergetar', 'dicas ada getar', 'dicharge ada getar',
        'cas bergetar', 'charge bergetar', 'cas ada getar', 'charge ada getar',
        'mesin getar', 'indikator getar', 'getar saja'
    ])
    has_vibe_on_charge_comb = (
        _match_negative(t, ['getar', 'getaran', 'bergetar']) and
        _match(t, ['cas', 'dicas', 'charge', 'dicharge'])
    )
    has_vibe_on_charge = has_vibe_on_charge_kw or has_vibe_on_charge_comb
    
    # Kata kunci layar/lcd mati/tidak tampil
    has_screen_dead_kw = _match(t, [
        'lcd mati', 'lcd tidak nyala', 'lcd tidak hidup', 'lcd gelap',
        'lcd blank', 'lcd mati total', 'lcd tidak tampil', 'lcd blackscreen'
    ])

    # ----------------------------------------------------------------
    # Konteks negatif yang sering menyebabkan false-positive
    # ----------------------------------------------------------------
    is_speaker_ctx   = _match(t, ['suara', 'speaker', 'buzzer', 'audio',
                                  'dering', 'nada', 'bunyi', 'berbunyi'])
    # Konteks mikrofon: kata kunci yg spesifik menunjuk mic sebagai sumber masalah
    is_mic_ctx       = _match(t, ['mikrofon', 'microphone', 'rekam', 'merekam',
                                  'tidak terdengar', 'tidak dengar',
                                  'pihak lain', 'orang lain'])
    is_backdoor_ctx  = _match(t, ['backdoor', 'kaca belakang', 'punggung'])
    is_housing_ctx   = _match(t, ['housing', 'casing', 'bodi'])
    is_battery_ctx   = _match(t, ['baterai', 'kembung', 'boros', 'mentok',
                                  'daya', 'kapasitas'])
    is_signal_ctx    = _match(t, ['sinyal', 'signal', 'jaringan', 'wifi',
                                  'internet', 'naik turun', 'hilang timbul'])

    # ----------------------------------------------------------------
    # 1. Signal
    # ----------------------------------------------------------------
    if _match(t, ['sinyal hilang', 'signal hilang', 'hilang jaringan',
                  'modem', 'baseband', 'no signal', 'keblokir']):
        signal = 'Hilang Total'
    elif _match(t, ['sinyal lemah', 'signal lemah', 'sinyal naik turun',
                    'signal naik turun', 'signal hilang timbul',
                    'sinyal hilang timbul']):
        signal = 'Bar Rendah'
    else:
        signal = 'Normal'

    # ----------------------------------------------------------------
    # 2. Baterai
    # PERBAIKAN: hapus 'turun' sendirian (terlalu ambigu)
    # Tambah konteks: pastikan tidak dalam kalimat sinyal
    # ----------------------------------------------------------------
    has_baterai_kw = _match_negative(t, ['baterai', 'kembung', 'drop', 'boros',
                                 'mentok 0%'])
    # 'turun' hanya valid jika ada kata baterai/daya/% di sekitarnya
    has_turun_battery = (
        _match(t, ['turun']) and is_battery_ctx and not is_signal_ctx
    )

    if has_baterai_kw or has_turun_battery:
        baterai = 'Daya Tahan Rendah/Gembung'
    else:
        baterai = 'Normal'

    # ----------------------------------------------------------------
    # 3. LCD
    # PERBAIKAN: 'pecah' dalam konteks speaker/audio TIDAK memicu LCD
    # ----------------------------------------------------------------
    has_lcd_kw = _match(t, ['greenscreen', 'greenline', 'hijau'])

    # 'pecah' di sini hanya valid jika bukan konteks speaker/audio/backdoor
    has_blank_kw = _match(t, ['blank', 'blackscreen', 'gelap', 'retak', 'garis'])
    
    # Jika layar mati/tidak tampil tetapi mesin getar saat cas, tandanya LCD-nya rusak/gelap
    has_lcd_dead_vibrating = has_screen_dead_kw and has_vibe_on_charge
    
    has_blank_valid = (has_blank_kw or has_lcd_dead_vibrating) and not is_backdoor_ctx and not is_housing_ctx

    has_pecah_lcd = (
        _match(t, ['pecah'])
        and not is_speaker_ctx    # 'speaker pecah' bukan LCD
        and not is_mic_ctx
        and not is_backdoor_ctx
        and not is_housing_ctx
    )

    if has_lcd_kw:
        lcd = 'Greenscreen'
    elif has_blank_valid or has_pecah_lcd:
        lcd = 'Gelap'
    else:
        lcd = 'Normal'

    # ----------------------------------------------------------------
    # 4. Wifi
    # ----------------------------------------------------------------
    if _match_negative(t, ['wifi']):
        wifi = 'Hilang Timbul'
    else:
        wifi = 'Normal'

    # ----------------------------------------------------------------
    # 5. Touchscreen
    # ----------------------------------------------------------------
    if _match_negative(t, ['disentuh', 'sentuh', 'touchscreen', 'ghostouch', 'ngefreeze']):
        touch = 'Tidak bisa disentuh'
    else:
        touch = 'Normal'

    # ----------------------------------------------------------------
    # 6. Tegangan
    # ----------------------------------------------------------------
    if has_vibe_on_charge:
        tegangan = '0,8 - 2,2'
    elif _match(t, ['korsleting', 'mati total', 'korosi',
                  'basah', 'kena air', 'masuk air']):
        if _match(t, ['tombol', 'kamera', 'speaker', 'wifi']):
            tegangan = '0,8 - 2,2'
        else:
            tegangan = '0,0'
    elif _match(t, ['mati']) and not is_speaker_ctx and not is_signal_ctx and not is_mic_ctx:
        # 'mati' sendirian (bukan konteks speaker/sinyal/mikrofon) → tegangan rendah
        if _match(t, ['tombol', 'kamera', 'speaker', 'wifi']):
            tegangan = '0,8 - 2,2'
        else:
            tegangan = '0,0'
    elif _match(t, ['tegangan rendah', 'vcc main', 'baterai drop']):
        tegangan = '0,6'
    else:
        tegangan = '0,8 - 2,2'

    # ----------------------------------------------------------------
    # 7. Kamera & Senter
    # ----------------------------------------------------------------
    if _match_negative(t, ['kamera', 'foto', 'buram', 'jamur', 'getar', 'flash', 'senter', 'flashlight']):
        # 'getar' hanya jika bukan konteks mikrofon/telepon
        if _match(t, ['getar']) and not _match(t, ['kamera', 'foto', 'buram', 'jamur', 'flash', 'senter', 'flashlight']):
            kamera = 'Normal'
        else:
            kamera = 'Blank'
    else:
        kamera = 'Normal'

    # ----------------------------------------------------------------
    # 8. Konektor Cas
    # ----------------------------------------------------------------
    if has_vibe_on_charge:
        konektor = 'Normal'
    elif _match_negative(t, ['tidak bisa dicas', 'dicas mati', 'dicas tidak naik',
                  'dicas keluar masuk', 'konektor cas', 'dicas', 'cas', 'konektor']):
        if _match(t, ['keluar masuk', 'longgar', 'kotor']):
            konektor = 'Keluar masuk'
        else:
            konektor = 'Tidak Ngecas'
    else:
        konektor = 'Normal'

    # ----------------------------------------------------------------
    # 9. Speaker
    # PERBAIKAN: pisahkan dari mikrofon.
    # Speaker = keluhan keluaran suara (speaker, earpiece, dering)
    # Mikrofon = keluhan penerimaan suara (mikrofon, rekam, suara masuk)
    # ----------------------------------------------------------------
    speaker_keywords = [
        'speaker', 'buzzer', 'dering', 'berdering',
        'bunyi', 'berbunyi', 'nada dering', 'nada',
        'audio', 'earpiece', 'suara keluar',
    ]
    has_speaker_kw = _match_negative(t, speaker_keywords)
    # 'suara' saja valid untuk speaker HANYA jika tidak dalam konteks mikrofon
    # Jika ada 'tidak dengar'/'pihak lain' dll, konteks adalah mikrofon
    has_suara_general = _match_negative(t, ['suara']) and not is_mic_ctx
    # 'pecah' speaker: suara pecah (bukan LCD pecah)
    has_pecah_speaker = (
        _match_negative(t, ['pecah'])
        and _match_negative(t, ['suara', 'speaker', 'buzzer', 'audio'])
        and not is_mic_ctx
    )
    # Kata telepon/telfon HANYA jika tidak ada konteks mikrofon
    has_telepon_kw = (
        _match_negative(t, ['ditelpon', 'ditelepon', 'telfon tidak', 'telfon ga'])
        and not is_mic_ctx
    )

    if has_speaker_kw or has_suara_general or has_pecah_speaker or has_telepon_kw:
        speaker = 'Rusak'
    else:
        speaker = 'Normal'

    # ----------------------------------------------------------------
    # 10. Mikrofon (BARU - Kolom Terpisah)
    # Mikrofon = pihak lain tidak dengar, rekam suara, mic mati
    # ----------------------------------------------------------------
    mikrofon_keywords = [
        'mikrofon', 'microphone', 'mic',
        'rekam suara', 'merekam', 'recording',
        'tidak terdengar', 'suara tidak terdengar',
        'tidak dengar', 'orang tidak dengar',
        'tidak kedengaran', 'suara tidak kedengaran',
        'pihak lain tidak dengar', 'orang lain tidak dengar',
        'suara tidak masuk', 'suara putus',
        'telepon tidak terdengar',
    ]
    if _match_negative(t, mikrofon_keywords):
        mikrofon = 'Tidak Berfungsi'
    else:
        mikrofon = 'Normal'

    # ----------------------------------------------------------------
    # 11. Backdoor
    # ----------------------------------------------------------------
    if is_backdoor_ctx:
        backdoor = 'Pecah/Retak'
    else:
        backdoor = 'Normal'

    # ----------------------------------------------------------------
    # 11b. Housing
    # ----------------------------------------------------------------
    if is_housing_ctx:
        housing = 'Pecah/Retak/Bengkok'
    else:
        housing = 'Normal'

    # ----------------------------------------------------------------
    # 12. Tombol
    # ----------------------------------------------------------------
    if _match_negative(t, ['tombol', 'power', 'volume', 'haptic', 'haptik',
                  'switch', 'silent', 'home', 'on/off']):
        tombol = 'Tidak Berfungsi'
    else:
        tombol = 'Normal'

    return {
        'Signal':       signal,
        'Baterai':      baterai,
        'LCD':          lcd,
        'Wifi':         wifi,
        'Touchscreen':  touch,
        'Tegangan':     tegangan,
        'Kamera':       kamera,
        'Konektor Cas': konektor,
        'Speaker':      speaker,
        'Mikrofon':     mikrofon,
        'Backdoor':     backdoor,
        'Housing':      housing,
        'Tombol':       tombol,
    }
