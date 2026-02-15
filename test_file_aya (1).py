#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Quran Phonetic Script (QPS) - Generic Tajweed Rules Implementation
A fully generic system that extracts and applies ALL Tajweed rules to ANY Quranic text
"""

from typing import List, Tuple, Dict, Optional, Any, Union
import re
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

# ==================== ENUMS AND CONSTANTS ====================

class TajweedRuleCategory(Enum):
    """Major categories of Tajweed rules"""
    NOON_SAKINAH = "noon_sakinah"
    MEEM_SAKINAH = "meem_sakinah"
    LAM_DEFINITE = "lam_definite"
    MADD = "madd"
    QALQALAH = "qalqalah"
    TAFKHIM = "tafkhim"
    TARQEEQ = "tarqeeq"
    STOPPING = "waqf"
    STARTING = "ibtida"
    SILENT = "sakt"
    GUNNAH = "ghunnah"
    IDGHAM = "idgham"
    IKHFAA = "ikhfa"
    IQLAB = "iqlab"
    IZHAAR = "izhaar"
    HAMS = "hams"
    JAHR = "jahr"
    SHIDDAH = "shiddah"
    RIKHWAH = "rikhwah"
    ISTILA = "istila"
    ISTIFAL = "istifal"
    ITBAQ = "itbaq"
    INFITAH = "infitah"
    SAFEER = "safeer"
    TAKREER = "takreer"
    INHIRAF = "inhiraf"


class QuranicPhoneme(Enum):
    """Complete set of Quranic phonemes with their IPA equivalents"""
    # Consonants
    HAMZA = "ʔ"          # ء
    ALIF = "ʔ"           # ا
    BA = "b"             # ب
    TA = "t"             # ت
    THA = "θ"            # ث
    JEEM = "dʒ"          # ج
    HA = "ħ"             # ح
    KHA = "x"            # خ
    DAL = "d"            # د
    DHAL = "ð"           # ذ
    RA = "r"             # ر
    ZAY = "z"            # ز
    SEEN = "s"           # س
    SHEEN = "ʃ"          # ش
    SAD = "sˤ"           # ص
    DAD = "dˤ"           # ض
    TA_EMPHATIC = "tˤ"   # ط
    ZA_EMPHATIC = "ðˤ"   # ظ
    AYN = "ʕ"            # ع
    GHAYN = "ɣ"          # غ
    FA = "f"             # ف
    QAF = "q"            # ق
    KAF = "k"            # ك
    LAAM = "l"           # ل
    MEEM = "m"           # م
    NUN = "n"            # ن
    HA_HEAVY = "h"       # ه
    WAW = "w"            # و
    YA = "j"             # ي
    
    # Vowels
    FATHA = "a"          # َ
    KASRA = "i"          # ِ
    DAMMA = "u"          # ُ
    ALIF_MADD = "ā"      # ا
    WAW_MADD = "ū"       # و
    YA_MADD = "ī"        # ي
    
    # Special markers
    SUKUN = ""           # ْ
    SHADDA = "ː"         # ّ
    TANWEEN_FATH = "an"  # ً
    TANWEEN_KASR = "in"  # ٍ
    TANWEEN_DAMM = "un"  # ٌ
    MADD_SIGN = "~"      # ~
    SPACE = " "          # space


class SifaAttributes(Enum):
    """Complete set of Sifa (articulation attributes) as per Tajweed"""
    # Voice-related
    HAMS = "H"           # Whisper
    JAHR = "J"           # Voice
    
    # Airflow-related
    RIKHWA = "R"         # Softness
    SHAFWI = "F"         # Labial
    SHIDDAH = "S"        # Strength
    TAWASSUT = "T"       # Moderate
    
    # Nasalization
    GUNNAH = "G"         # Nasalization
    
    # Articulation quality
    ISTILA = "I"         # Elevation
    ISTIFAL = "L"        # Lowering
    ITBAQ = "B"          # Adhesion
    INFITAH = "O"        # Opening
    
    # Special effects
    QALQALAH = "C"       # Echo/bounce
    INHIRAF = "Y"        # Deviation
    TAKREER = "R"        # Repetition
    TAFKHIM = "M"        # Heavy articulation
    TARQEEQ = "Q"        # Light articulation
    SAFEER = "Sf"        # Whistling
    
    # Duration markers
    DUR_2 = "2"          # 2 counts
    DUR_4 = "4"          # 4 counts
    DUR_5 = "5"          # 5 counts
    DUR_6 = "6"          # 6 counts
    
    # Rule markers
    IDGHAM = "D"         # Assimilation
    IKHFAA = "K"         # Concealment
    IQLAB = "B"          # Conversion
    IZHAAR = "Z"         # Clarity


# ==================== DATA CLASSES ====================

@dataclass
class TajweedRule:
    """Represents a single Tajweed rule with its conditions and effects"""
    name: str
    category: TajweedRuleCategory
    pattern: str
    sifa_output: str
    duration: int = 1
    description: str = ""
    condition_func: Optional[callable] = None
    
    def matches(self, text: str, position: int, context: Dict[str, Any]) -> bool:
        """Check if rule matches at given position"""
        if self.condition_func:
            return self.condition_func(text, position, context)
        
        # Check pattern
        if self.pattern:
            pattern = re.compile(self.pattern)
            return bool(pattern.match(text[position:]))
        
        return False


@dataclass
class PhonemeMapping:
    """Mapping from Arabic character to phoneme"""
    arabic_char: str
    phoneme: str
    category: str
    sifa_default: List[str] = field(default_factory=list)


@dataclass
class RuleApplication:
    """Record of a rule application"""
    rule_name: str
    category: str
    position: int
    arabic_char: str
    phoneme_before: str
    phoneme_after: str
    sifa_applied: str
    duration: int
    context: Dict[str, Any]


@dataclass
class QPSResult:
    """Complete QPS processing result"""
    original_text: str
    normalized_text: str
    phoneme_sequence: List[str]
    sifa_sequence: List[str]
    duration_sequence: List[int]
    rule_applications: List[RuleApplication]
    word_boundaries: List[int]
    metadata: Dict[str, Any]
    
    def get_phoneme_string(self) -> str:
        return ''.join(self.phoneme_sequence)
    
    def get_sifa_string(self) -> str:
        return ' '.join(self.sifa_sequence)
    
    def get_detailed_breakdown(self) -> List[Dict]:
        breakdown = []
        pos = 0
        for i, (phoneme, sifa, duration) in enumerate(zip(
            self.phoneme_sequence, self.sifa_sequence, self.duration_sequence
        )):
            rules_here = [r.rule_name for r in self.rule_applications if r.position == i]
            breakdown.append({
                'position': pos,
                'arabic': self.normalized_text[i] if i < len(self.normalized_text) else '',
                'phoneme': phoneme,
                'sifa': sifa if sifa else 'None',
                'duration': duration,
                'rules': rules_here
            })
            pos += duration
        return breakdown


# ==================== MAIN GENERIC CLASS ====================

class GenericQuranPhoneticScript:
    """
    A completely generic system for applying ALL Tajweed rules to ANY Quranic text
    """
    
    def __init__(self, qiraat: str = "hafs"):
        self.qiraat = qiraat
        self._init_phoneme_mappings()
        self._init_sifa_matrix()
        self._init_tajweed_rules()
        self._init_letter_properties()
        self._init_rule_dependencies()
        
    def _init_phoneme_mappings(self):
        """Initialize complete phoneme mapping system"""
        
        # Base phoneme mappings
        self.phoneme_map = {
            # Consonants
            'ء': ('ʔ', 'hamz', ['J', 'S']),
            'ا': ('ʔ', 'alif', []),
            'ب': ('b', 'ba', ['J', 'R', 'Q']),
            'ت': ('t', 'ta', ['H', 'S']),
            'ث': ('θ', 'tha', ['H', 'R']),
            'ج': ('dʒ', 'jeem', ['J', 'S', 'Q']),
            'ح': ('ħ', 'ha', ['H', 'R']),
            'خ': ('x', 'kha', ['H', 'R', 'I']),
            'د': ('d', 'dal', ['J', 'S', 'Q']),
            'ذ': ('ð', 'dhal', ['J', 'R']),
            'ر': ('r', 'ra', ['J', 'T', 'Rr']),
            'ز': ('z', 'zay', ['J', 'R']),
            'س': ('s', 'seen', ['H', 'R', 'Sf']),
            'ش': ('ʃ', 'sheen', ['H', 'R']),
            'ص': ('sˤ', 'sad', ['J', 'R', 'I', 'B', 'Sf']),
            'ض': ('dˤ', 'dad', ['J', 'R', 'I', 'B']),
            'ط': ('tˤ', 'ta', ['J', 'S', 'I', 'B', 'Q']),
            'ظ': ('ðˤ', 'za', ['J', 'R', 'I', 'B']),
            'ع': ('ʕ', 'ayn', ['J', 'T']),
            'غ': ('ɣ', 'ghayn', ['J', 'R', 'I']),
            'ف': ('f', 'fa', ['J', 'R', 'F']),
            'ق': ('q', 'qaf', ['J', 'S', 'I', 'Q']),
            'ك': ('k', 'kaf', ['H', 'S']),
            'ل': ('l', 'lam', ['J', 'R', 'Y']),
            'م': ('m', 'meem', ['J', 'R', 'F']),
            'ن': ('n', 'noon', ['J', 'T', 'Y']),
            'ه': ('h', 'ha', ['H', 'R']),
            'و': ('w', 'waw', ['J', 'R']),
            'ي': ('j', 'ya', ['J', 'R']),
            
            # Vowel marks
            'َ': ('a', 'fatha', []),
            'ِ': ('i', 'kasra', []),
            'ُ': ('u', 'damma', []),
            
            # Tanween
            'ً': ('an', 'tanween_fath', ['G']),
            'ٍ': ('in', 'tanween_kasr', ['G']),
            'ٌ': ('un', 'tanween_damm', ['G']),
            
            # Sukun and Shadda
            'ْ': ('', 'sukun', []),
            'ّ': ('ː', 'shadda', []),
            
            # Special Alif forms
            'إ': ('ʔi', 'alif_with_kasra', []),
            'أ': ('ʔa', 'alif_with_fatha', []),
            'آ': ('ʔā', 'alif_madd', ['M']),
            'ٱ': ('ʔ', 'alif_wasl', []),
            'ٰ': ('ā', 'alif_khanjariya', ['M']),
        }
        
        # Reverse mapping for lookups
        self.reverse_phoneme_map = {}
        for k, v in self.phoneme_map.items():
            self.reverse_phoneme_map[k] = {'phoneme': v[0], 'name': v[1], 'sifa': v[2]}
    
    def _init_sifa_matrix(self):
        """Initialize the complete Sifa attributes matrix"""
        self.sifa_matrix = {
            # Format: [Hams/Jahr, Shiddah/Rikhwa/Tawassut, Isti'la/Istifal, Itbaq/Infitah, Special]
            'ء': ['J', 'S', 'L', 'O', ''],
            'ب': ['J', 'R', 'L', 'O', 'Qalqalah,Shafawi'],
            'ت': ['H', 'S', 'L', 'O', ''],
            'ث': ['H', 'R', 'L', 'O', ''],
            'ج': ['J', 'S', 'L', 'O', 'Qalqalah'],
            'ح': ['H', 'R', 'L', 'O', ''],
            'خ': ['H', 'R', 'I', 'O', ''],
            'د': ['J', 'S', 'L', 'O', 'Qalqalah'],
            'ذ': ['J', 'R', 'L', 'O', ''],
            'ر': ['J', 'T', 'L', 'O', 'Takreer,Inhiraf'],
            'ز': ['J', 'R', 'L', 'O', 'Safeer'],
            'س': ['H', 'R', 'L', 'O', 'Safeer'],
            'ش': ['H', 'R', 'L', 'O', ''],
            'ص': ['J', 'R', 'I', 'B', 'Safeer'],
            'ض': ['J', 'R', 'I', 'B', ''],
            'ط': ['J', 'S', 'I', 'B', 'Qalqalah'],
            'ظ': ['J', 'R', 'I', 'B', ''],
            'ع': ['J', 'T', 'L', 'O', ''],
            'غ': ['J', 'R', 'I', 'O', ''],
            'ف': ['J', 'R', 'L', 'O', 'Shafawi'],
            'ق': ['J', 'S', 'I', 'O', 'Qalqalah'],
            'ك': ['H', 'S', 'L', 'O', ''],
            'ل': ['J', 'R', 'L', 'O', 'Inhiraf'],
            'م': ['J', 'R', 'L', 'O', 'Shafawi,Ghunnah'],
            'ن': ['J', 'T', 'L', 'O', 'Inhiraf,Ghunnah'],
            'ه': ['H', 'R', 'L', 'O', ''],
            'و': ['J', 'R', 'L', 'O', 'Ghunnah'],
            'ي': ['J', 'R', 'L', 'O', ''],
        }
    
    def _init_letter_properties(self):
        """Initialize various letter groupings for rule application"""
        
        # Throat letters (for Izhaar)
        self.throat_letters = 'ءهعحغخ'
        
        # Letters for Idgham with Ghunnah
        self.idgham_bi_ghunnah = 'يومون'
        
        # Letters for Idgham without Ghunnah
        self.idgham_bila_ghunnah = 'رل'
        
        # Iqlab letter
        self.iqlab_letter = 'ب'
        
        # Ikhfaa letters
        self.ikhfaa_letters = 'صضطظسشثدذز'
        
        # Qalqalah letters
        self.qalqalah_letters = 'قطبد'
        
        # Always heavy letters
        self.always_heavy = 'خصضغظقط'
        
        # Shamsi letters (Sun letters)
        self.shamsi_letters = 'تثدذرزسشصضطظلن'
        
        # Qamari letters (Moon letters)
        self.qamari_letters = 'ءبغحجفكوهي'
        
        # Madd letters
        self.madd_letters = {'ا': 'ā', 'و': 'ū', 'ي': 'ī'}
        
        # Ghunnah letters
        self.ghunnah_letters = 'نوم'
        
        # Shafawi letters
        self.shafawi_letters = 'فمب'
        
        # Safeer letters (whistling)
        self.safeer_letters = 'صسز'
        
        # Takreer letter
        self.takreer_letter = 'ر'
        
        # Inhiraf letters
        self.inhiraf_letters = 'لر'
        
        # Hams letters
        self.hams_letters = 'فحثهسشكخت'
        
        # Jahr letters (opposite of Hams)
        self.jahr_letters = 'ءبجدذرزصضطظعغقلمنوهي'
    
    def _init_tajweed_rules(self):
        """Initialize all Tajweed rules with conditions and effects"""
        self.tajweed_rules = []
        
        # ========== 1. NOON SAKINAH AND TANWEEN RULES ==========
        
        def izhaar_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 1 >= len(text):
                return False
            current = text[pos]
            next_char = text[pos + 1]
            return (current in ['ن', 'ً', 'ٍ', 'ٌ'] and 
                    pos + 1 < len(text) and text[pos + 1] in self.throat_letters)
        
        self.tajweed_rules.append(TajweedRule(
            name="izhaar_halqi",
            category=TajweedRuleCategory.IZHAAR,
            pattern="",
            sifa_output=SifaAttributes.IZHAAR.value,
            duration=1,
            description="Clear pronunciation of noon sakinah/tanween before throat letters",
            condition_func=izhaar_condition
        ))
        
        def idgham_bi_ghunnah_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 1 >= len(text):
                return False
            current = text[pos]
            next_char = text[pos + 1]
            return (current in ['ن', 'ً', 'ٍ', 'ٌ'] and 
                    next_char in self.idgham_bi_ghunnah)
        
        self.tajweed_rules.append(TajweedRule(
            name="idgham_bi_ghunnah",
            category=TajweedRuleCategory.IDGHAM,
            pattern="",
            sifa_output=SifaAttributes.IDGHAM.value + SifaAttributes.GUNNAH.value,
            duration=2,
            description="Merging with nasalization",
            condition_func=idgham_bi_ghunnah_condition
        ))
        
        def idgham_bila_ghunnah_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 1 >= len(text):
                return False
            current = text[pos]
            next_char = text[pos + 1]
            return (current in ['ن', 'ً', 'ٍ', 'ٌ'] and 
                    next_char in self.idgham_bila_ghunnah)
        
        self.tajweed_rules.append(TajweedRule(
            name="idgham_bila_ghunnah",
            category=TajweedRuleCategory.IDGHAM,
            pattern="",
            sifa_output=SifaAttributes.IDGHAM.value,
            duration=1,
            description="Merging without nasalization",
            condition_func=idgham_bila_ghunnah_condition
        ))
        
        def iqlab_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 1 >= len(text):
                return False
            current = text[pos]
            next_char = text[pos + 1]
            return (current in ['ن', 'ً', 'ٍ', 'ٌ'] and 
                    next_char == self.iqlab_letter)
        
        self.tajweed_rules.append(TajweedRule(
            name="iqlab",
            category=TajweedRuleCategory.IQLAB,
            pattern="",
            sifa_output=SifaAttributes.IQLAB.value + SifaAttributes.GUNNAH.value,
            duration=2,
            description="Conversion of noon to meem",
            condition_func=iqlab_condition
        ))
        
        def ikhfaa_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 1 >= len(text):
                return False
            current = text[pos]
            next_char = text[pos + 1]
            return (current in ['ن', 'ً', 'ٍ', 'ٌ'] and 
                    next_char in self.ikhfaa_letters)
        
        self.tajweed_rules.append(TajweedRule(
            name="ikhfaa",
            category=TajweedRuleCategory.IKHFAA,
            pattern="",
            sifa_output=SifaAttributes.IKHFAA.value + SifaAttributes.GUNNAH.value,
            duration=2,
            description="Concealment of noon",
            condition_func=ikhfaa_condition
        ))
        
        # ========== 2. MEEM SAKINAH RULES ==========
        
        def ikhfaa_shafawi_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 2 >= len(text):
                return False
            return (text[pos] == 'م' and 
                    pos + 1 < len(text) and text[pos + 1] == 'ْ' and
                    pos + 2 < len(text) and text[pos + 2] == 'ب')
        
        self.tajweed_rules.append(TajweedRule(
            name="ikhfaa_shafawi",
            category=TajweedRuleCategory.IKHFAA,
            pattern="",
            sifa_output=SifaAttributes.IKHFAA.value + SifaAttributes.SHAFWI.value,
            duration=2,
            description="Labial concealment",
            condition_func=ikhfaa_shafawi_condition
        ))
        
        def idgham_shafawi_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 2 >= len(text):
                return False
            return (text[pos] == 'م' and 
                    pos + 1 < len(text) and text[pos + 1] == 'ْ' and
                    pos + 2 < len(text) and text[pos + 2] == 'م')
        
        self.tajweed_rules.append(TajweedRule(
            name="idgham_shafawi",
            category=TajweedRuleCategory.IDGHAM,
            pattern="",
            sifa_output=SifaAttributes.IDGHAM.value + SifaAttributes.SHAFWI.value,
            duration=2,
            description="Labial merging",
            condition_func=idgham_shafawi_condition
        ))
        
        def izhaar_shafawi_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 2 >= len(text):
                return False
            return (text[pos] == 'م' and 
                    pos + 1 < len(text) and text[pos + 1] == 'ْ' and
                    pos + 2 < len(text) and text[pos + 2] not in ['ب', 'م'])
        
        self.tajweed_rules.append(TajweedRule(
            name="izhaar_shafawi",
            category=TajweedRuleCategory.IZHAAR,
            pattern="",
            sifa_output=SifaAttributes.IZHAAR.value + SifaAttributes.SHAFWI.value,
            duration=1,
            description="Labial clarity",
            condition_func=izhaar_shafawi_condition
        ))
        
        # ========== 3. LAM DEFINITE RULES ==========
        
        def lam_shamsiyyah_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos < 1 or pos + 2 >= len(text):
                return False
            return (text[pos - 1] == 'ا' and text[pos] == 'ل' and
                    text[pos + 2] in self.shamsi_letters)
        
        self.tajweed_rules.append(TajweedRule(
            name="lam_shamsiyyah",
            category=TajweedRuleCategory.LAM_DEFINITE,
            pattern="",
            sifa_output=SifaAttributes.IDGHAM.value,
            duration=2,
            description="Sun letters - lam is assimilated",
            condition_func=lam_shamsiyyah_condition
        ))
        
        def lam_qamariyyah_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos < 1 or pos + 2 >= len(text):
                return False
            return (text[pos - 1] == 'ا' and text[pos] == 'ل' and
                    text[pos + 2] in self.qamari_letters)
        
        self.tajweed_rules.append(TajweedRule(
            name="lam_qamariyyah",
            category=TajweedRuleCategory.LAM_DEFINITE,
            pattern="",
            sifa_output=SifaAttributes.IZHAAR.value,
            duration=1,
            description="Moon letters - lam is clear",
            condition_func=lam_qamariyyah_condition
        ))
        
        # ========== 4. MADD RULES ==========
        
        def madd_tabii_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos >= len(text):
                return False
            char = text[pos]
            if char not in self.madd_letters:
                return False
            # Check if it's a natural madd
            if pos + 1 < len(text):
                next_char = text[pos + 1]
                if next_char in ['ء', 'ْ']:
                    return False
                if pos + 2 < len(text) and text[pos + 2] == 'ّ':
                    return False
            return True
        
        self.tajweed_rules.append(TajweedRule(
            name="madd_tabii",
            category=TajweedRuleCategory.MADD,
            pattern="",
            sifa_output=SifaAttributes.DUR_2.value,
            duration=2,
            description="Natural elongation - 2 counts",
            condition_func=madd_tabii_condition
        ))
        
        def madd_wajib_muttasil_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 1 >= len(text):
                return False
            char = text[pos]
            next_char = text[pos + 1]
            return char in self.madd_letters and next_char == 'ء'
        
        self.tajweed_rules.append(TajweedRule(
            name="madd_wajib_muttasil",
            category=TajweedRuleCategory.MADD,
            pattern="",
            sifa_output=SifaAttributes.DUR_5.value,
            duration=5,
            description="Required connected madd - 4-5 counts",
            condition_func=madd_wajib_muttasil_condition
        ))
        
        def madd_jaiz_munfasil_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 2 >= len(text):
                return False
            char = text[pos]
            return (char in self.madd_letters and 
                    text[pos + 1].isspace() and 
                    text[pos + 2] == 'ء')
        
        self.tajweed_rules.append(TajweedRule(
            name="madd_jaiz_munfasil",
            category=TajweedRuleCategory.MADD,
            pattern="",
            sifa_output=SifaAttributes.DUR_4.value,
            duration=4,
            description="Permitted separate madd - 4-5 counts",
            condition_func=madd_jaiz_munfasil_condition
        ))
        
        def madd_lazim_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 2 >= len(text):
                return False
            char = text[pos]
            return (char in self.madd_letters and 
                    text[pos + 2] == 'ّ')
        
        self.tajweed_rules.append(TajweedRule(
            name="madd_lazim",
            category=TajweedRuleCategory.MADD,
            pattern="",
            sifa_output=SifaAttributes.DUR_6.value,
            duration=6,
            description="Necessary heavy madd - 6 counts",
            condition_func=madd_lazim_condition
        ))
        
        def madd_lin_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 2 >= len(text):
                return False
            char = text[pos]
            return (char in ['و', 'ي'] and 
                    pos + 1 < len(text) and text[pos + 1] == 'ْ' and
                    text[pos + 2] not in self.madd_letters)
        
        self.tajweed_rules.append(TajweedRule(
            name="madd_lin",
            category=TajweedRuleCategory.MADD,
            pattern="",
            sifa_output=SifaAttributes.DUR_4.value,
            duration=4,
            description="Lin madd - 2-4-6 counts depending on context",
            condition_func=madd_lin_condition
        ))
        
        # ========== 5. QALQALAH RULES ==========
        
        def qalqalah_kubra_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 1 >= len(text):
                return False
            char = text[pos]
            return (char in self.qalqalah_letters and 
                    pos + 1 < len(text) and text[pos + 1] == 'ْ' and
                    (pos + 2 >= len(text) or text[pos + 2].isspace()))
        
        self.tajweed_rules.append(TajweedRule(
            name="qalqalah_kubra",
            category=TajweedRuleCategory.QALQALAH,
            pattern="",
            sifa_output=SifaAttributes.QALQALAH.value + '!',
            duration=2,
            description="Major echo - at stop",
            condition_func=qalqalah_kubra_condition
        ))
        
        def qalqalah_wusta_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 2 >= len(text):
                return False
            char = text[pos]
            return (char in self.qalqalah_letters and 
                    pos + 1 < len(text) and text[pos + 1] == 'ْ' and
                    pos + 2 < len(text) and not text[pos + 2].isspace())
        
        self.tajweed_rules.append(TajweedRule(
            name="qalqalah_wusta",
            category=TajweedRuleCategory.QALQALAH,
            pattern="",
            sifa_output=SifaAttributes.QALQALAH.value,
            duration=1,
            description="Medium echo - within word",
            condition_func=qalqalah_wusta_condition
        ))
        
        # ========== 6. TAFKHIM AND TARQEEQ RULES ==========
        
        def tafkhim_daim_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos >= len(text):
                return False
            return text[pos] in self.always_heavy
        
        self.tajweed_rules.append(TajweedRule(
            name="tafkhim_daim",
            category=TajweedRuleCategory.TAFKHIM,
            pattern="",
            sifa_output=SifaAttributes.TAFKHIM.value,
            duration=1,
            description="Always heavy letters",
            condition_func=tafkhim_daim_condition
        ))
        
        def tafkhim_ra_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos >= len(text) or text[pos] != 'ر':
                return False
            
            # Check for heavy ra conditions
            if pos > 0:
                prev = text[pos - 1]
                if prev in ['َ', 'ُ']:  # Fatha or damma before
                    return True
                if prev == 'ْ' and pos > 1 and text[pos - 2] in ['َ', 'ُ']:
                    return True
            
            # Check if ra has fatha or damma
            if pos + 1 < len(text) and text[pos + 1] in ['َ', 'ُ']:
                return True
            
            return False
        
        self.tajweed_rules.append(TajweedRule(
            name="tafkhim_ra",
            category=TajweedRuleCategory.TAFKHIM,
            pattern="",
            sifa_output=SifaAttributes.TAFKHIM.value,
            duration=1,
            description="Heavy ra",
            condition_func=tafkhim_ra_condition
        ))
        
        def tarqeeq_ra_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos >= len(text) or text[pos] != 'ر':
                return False
            
            # Check for light ra conditions
            if pos > 0:
                prev = text[pos - 1]
                if prev == 'ِ':  # Kasra before
                    return True
                if prev == 'ْ' and pos > 1 and text[pos - 2] == 'ِ':
                    return True
            
            # Check if ra has kasra
            if pos + 1 < len(text) and text[pos + 1] == 'ِ':
                return True
            
            return False
        
        self.tajweed_rules.append(TajweedRule(
            name="tarqeeq_ra",
            category=TajweedRuleCategory.TARQEEQ,
            pattern="",
            sifa_output=SifaAttributes.TARQEEQ.value,
            duration=1,
            description="Light ra",
            condition_func=tarqeeq_ra_condition
        ))
        
        def tafkhim_lam_allah_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 2 >= len(text) or text[pos] != 'ل':
                return False
            # Check for Allah word
            return (text[pos:pos+3] in ['لَّه', 'لَٰه', 'لَّه'])
        
        self.tajweed_rules.append(TajweedRule(
            name="tafkhim_lam_allah",
            category=TajweedRuleCategory.TAFKHIM,
            pattern="",
            sifa_output=SifaAttributes.TAFKHIM.value,
            duration=1,
            description="Heavy lam in Allah",
            condition_func=tafkhim_lam_allah_condition
        ))
        
        # ========== 7. GHUNNAH RULES ==========
        
        def ghunnah_mushaddad_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos + 1 >= len(text):
                return False
            return (text[pos] in self.ghunnah_letters and 
                    text[pos + 1] == 'ّ')
        
        self.tajweed_rules.append(TajweedRule(
            name="ghunnah_mushaddad",
            category=TajweedRuleCategory.GUNNAH,
            pattern="",
            sifa_output=SifaAttributes.GUNNAH.value + 'ː',
            duration=3,
            description="Nasalization with shadda",
            condition_func=ghunnah_mushaddad_condition
        ))
        
        # ========== 8. ADDITIONAL SIFA RULES ==========
        
        def hams_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos >= len(text):
                return False
            return text[pos] in self.hams_letters
        
        self.tajweed_rules.append(TajweedRule(
            name="hams",
            category=TajweedRuleCategory.HAMS,
            pattern="",
            sifa_output=SifaAttributes.HAMS.value,
            duration=1,
            description="Whispered articulation",
            condition_func=hams_condition
        ))
        
        def jahr_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos >= len(text):
                return False
            return text[pos] in self.jahr_letters
        
        self.tajweed_rules.append(TajweedRule(
            name="jahr",
            category=TajweedRuleCategory.JAHR,
            pattern="",
            sifa_output=SifaAttributes.JAHR.value,
            duration=1,
            description="Voiced articulation",
            condition_func=jahr_condition
        ))
        
        def safeer_condition(text: str, pos: int, ctx: Dict) -> bool:
            if pos >= len(text):
                return False
            return text[pos] in self.safeer_letters
        
        self.tajweed_rules.append(TajweedRule(
            name="safeer",
            category=TajweedRuleCategory.SAFEER,
            pattern="",
            sifa_output=SifaAttributes.SAFEER.value,
            duration=1,
            description="Whistling sound",
            condition_func=safeer_condition
        ))
    
    def _init_rule_dependencies(self):
        """Initialize rule dependencies and conflict resolution"""
        self.rule_priority = {
            # Higher number = higher priority
            TajweedRuleCategory.MADD: 100,
            TajweedRuleCategory.NOON_SAKINAH: 90,
            TajweedRuleCategory.MEEM_SAKINAH: 90,
            TajweedRuleCategory.IQLAB: 85,
            TajweedRuleCategory.IDGHAM: 80,
            TajweedRuleCategory.IKHFAA: 75,
            TajweedRuleCategory.IZHAAR: 70,
            TajweedRuleCategory.QALQALAH: 60,
            TajweedRuleCategory.GUNNAH: 50,
            TajweedRuleCategory.TAFKHIM: 40,
            TajweedRuleCategory.TARQEEQ: 40,
            TajweedRuleCategory.LAM_DEFINITE: 30,
            TajweedRuleCategory.HAMS: 20,
            TajweedRuleCategory.JAHR: 20,
        }
        
        self.rule_conflicts = {
            'idgham_bi_ghunnah': ['izhaar_halqi', 'ikhfaa'],
            'idgham_bila_ghunnah': ['izhaar_halqi', 'ikhfaa'],
            'iqlab': ['izhaar_halqi', 'ikhfaa', 'idgham'],
            'ikhfaa': ['izhaar_halqi', 'idgham'],
        }
    
    def normalize_arabic(self, text: str) -> str:
        """Normalize Arabic text for consistent processing"""
        # Remove tatweel (kashida)
        text = re.sub(r'[ـ]', '', text)
        
        # Normalize alif variants
        text = re.sub(r'[إأٱآ]', 'ا', text)
        
        # Normalize ta marbuta
        text = re.sub(r'ة', 'ه', text)
        
        return text
    
    def get_letter_context(self, text: str, pos: int, window: int = 3) -> Dict[str, Any]:
        """Get contextual information around a position"""
        context = {
            'current': text[pos] if pos < len(text) else '',
            'prev': text[pos - 1] if pos > 0 else '',
            'next': text[pos + 1] if pos + 1 < len(text) else '',
            'prev_prev': text[pos - 2] if pos > 1 else '',
            'next_next': text[pos + 2] if pos + 2 < len(text) else '',
            'is_word_start': pos == 0 or text[pos - 1].isspace(),
            'is_word_end': pos == len(text) - 1 or (pos + 1 < len(text) and text[pos + 1].isspace()),
            'is_verse_end': pos == len(text) - 1,
            'has_sukun': pos + 1 < len(text) and text[pos + 1] == 'ْ',
            'has_shadda': pos + 1 < len(text) and text[pos + 1] == 'ّ',
            'vowel': '',
        }
        
        # Determine vowel
        if pos + 1 < len(text):
            if text[pos + 1] in ['َ', 'ِ', 'ُ']:
                context['vowel'] = text[pos + 1]
        
        return context
    
    def apply_rules_at_position(self, text: str, pos: int, 
                                 current_phoneme: str,
                                 context: Dict[str, Any]) -> Tuple[str, List[RuleApplication]]:
        """
        Apply all relevant Tajweed rules at a given position
        Returns: (modified_phoneme, list of rule applications)
        """
        applications = []
        modified_phoneme = current_phoneme
        
        # Collect all matching rules
        matching_rules = []
        for rule in self.tajweed_rules:
            if rule.matches(text, pos, context):
                matching_rules.append(rule)
        
        # Sort by priority
        matching_rules.sort(
            key=lambda r: self.rule_priority.get(r.category, 0),
            reverse=True
        )
        
        # Apply rules (highest priority first)
        applied_categories = set()
        for rule in matching_rules:
            # Check for conflicts
            if rule.name in self.rule_conflicts:
                conflict_rules = self.rule_conflicts[rule.name]
                if any(c in [r.name for r in applications] for c in conflict_rules):
                    continue
            
            # Apply if not same category already applied
            if rule.category not in applied_categories:
                # Create rule application record
                application = RuleApplication(
                    rule_name=rule.name,
                    category=rule.category.value,
                    position=pos,
                    arabic_char=text[pos],
                    phoneme_before=modified_phoneme,
                    phoneme_after=modified_phoneme,  # Will update based on rule
                    sifa_applied=rule.sifa_output,
                    duration=rule.duration,
                    context=context
                )
                
                # Modify phoneme based on rule
                if rule.category == TajweedRuleCategory.IQLAB:
                    modified_phoneme = 'm'
                elif rule.category == TajweedRuleCategory.IDGHAM:
                    if rule.name == 'idgham_bi_ghunnah':
                        modified_phoneme = ''  # Assimilated
                
                application.phoneme_after = modified_phoneme
                applications.append(application)
                applied_categories.add(rule.category)
        
        return modified_phoneme, applications
    
    def process_text(self, arabic_text: str) -> QPSResult:
        """
        Process any Arabic text and extract ALL Tajweed rules
        This is the main generic function
        """
        # Normalize text
        normalized = self.normalize_arabic(arabic_text)
        
        # Initialize result components
        phoneme_sequence = []
        sifa_sequence = []
        duration_sequence = []
        rule_applications = []
        word_boundaries = []
        
        # Track position
        i = 0
        position = 0
        
        # Find word boundaries
        for j, char in enumerate(normalized):
            if char.isspace():
                word_boundaries.append(j)
        
        # Process each character
        while i < len(arabic_text):
            char = arabic_text[i]
            
            # Get context
            context = self.get_letter_context(arabic_text, i)
            
            # Handle spaces
            if char.isspace():
                phoneme_sequence.append(' ')
                sifa_sequence.append(' ')
                duration_sequence.append(1)
                i += 1
                position += 1
                continue
            
            # Get base phoneme
            if char in self.reverse_phoneme_map:
                base_phoneme = self.reverse_phoneme_map[char]['phoneme']
                base_sifa = self.reverse_phoneme_map[char]['sifa']
            else:
                base_phoneme = char
                base_sifa = []
            
            # Apply Tajweed rules
            modified_phoneme, applications = self.apply_rules_at_position(
                arabic_text, i, base_phoneme, context
            )
            
            # Collect sifa attributes
            sifa_attrs = []
            
            # Add base sifa
            sifa_attrs.extend(base_sifa)
            
            # Add rule sifa
            for app in applications:
                sifa_attrs.append(app.sifa_applied)
                rule_applications.append(app)
            
            # Add to sequences
            phoneme_sequence.append(modified_phoneme)
            
            # Combine sifa attributes
            if sifa_attrs:
                sifa_sequence.append(''.join(set(sifa_attrs)))  # Remove duplicates
            else:
                sifa_sequence.append('_')
            
            # Duration
            max_duration = max([app.duration for app in applications]) if applications else 1
            duration_sequence.append(max_duration)
            
            i += 1
            position += max_duration
        
        # Create result object
        result = QPSResult(
            original_text=arabic_text,
            normalized_text=normalized,
            phoneme_sequence=phoneme_sequence,
            sifa_sequence=sifa_sequence,
            duration_sequence=duration_sequence,
            rule_applications=rule_applications,
            word_boundaries=word_boundaries,
            metadata={
                'qiraat': self.qiraat,
                'char_count': len(arabic_text),
                'rule_count': len(rule_applications),
                'unique_rules': len(set([r.rule_name for r in rule_applications]))
            }
        )
        
        return result
    
    def extract_rules_only(self, arabic_text: str) -> Dict[str, Any]:
        """
        Extract only the Tajweed rules without full phonetic conversion
        Useful for rule analysis and learning
        """
        result = self.process_text(arabic_text)
        
        # Organize rules by category
        rules_by_category = defaultdict(list)
        for app in result.rule_applications:
            rules_by_category[app.category].append({
                'rule': app.rule_name,
                'position': app.position,
                'arabic_char': app.arabic_char,
                'context': app.context
            })
        
        # Get unique rules
        unique_rules = set([app.rule_name for app in result.rule_applications])
        
        # Create summary
        summary = {
            'text': arabic_text,
            'total_rules_found': len(result.rule_applications),
            'unique_rules': list(unique_rules),
            'rules_by_category': dict(rules_by_category),
            'rule_applications': [
                {
                    'rule': app.rule_name,
                    'category': app.category,
                    'position': app.position,
                    'char': app.arabic_char,
                    'sifa': app.sifa_applied,
                    'duration': app.duration
                }
                for app in result.rule_applications
            ]
        }
        
        return summary
    
    def format_rule_extraction(self, arabic_text: str, detailed: bool = False) -> str:
        """
        Format rule extraction in a readable way
        """
        result = self.process_text(arabic_text)
        
        output = []
        output.append("=" * 80)
        output.append("TAJWEED RULES EXTRACTION - GENERIC SYSTEM")
        output.append("=" * 80)
        
        output.append(f"\nOriginal Text: {arabic_text}")
        output.append(f"Normalized: {result.normalized_text}")
        output.append(f"\nTotal Rules Found: {len(result.rule_applications)}")
        output.append(f"Unique Rules: {len(set([r.rule_name for r in result.rule_applications]))}")
        
        # Group rules by category
        rules_by_cat = defaultdict(list)
        for app in result.rule_applications:
            rules_by_cat[app.category].append(app)
        
        output.append("\n" + "-" * 80)
        output.append("RULES BY CATEGORY:")
        output.append("-" * 80)
        
        for category, apps in rules_by_cat.items():
            output.append(f"\n{category.upper()}: {len(apps)} application(s)")
            unique_in_cat = set([a.rule_name for a in apps])
            for rule in unique_in_cat:
                count = sum(1 for a in apps if a.rule_name == rule)
                output.append(f"  • {rule}: {count} time(s)")
        
        if detailed:
            output.append("\n" + "-" * 80)
            output.append("DETAILED BREAKDOWN:")
            output.append("-" * 80)
            output.append(f"{'Pos':<4} {'Char':<4} {'Rule':<25} {'Category':<15} {'Sifa':<6} {'Dur':<4}")
            output.append("-" * 80)
            
            for app in sorted(result.rule_applications, key=lambda x: x.position):
                output.append(f"{app.position:<4} {app.arabic_char:<4} "
                            f"{app.rule_name:<25} {app.category:<15} "
                            f"{app.sifa_applied:<6} {app.duration:<4}")
        
        output.append("\n" + "=" * 80)
        return '\n'.join(output)


# ==================== CONVENIENCE FUNCTIONS ====================

def extract_tajweed_rules(arabic_text: str, qiraat: str = "hafs") -> Dict[str, Any]:
    """
    Convenience function to extract Tajweed rules from any Arabic text
    """
    processor = GenericQuranPhoneticScript(qiraat=qiraat)
    return processor.extract_rules_only(arabic_text)


def print_tajweed_rules(arabic_text: str, detailed: bool = False) -> None:
    """
    Convenience function to print Tajweed rules for any Arabic text
    """
    processor = GenericQuranPhoneticScript()
    print(processor.format_rule_extraction(arabic_text, detailed))


def analyze_verse(arabic_text: str) -> Dict[str, Any]:
    """
    Comprehensive analysis of a verse with all Tajweed rules
    """
    processor = GenericQuranPhoneticScript()
    result = processor.process_text(arabic_text)
    
    analysis = {
        'text': arabic_text,
        'phonetic': result.get_phoneme_string(),
        'sifa': result.get_sifa_string(),
        'rules': [
            {
                'rule': app.rule_name,
                'category': app.category,
                'position': app.position,
                'char': app.arabic_char,
                'effect': app.sifa_applied
            }
            for app in result.rule_applications
        ],
        'statistics': {
            'total_chars': len(arabic_text),
            'total_rules': len(result.rule_applications),
            'unique_rules': len(set([r.rule_name for r in result.rule_applications])),
            'categories': list(set([r.category for r in result.rule_applications]))
        }
    }
    
    return analysis


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Test with multiple verses
    test_verses = [
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "قُلْ هُوَ اللَّهُ أَحَدٌ",
        "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        "مَالِكِ يَوْمِ الدِّينِ",
        "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ"
    ]
    
    print("\n" + "=" * 80)
    print("GENERIC TAJWEED RULES EXTRACTION SYSTEM")
    print("=" * 80)
    
    for i, verse in enumerate(test_verses, 1):
        print(f"\n\nTEST VERSE {i}:")
        print("-" * 40)
        print(print_tajweed_rules(verse, detailed=True))
    
    # Example of detailed analysis
    print("\n" + "=" * 80)
    print("DETAILED ANALYSIS EXAMPLE")
    print("=" * 80)
    
    bismillah = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    analysis = analyze_verse(bismillah)
    
    print(f"\nText: {analysis['text']}")
    print(f"Phonetic: {analysis['phonetic']}")
    print(f"\nStatistics:")
    for key, value in analysis['statistics'].items():
        print(f"  {key}: {value}")