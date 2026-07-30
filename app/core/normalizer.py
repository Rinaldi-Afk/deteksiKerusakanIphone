import re

# Kamus normalisasi slang/typo bahasa Indonesia ke kata baku
# (Disalin dari preprocessing.ipynb — TIDAK memodifikasi notebook)
SLANG_MAP = {
    r'\bbatrai\b': 'baterai',
    r'\bbatre\b': 'baterai',
    r'\bbatrey\b': 'baterai',
    r'\bbattery\b': 'baterai',
    r'\bbatarai\b': 'baterai',
    r'\bgembung\b': 'kembung',
    r'\blembung\b': 'kembung',
    r'\bgakbisa\b': 'tidak bisa',
    r'\bgkbisa\b': 'tidak bisa',
    r'\bgabisa\b': 'tidak bisa',
    r'\bgak bisa\b': 'tidak bisa',
    r'\bgk bisa\b': 'tidak bisa',
    r'\bga bisa\b': 'tidak bisa',
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
}


def normalize_text(text: str) -> str:
    """
    Normalisasi teks keluhan: lowercase, hapus slang/typo,
    bersihkan spasi berlebih.
    """
    text = str(text).lower().strip()
    for pattern, replacement in SLANG_MAP.items():
        text = re.sub(pattern, replacement, text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
