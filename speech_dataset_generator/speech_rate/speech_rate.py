import pyphen

from pypinyin import pinyin, Style
from konlpy.tag import Okt

# Try to import CAMeL Tools for Arabic support
try:
    from camel_tools.disambig.mle import MLEDisambiguator
    from camel_tools.tokenizers.morphological import MorphologicalTokenizer
    CAMEL_TOOLS_AVAILABLE = True
except ImportError:
    CAMEL_TOOLS_AVAILABLE = False

class SpeechRate:
    
    def __init__(self):
        # Lazy loading for Arabic models to avoid startup delays
        self._mle_msa = None
        self._tok_msa = None
            
    def check_language_availability(self, language):
        language_codes = list(set(code.split('_')[0] for code in pyphen.LANGUAGES.keys()))
        language_codes.extend(['zh', 'ko', 'ar'])
        return language in language_codes
    
    def _ensure_arabic_tokenizer(self):
        """Lazily initialize Arabic models only when needed."""
        if not CAMEL_TOOLS_AVAILABLE:
            return False
        
        if self._tok_msa is None:
            try:
                self._mle_msa = MLEDisambiguator.pretrained('calima-msa-r13')
                self._tok_msa = MorphologicalTokenizer(
                    disambiguator=self._mle_msa, scheme='d3tok'
                )
                return True
            except Exception:
                return False
        return True
    
    def count_syllables_in_pinyin(self, pinyin_text):
        # Convert Pinyin to numbered Pinyin (with tone numbers)
        pinyin_with_tone_numbers = pinyin(pinyin_text, style=Style.TONE3)

        # Count the number of syllables
        syllable_count = sum([1 for s in pinyin_with_tone_numbers if s[0][-1].isdigit()])
        
        return syllable_count

    def get_total_syllables_per_word(self, word, language):
        
        if not self.check_language_availability(language):
            # Fallback: treat unsupported languages as 1 syllable per word
            return 1
        
        if language == 'zh':
            pinyin_with_tone_numbers = pinyin(word, style=Style.TONE3)
            # Count the number of syllables
            total_syllables = sum([1 for s in pinyin_with_tone_numbers if s[0][-1].isdigit()])
        
        elif language == 'ko':
            okt = Okt()
            morphemes = okt.morphs(word)
            total_syllables = len(morphemes)
            
        elif language == 'ar':
            # Arabic syllable estimation using CAMeL Tools morphological tokenization
            if self._ensure_arabic_tokenizer():
                try:
                    # Split word into morphological tokens (each token ≈ one syllable)
                    tokens = self._tok_msa.tokenize([word])[0]
                    total_syllables = max(1, len(tokens))
                except Exception:
                    # Fallback to simple heuristic if tokenization fails
                    total_syllables = max(1, len(word) // 3)
            else:
                # Fallback: simple character-based heuristic for Arabic
                total_syllables = max(1, len(word) // 3)
                
        else:
            # Use pyphen for other supported languages
            dic = pyphen.Pyphen(lang=language)
            total_syllables = len(dic.inserted(word).split('-'))
            
        return total_syllables

    def get_syllables_per_minute(self, words, language, duration_in_seconds):

        total_syllables = sum(self.get_total_syllables_per_word(word, language) for word in words)

        spm = (total_syllables / duration_in_seconds) * 60

        return round(spm, 3)
    
    def get_words_per_minute(self, words, duration_in_seconds):
        
        wpm = (len(words) / duration_in_seconds) * 60

        return round(wpm, 3)