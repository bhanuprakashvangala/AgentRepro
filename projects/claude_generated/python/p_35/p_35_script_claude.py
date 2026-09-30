"""
Text Summarization Tool
Supports both extractive and abstractive summarization methods
"""

import os
from typing import List, Dict, Union, Optional
from enum import Enum
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import warnings

warnings.filterwarnings('ignore')


class SummarizationMethod(Enum):
    """Available summarization methods"""
    EXTRACTIVE_LSA = "extractive_lsa"
    EXTRACTIVE_LUHN = "extractive_luhn"
    EXTRACTIVE_TEXTRANK = "extractive_textrank"
    ABSTRACTIVE_BART = "abstractive_bart"
    ABSTRACTIVE_T5 = "abstractive_t5"


class TextSummarizer:
    """
    A comprehensive text summarization tool supporting multiple methods
    """

    def __init__(self, method: Union[str, SummarizationMethod] = SummarizationMethod.EXTRACTIVE_TEXTRANK):
        """
        Initialize the summarizer with specified method

        Args:
            method: Summarization method to use
        """
        if isinstance(method, str):
            method = SummarizationMethod(method)

        self.method = method
        self.pipeline = None
        self.tokenizer = None
        self.model = None

        # Download required NLTK data
        self._setup_nltk()

        # Initialize the appropriate summarizer
        if method in [SummarizationMethod.ABSTRACTIVE_BART, SummarizationMethod.ABSTRACTIVE_T5]:
            self._setup_abstractive(method)
        else:
            self._setup_extractive(method)

    def _setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)

    def _setup_extractive(self, method: SummarizationMethod):
        """Setup extractive summarization"""
        if method == SummarizationMethod.EXTRACTIVE_LSA:
            self.summarizer = LsaSummarizer()
        elif method == SummarizationMethod.EXTRACTIVE_LUHN:
            self.summarizer = LuhnSummarizer()
        elif method == SummarizationMethod.EXTRACTIVE_TEXTRANK:
            self.summarizer = TextRankSummarizer()

    def _setup_abstractive(self, method: SummarizationMethod):
        """Setup abstractive summarization using transformers"""
        print(f"Loading {method.value} model... This may take a moment.")

        if method == SummarizationMethod.ABSTRACTIVE_BART:
            model_name = "facebook/bart-large-cnn"
        else:  # T5
            model_name = "t5-small"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.pipeline = pipeline("summarization", model=self.model, tokenizer=self.tokenizer)
        print(f"Model loaded successfully!")

    def summarize(
        self,
        text: str,
        num_sentences: int = 3,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None
    ) -> str:
        """
        Summarize a single text document

        Args:
            text: Input text to summarize
            num_sentences: Number of sentences for extractive summary
            max_length: Maximum length for abstractive summary (in tokens)
            min_length: Minimum length for abstractive summary (in tokens)

        Returns:
            Summarized text
        """
        if not text or not text.strip():
            return ""

        # Choose summarization method
        if self.method in [SummarizationMethod.ABSTRACTIVE_BART, SummarizationMethod.ABSTRACTIVE_T5]:
            return self._abstractive_summarize(text, max_length, min_length)
        else:
            return self._extractive_summarize(text, num_sentences)

    def _extractive_summarize(self, text: str, num_sentences: int) -> str:
        """Perform extractive summarization"""
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summary = self.summarizer(parser.document, num_sentences)
        return " ".join([str(sentence) for sentence in summary])

    def _abstractive_summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None
    ) -> str:
        """Perform abstractive summarization"""
        # Set default lengths if not provided
        if max_length is None:
            max_length = 150
        if min_length is None:
            min_length = 30

        # Handle long texts by chunking if necessary
        max_input_length = 1024
        tokens = self.tokenizer.encode(text, truncation=True, max_length=max_input_length)

        if len(tokens) > max_input_length:
            text = self.tokenizer.decode(tokens[:max_input_length], skip_special_tokens=True)

        # Generate summary
        summary = self.pipeline(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )

        return summary[0]['summary_text']

    def summarize_batch(
        self,
        texts: List[str],
        num_sentences: int = 3,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        show_progress: bool = True
    ) -> List[str]:
        """
        Summarize multiple documents in batch

        Args:
            texts: List of input texts
            num_sentences: Number of sentences for extractive summary
            max_length: Maximum length for abstractive summary
            min_length: Minimum length for abstractive summary
            show_progress: Show progress during batch processing

        Returns:
            List of summarized texts
        """
        summaries = []
        total = len(texts)

        for idx, text in enumerate(texts):
            if show_progress:
                print(f"Processing document {idx + 1}/{total}...", end='\r')

            summary = self.summarize(
                text,
                num_sentences=num_sentences,
                max_length=max_length,
                min_length=min_length
            )
            summaries.append(summary)

        if show_progress:
            print(f"\nCompleted processing {total} documents!")

        return summaries

    def get_summary_stats(self, original_text: str, summary: str) -> Dict[str, Union[int, float]]:
        """
        Get statistics about the summarization

        Args:
            original_text: Original text
            summary: Summarized text

        Returns:
            Dictionary with statistics
        """
        return {
            'original_length': len(original_text),
            'summary_length': len(summary),
            'original_words': len(original_text.split()),
            'summary_words': len(summary.split()),
            'compression_ratio': len(summary) / len(original_text) if len(original_text) > 0 else 0
        }


def main():
    """Demo usage of the text summarization tool"""

    # Sample texts for demonstration
    sample_text_1 = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural
    intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of
    "intelligent agents": any device that perceives its environment and takes actions that maximize its
    chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" is often
    used to describe machines (or computers) that mimic "cognitive" functions that humans associate with
    the human mind, such as "learning" and "problem solving". As machines become increasingly capable,
    tasks considered to require "intelligence" are often removed from the definition of AI, a phenomenon
    known as the AI effect. A quip in Tesler's Theorem says "AI is whatever hasn't been done yet." For
    instance, optical character recognition is frequently excluded from things considered to be AI, having
    become a routine technology.
    """

    sample_text_2 = """
    Climate change includes both global warming driven by human-induced emissions of greenhouse gases
    and the resulting large-scale shifts in weather patterns. Though there have been previous periods of
    climatic change, since the mid-20th century humans have had an unprecedented impact on Earth's climate
    system and caused change on a global scale. The largest driver of warming is the emission of gases that
    create a greenhouse effect, of which more than 90% are carbon dioxide and methane. Fossil fuel burning
    (coal, oil, and natural gas) for energy consumption is the main source of these emissions, with additional
    contributions from agriculture, deforestation, and manufacturing. Temperature rise is accelerated or
    tempered by climate feedbacks, such as loss of sunlight-reflecting snow and ice cover, increased water
    vapour (a greenhouse gas itself), and changes to land and ocean carbon sinks.
    """

    sample_texts = [sample_text_1, sample_text_2]

    print("=" * 80)
    print("TEXT SUMMARIZATION TOOL - DEMONSTRATION")
    print("=" * 80)

    # Example 1: Extractive summarization with TextRank
    print("\n1. EXTRACTIVE SUMMARIZATION (TextRank)")
    print("-" * 80)
    summarizer = TextSummarizer(method=SummarizationMethod.EXTRACTIVE_TEXTRANK)
    summary = summarizer.summarize(sample_text_1, num_sentences=2)
    print(f"Summary: {summary}")
    stats = summarizer.get_summary_stats(sample_text_1, summary)
    print(f"\nStats: Compression ratio: {stats['compression_ratio']:.2%}")

    # Example 2: Extractive summarization with LSA
    print("\n\n2. EXTRACTIVE SUMMARIZATION (LSA)")
    print("-" * 80)
    summarizer_lsa = TextSummarizer(method=SummarizationMethod.EXTRACTIVE_LSA)
    summary_lsa = summarizer_lsa.summarize(sample_text_2, num_sentences=2)
    print(f"Summary: {summary_lsa}")

    # Example 3: Batch processing with extractive method
    print("\n\n3. BATCH PROCESSING (Extractive - Luhn)")
    print("-" * 80)
    summarizer_batch = TextSummarizer(method=SummarizationMethod.EXTRACTIVE_LUHN)
    summaries = summarizer_batch.summarize_batch(sample_texts, num_sentences=2)
    for idx, summary in enumerate(summaries):
        print(f"\nDocument {idx + 1} Summary:")
        print(summary)

    # Example 4: Abstractive summarization (commented out by default as it's slower)
    print("\n\n4. ABSTRACTIVE SUMMARIZATION (T5) - Optional")
    print("-" * 80)
    print("Uncomment the code below to test abstractive summarization")
    print("Note: This will download and load a transformer model (~500MB)")

    # Uncomment to test abstractive summarization:
    # summarizer_abs = TextSummarizer(method=SummarizationMethod.ABSTRACTIVE_T5)
    # summary_abs = summarizer_abs.summarize(sample_text_1, max_length=100, min_length=30)
    # print(f"Abstractive Summary: {summary_abs}")

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
