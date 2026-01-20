"""Translation logic using LangChain and Ollama.

Implements the "Divide and Conquer" strategy for translating large documents
by splitting text into chunks and processing them sequentially.
"""
from collections.abc import Generator
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from .config import Settings

# Note: Two blank lines before the text are mandatory for TranslateGemma
TRANSLATION_PROMPT_TEMPLATE = """You are a professional {source_lang} ({source_code}) to {target_lang} ({target_code}) translator. Your goal is to accurately convey the meaning and nuances of the original {source_lang} text while adhering to {target_lang} grammar, vocabulary, and cultural sensitivities.
Produce only the {target_lang} translation, without any additional explanations or commentary. Please translate the following {source_lang} text into {target_lang}:


{text}"""

class Translator:
    """Handles document translation using LangChain and Ollama."""
    
    def __init__(self, settings: Settings) -> None:
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
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]
        )
    
    def translate_chunk(self, text: str) -> str:
        """Translate a single text chunk."""
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
            if "connection" in str(e).lower():
                raise ConnectionError(
                    f"Failed to connect to Ollama at {self.settings.api_base}. "
                    "Please ensure Ollama is running."
                ) from e
            raise
    
    def split_text(self, text: str) -> list[str]:
        """Split text into chunks."""
        return self.splitter.split_text(text)
    
    def translate_document(self, text: str) -> Generator[tuple[int, int, str], None, None]:
        """Translate a full document, yielding progress updates."""
        chunks = self.split_text(text)
        total = len(chunks)
        
        for i, chunk in enumerate(chunks):
            translated = self.translate_chunk(chunk)
            yield i, total, translated