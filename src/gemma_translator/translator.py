"""Translation logic using LangChain and Ollama.

Implements the "Divide and Conquer" strategy for translating large documents
by splitting text into chunks and processing them sequentially.
"""

from collections.abc import Generator

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from .config import Settings


# Translation prompt template as specified in requirements
# Note: Two blank lines before the text are mandatory for TranslateGemma
TRANSLATION_PROMPT_TEMPLATE = """You are a professional {source_lang} ({source_code}) to {target_lang} ({target_code}) translator. Your goal is to accurately convey the meaning and nuances of the original {source_lang} text while adhering to {target_lang} grammar, vocabulary, and cultural sensitivities.
Produce only the {target_lang} translation, without any additional explanations or commentary. Please translate the following {source_lang} text into {target_lang}:


{text}"""


class Translator:
    """Handles document translation using LangChain and Ollama."""
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the translator with configuration.
        
        Args:
            settings: Application settings instance.
        """
        self.settings = settings
        self.llm = ChatOllama(
            model=settings.model_name,
            base_url=settings.api_base,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            # Separators optimized for preserving sentence structure
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
        )
    
    def translate_chunk(self, text: str) -> str:
        """Translate a single text chunk.
        
        Args:
            text: Text chunk to translate.
            
        Returns:
            Translated text.
            
        Raises:
            ConnectionError: If Ollama is not available.
        """
        # Build the single user prompt according to specifications
        prompt = TRANSLATION_PROMPT_TEMPLATE.format(
            source_lang=self.settings.source_lang,
            source_code=self.settings.source_code,
            target_lang=self.settings.target_lang,
            target_code=self.settings.target_code,
            text=text,
        )
        
        messages = [HumanMessage(content=prompt)]
        
        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            if "Connection" in str(type(e).__name__) or "connection" in str(e).lower():
                raise ConnectionError(
                    f"Failed to connect to Ollama at {self.settings.api_base}. "
                    "Please ensure Ollama is running."
                ) from e
            raise
    
    def split_text(self, text: str) -> list[str]:
        """Split text into chunks for translation.
        
        Args:
            text: Full document text to split.
            
        Returns:
            List of text chunks.
        """
        return self.splitter.split_text(text)
    
    def translate_document(self, text: str) -> Generator[tuple[int, int, str], None, None]:
        """Translate a full document, yielding progress updates.
        
        Args:
            text: Full document text to translate.
            
        Yields:
            Tuples of (current_chunk_index, total_chunks, translated_chunk).
        """
        chunks = self.split_text(text)
        total = len(chunks)
        
        for i, chunk in enumerate(chunks):
            translated = self.translate_chunk(chunk)
            yield i, total, translated
