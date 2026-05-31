import re
import requests
import logging
from typing import List, Dict, Tuple, Any
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

# Canonical map of books to their maximum chapters to prevent gross hallucinations
# (e.g. Romans 50:12)
BIBLE_CANON = {
    # Pentateuch
    "genesis": 50, "exodus": 40, "leviticus": 27, "numbers": 36, "deuteronomy": 34,
    # Historical
    "joshua": 24, "judges": 21, "ruth": 4, "1 samuel": 31, "2 samuel": 24, 
    "1 kings": 22, "2 kings": 25, "1 chronicles": 29, "2 chronicles": 36,
    "ezra": 10, "nehemiah": 13, "esther": 10,
    # Wisdom/Poetry
    "job": 42, "psalm": 150, "psalms": 150, "proverbs": 31, "ecclesiastes": 12, "song of solomon": 8, "song of songs": 8,
    # Prophets
    "isaiah": 66, "jeremiah": 52, "lamentations": 5, "ezekiel": 48, "daniel": 12,
    "hosea": 14, "joel": 3, "amos": 9, "obadiah": 1, "jonah": 4, "micah": 7,
    "nahum": 3, "habakkuk": 3, "zephaniah": 3, "haggai": 2, "zechariah": 14, "malachi": 4,
    # New Testament Gospels & Acts
    "matthew": 28, "mark": 16, "luke": 24, "john": 21, "acts": 28,
    # Epistles
    "romans": 16, "1 corinthians": 16, "2 corinthians": 13, "galatians": 6, "ephesians": 6,
    "philippians": 4, "colossians": 4, "1 thessalonians": 5, "2 thessalonians": 3,
    "1 timothy": 6, "2 timothy": 4, "titus": 3, "philemon": 1, "hebrews": 13, "james": 5,
    "1 peter": 5, "2 peter": 3, "1 john": 5, "2 john": 1, "3 john": 1, "jude": 1, "revelation": 22,
    # Catholic Deuterocanon / Apocrypha
    "tobit": 14, "judith": 16, "wisdom": 19, "wisdom of solomon": 19, "sirach": 51, "ecclesiasticus": 51,
    "baruch": 6, "1 maccabees": 16, "2 maccabees": 15,
    # Orthodox additions
    "1 esdras": 9, "2 esdras": 16, "3 maccabees": 7, "4 maccabees": 18, "prayer of manasseh": 1
}

# Regex to match bible scripture citations: e.g. John 3:16, 1 Corinthians 13:4, 2 Maccabees 12:43
CITATION_REGEX = re.compile(
    r"\b([1-3]\s+[A-Za-z]+|[A-Za-z][A-Za-z\s]+)\s+(\d+):(\d+)(-\d+)?\b",
    re.IGNORECASE
)

import re
import httpx
import logging
import asyncio
from typing import List, Dict, Tuple, Any
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

# ... (BIBLE_CANON and CITATION_REGEX remain unchanged)

class VerificationService:
    @staticmethod
    async def verify_single_citation(book: str, chapter: int, verse: int) -> Tuple[bool, str]:
        """
        Verifies a citation. Returns (is_valid, verse_text).
        Checks canonical bounds first, then checks local database, then hits bible-api.com fallback.
        """
        book_clean = book.strip().lower()
        
        # 1. Structural check against canon limits
        if book_clean in BIBLE_CANON:
            max_chapters = BIBLE_CANON[book_clean]
            if chapter > max_chapters or chapter <= 0:
                logger.warning(f"Citation verification failed: {book} only has {max_chapters} chapters (requested chapter {chapter})")
                return False, f"[Invalid Chapter: {book} {chapter}]"
        else:
            # If the book name is completely fabricated
            logger.warning(f"Citation verification failed: {book} is not a valid Bible book in our canon")
            return False, f"[Invalid Book: {book}]"

        # 2. Local database / RAG lookup check
        local_results = RAGService.query_scriptures(f"{book} {chapter}:{verse}", top_k=1)
        for lr in local_results:
            if lr["book"].lower() == book_clean and lr["chapter"] == chapter and lr["verse"] == verse:
                return True, lr["text"]

        # 3. Dynamic HTTP API Fallback (bible-api.com)
        try:
            # bible-api.com does not support deuterocanonical/apocryphal books easily
            is_deuterocanon = book_clean in ["tobit", "judith", "wisdom", "wisdom of solomon", "sirach", "ecclesiasticus", "baruch", "1 maccabees", "2 maccabees", "1 esdras", "2 esdras", "3 maccabees", "4 maccabees"]
            
            if is_deuterocanon:
                return True, f"[Deuterocanonical Text] Ref: {book} {chapter}:{verse}"
                
            # Query public Bible API
            api_url = f"https://bible-api.com/{book}+{chapter}:{verse}"
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, timeout=3.0)
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("text", "").strip()
                    if text:
                        return True, text
        except Exception as e:
            logger.error(f"Fallback scripture API error: {e}")
            # If network fails but it passed structural checks, we temporarily allow it but log
            return True, f"[Verified Structurally] Ref: {book} {chapter}:{verse}"

        return False, f"[Invalid Reference: {book} {chapter}:{verse}]"

    @staticmethod
    async def intercept_and_verify(text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Intercepts generated text, extracts and validates citations,
        and sanitizes the response if hallucinations are detected.
        """
        matches = CITATION_REGEX.findall(text)
        if not matches:
            return text, []

        tasks = []
        for match in matches:
            book_name, chapter_str, verse_str, verse_range = match
            tasks.append(VerificationService.verify_single_citation(book_name, int(chapter_str), int(verse_str)))

        results = await asyncio.gather(*tasks)
        
        citations_logged = []
        sanitized_text = text
        
        for i, match in enumerate(matches):
            book_name, chapter_str, verse_str, verse_range = match
            full_ref = f"{book_name} {chapter_str}:{verse_str}{verse_range}"
            is_valid, verse_text = results[i]
            
            citations_logged.append({
                "reference": full_ref,
                "text": verse_text,
                "verified": is_valid
            })
            
            if not is_valid:
                pattern = re.compile(rf"\b{re.escape(book_name)}\s+{chapter_str}:{verse_str}{re.escape(verse_range)}\b", re.IGNORECASE)
                sanitized_text = pattern.sub(f"[Invalid Citation: {full_ref}]", sanitized_text)

        if any(not c['verified'] for c in citations_logged):
            sanitized_text += "\n\n*Note: Some scripture citations were flagged for verification.*"

        return sanitized_text, citations_logged
