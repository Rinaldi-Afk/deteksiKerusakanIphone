import re
from indoNLP.preprocessing import replace_slang, replace_word_elongation, remove_html, remove_url

# Pemetaan istilah teknis khusus perbaikan iPhone
# (Dijalankan setelah indoNLP membersihkan slang & typo umum bahasa Indonesia)
IPHONE_TECHNICAL_MAP = {
    r'\bbatrai\b': 'baterai',
    r'\bbatre\b': 'baterai',
    r'\bbatrey\b': 'baterai',
    r'\bbattery\b': 'baterai',
    r'\bbatarai\b': 'baterai',
    r'\bngedrop\b': 'drop',
    r'\bgembung\b': 'kembung',
    r'\blembung\b': 'kembung',
    r'\bkoncas\b': 'konektor cas',
    r'\bkon cas\b': 'konektor cas',
    r'\blubang cas\b': 'konektor cas',
    r'\bport cas\b': 'konektor cas',
    r'\bport charger\b': 'konektor cas',
    r'\bmatot\b': 'mati total',
    r'\bshort\b': 'korsleting',
    r'\bkonslet\b': 'korsleting',
    r'\bblkg\b': 'belakang',
    r'\bdicharge\b': 'dicas',
    r'\bdi charge\b': 'dicas',
    r'\bflexible\b': 'fleksibel',
    r'\bfleksi\b': 'fleksibel',
    r'\bflexy\b': 'fleksibel',
    r'\bflexyble\b': 'fleksibel',
    r'\bfelxyble\b': 'fleksibel',
    r'\bts\b': 'touchscreen',
    r'\blayar\b': 'lcd',
    r'\bscreen\b': 'lcd',
    r'\bcamera\b': 'kamera',
    r'\bbackdor\b': 'backdoor',
    r'\bbckdor\b': 'backdoor',
    r'\bback glass\b': 'backdoor',
    r'\bbackglass\b': 'backdoor',
    r'\bkaca belakang\b': 'backdoor',
    r'\bpunggung\b': 'backdoor',
    r'\bon off\b': 'on/off',
    r'\bonoff\b': 'on/off',
    r'\bbutton\b': 'tombol',
    r'\bbtn\b': 'tombol',
    r'\bcharge\b': 'cas',
    r'\bcharger\b': 'cas',
    r'\bathena\b': 'antena',
    # Kartu SIM & Sinyal
    r'\bsim\b': 'sim',
    r'\bsimcard\b': 'sim card',
    r'\bsim card\b': 'sim card',
    r'\bkartu sim\b': 'kartu sim',
    r'\bkartu simnya\b': 'kartu simnya',
    r'\bnelpon\b': 'telepon',
    r'\bnelp\b': 'telepon',
    r'\btelp\b': 'telepon',
    r'\bsinyalnya\b': 'sinyal',
    r'\bsignalnya\b': 'sinyal',
    r'\bjaringannya\b': 'jaringan',
    r'\bno signal\b': 'no signal',
    r'\bno service\b': 'no service',
}


def normalize_text(text: str) -> str:
    """
    IndoNLP Hybrid Normalizer:
    1. Membersihkan HTML, URL, & spasi luar.
    2. Menghapus pemanjangan karakter berulang (misal: "matiiii" -> "mati").
    3. Mengubah slang/informal Indonesia umum via indoNLP (misal: "bgt" -> "banget", "gk" -> "enggak").
    4. Memetakan istilah teknis spesifik perbaikan iPhone.
    5. Menghapus spasi berlebih.
    """
    if not text:
        return ""

    t = str(text).lower().strip()
    t = remove_url(remove_html(t))
    # Hapus huruf berulang berlebih (>2 huruf berturut-turut)
    t = re.sub(r'(.)\1{2,}', r'\1', t)
    t = replace_word_elongation(t)
    t = replace_slang(t)

    # Pemetaan domain teknis iPhone
    for pattern, replacement in IPHONE_TECHNICAL_MAP.items():
        t = re.sub(pattern, replacement, t)

    t = re.sub(r'\s+', ' ', t).strip()
    return t

