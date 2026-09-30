package com.example.text;

import org.apache.commons.lang3.*;
import org.apache.commons.text.similarity.*;
import java.util.*;
import java.util.stream.Collectors;

class TextStatistics {
    private final int characterCount;
    private final int wordCount;
    private final int sentenceCount;
    private final int paragraphCount;
    private final double averageWordLength;
    private final double averageSentenceLength;

    public TextStatistics(String text) {
        this.characterCount = text.length();
        this.wordCount = countWords(text);
        this.sentenceCount = countSentences(text);
        this.paragraphCount = countParagraphs(text);
        this.averageWordLength = calculateAverageWordLength(text);
        this.averageSentenceLength = wordCount / (double) Math.max(sentenceCount, 1);
    }

    private int countWords(String text) {
        return text.isBlank() ? 0 : text.trim().split("\\s+").length;
    }

    private int countSentences(String text) {
        return Math.max(1, text.split("[.!?]+").length);
    }

    private int countParagraphs(String text) {
        return Math.max(1, text.split("\\n\\s*\\n").length);
    }

    private double calculateAverageWordLength(String text) {
        String[] words = text.split("\\s+");
        return words.length == 0 ? 0 : Arrays.stream(words)
            .mapToInt(String::length)
            .average()
            .orElse(0);
    }

    public int getCharacterCount() { return characterCount; }
    public int getWordCount() { return wordCount; }
    public int getSentenceCount() { return sentenceCount; }
    public int getParagraphCount() { return paragraphCount; }
    public double getAverageWordLength() { return averageWordLength; }
    public double getAverageSentenceLength() { return averageSentenceLength; }

    @Override
    public String toString() {
        return String.format("""
            Text Statistics:
              Characters: %d
              Words: %d
              Sentences: %d
              Paragraphs: %d
              Avg word length: %.2f
              Avg sentence length: %.2f words
            """, characterCount, wordCount, sentenceCount, paragraphCount,
            averageWordLength, averageSentenceLength);
    }
}

class TextAnalyzer {

    public static Map<String, Integer> wordFrequency(String text) {
        Map<String, Integer> frequency = new HashMap<>();

        String[] words = text.toLowerCase()
            .replaceAll("[^a-z\\s]", "")
            .split("\\s+");

        for (String word : words) {
            if (!word.isBlank()) {
                frequency.merge(word, 1, Integer::sum);
            }
        }

        return frequency;
    }

    public static List<Map.Entry<String, Integer>> topWords(String text, int n) {
        return wordFrequency(text).entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(n)
            .collect(Collectors.toList());
    }

    public static Map<String, Integer> wordFrequencyWithoutStopwords(String text) {
        Set<String> stopwords = Set.of(
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "is", "was", "are", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "should",
            "could", "may", "might", "must", "can", "this", "that", "these", "those"
        );

        return wordFrequency(text).entrySet().stream()
            .filter(entry -> !stopwords.contains(entry.getKey()))
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    public static double readabilityScore(String text) {
        TextStatistics stats = new TextStatistics(text);

        // Simplified Flesch Reading Ease formula
        double avgSentenceLength = stats.getAverageSentenceLength();
        double avgSyllablesPerWord = stats.getAverageWordLength() / 2.0; // Approximation

        return 206.835 - 1.015 * avgSentenceLength - 84.6 * avgSyllablesPerWord;
    }

    public static String sentimentAnalysis(String text) {
        String lowerText = text.toLowerCase();

        Set<String> positiveWords = Set.of(
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "happy", "joy", "positive", "success", "best", "beautiful"
        );

        Set<String> negativeWords = Set.of(
            "bad", "terrible", "awful", "horrible", "hate", "sad", "negative",
            "failure", "worst", "ugly", "disappointed", "angry", "frustrated"
        );

        int positiveCount = 0;
        int negativeCount = 0;

        for (String word : lowerText.split("\\s+")) {
            String cleanWord = word.replaceAll("[^a-z]", "");
            if (positiveWords.contains(cleanWord)) positiveCount++;
            if (negativeWords.contains(cleanWord)) negativeCount++;
        }

        int totalSentiment = positiveCount - negativeCount;

        if (totalSentiment > 2) return "Very Positive";
        if (totalSentiment > 0) return "Positive";
        if (totalSentiment < -2) return "Very Negative";
        if (totalSentiment < 0) return "Negative";
        return "Neutral";
    }

    public static List<String> extractKeywords(String text, int n) {
        return wordFrequencyWithoutStopwords(text).entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(n)
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }

    public static List<String> generateNGrams(String text, int n) {
        String[] words = text.toLowerCase()
            .replaceAll("[^a-z\\s]", "")
            .split("\\s+");

        List<String> ngrams = new ArrayList<>();

        for (int i = 0; i <= words.length - n; i++) {
            StringBuilder ngram = new StringBuilder();
            for (int j = 0; j < n; j++) {
                if (j > 0) ngram.append(" ");
                ngram.append(words[i + j]);
            }
            ngrams.add(ngram.toString());
        }

        return ngrams;
    }
}

class TextTransformer {

    public static String toTitleCase(String text) {
        return Arrays.stream(text.split("\\s+"))
            .map(word -> word.isEmpty() ? word :
                Character.toUpperCase(word.charAt(0)) + word.substring(1).toLowerCase())
            .collect(Collectors.joining(" "));
    }

    public static String toCamelCase(String text) {
        String[] words = text.split("[\\s_-]+");
        StringBuilder result = new StringBuilder(words[0].toLowerCase());

        for (int i = 1; i < words.length; i++) {
            result.append(toTitleCase(words[i]));
        }

        return result.toString();
    }

    public static String toSnakeCase(String text) {
        return text.replaceAll("\\s+", "_")
                  .replaceAll("([a-z])([A-Z])", "$1_$2")
                  .toLowerCase();
    }

    public static String toKebabCase(String text) {
        return text.replaceAll("\\s+", "-")
                  .replaceAll("([a-z])([A-Z])", "$1-$2")
                  .toLowerCase();
    }

    public static String removeStopwords(String text) {
        Set<String> stopwords = Set.of(
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"
        );

        return Arrays.stream(text.split("\\s+"))
            .filter(word -> !stopwords.contains(word.toLowerCase()))
            .collect(Collectors.joining(" "));
    }

    public static String truncate(String text, int maxLength, String suffix) {
        if (text.length() <= maxLength) {
            return text;
        }

        return text.substring(0, maxLength - suffix.length()) + suffix;
    }

    public static String reverse(String text) {
        return new StringBuilder(text).reverse().toString();
    }

    public static String reverseWords(String text) {
        String[] words = text.split("\\s+");
        Collections.reverse(Arrays.asList(words));
        return String.join(" ", words);
    }

    public static String replaceAll(String text, Map<String, String> replacements) {
        String result = text;
        for (Map.Entry<String, String> entry : replacements.entrySet()) {
            result = result.replace(entry.getKey(), entry.getValue());
        }
        return result;
    }
}

class TextSimilarity {

    public static double levenshteinSimilarity(String text1, String text2) {
        LevenshteinDistance distance = new LevenshteinDistance();
        int dist = distance.apply(text1, text2);
        int maxLength = Math.max(text1.length(), text2.length());
        return maxLength == 0 ? 1.0 : 1.0 - (dist / (double) maxLength);
    }

    public static double jaccardSimilarity(String text1, String text2) {
        Set<String> words1 = new HashSet<>(Arrays.asList(text1.toLowerCase().split("\\s+")));
        Set<String> words2 = new HashSet<>(Arrays.asList(text2.toLowerCase().split("\\s+")));

        Set<String> intersection = new HashSet<>(words1);
        intersection.retainAll(words2);

        Set<String> union = new HashSet<>(words1);
        union.addAll(words2);

        return union.isEmpty() ? 0.0 : intersection.size() / (double) union.size();
    }

    public static double cosineSimilarity(String text1, String text2) {
        Map<String, Integer> freq1 = TextAnalyzer.wordFrequency(text1);
        Map<String, Integer> freq2 = TextAnalyzer.wordFrequency(text2);

        Set<String> allWords = new HashSet<>();
        allWords.addAll(freq1.keySet());
        allWords.addAll(freq2.keySet());

        double dotProduct = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;

        for (String word : allWords) {
            int count1 = freq1.getOrDefault(word, 0);
            int count2 = freq2.getOrDefault(word, 0);

            dotProduct += count1 * count2;
            norm1 += count1 * count1;
            norm2 += count2 * count2;
        }

        return (norm1 * norm2 == 0) ? 0.0 : dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
    }
}

public class TextProcessorApp {

    public static void main(String[] args) {
        System.out.println("=== Text Processing & Analysis Utility ===\n");

        String sampleText = """
            The quick brown fox jumps over the lazy dog. This is a wonderful example
            of a pangram sentence that contains every letter of the alphabet. Text
            processing and analysis is an important field in natural language processing.
            We can extract keywords, analyze sentiment, and calculate various statistics
            from text data. This technology is used in search engines, chatbots, and
            content analysis systems.
            """;

        // Example 1: Text statistics
        System.out.println("--- Example 1: Text Statistics ---");
        TextStatistics stats = new TextStatistics(sampleText);
        System.out.println(stats);

        // Example 2: Word frequency analysis
        System.out.println("--- Example 2: Word Frequency ---");
        List<Map.Entry<String, Integer>> topWords = TextAnalyzer.topWords(sampleText, 10);
        System.out.println("Top 10 most frequent words:");
        for (int i = 0; i < topWords.size(); i++) {
            Map.Entry<String, Integer> entry = topWords.get(i);
            System.out.println("  " + (i + 1) + ". " + entry.getKey() + ": " + entry.getValue());
        }

        // Example 3: Keyword extraction
        System.out.println("\n--- Example 3: Keyword Extraction ---");
        List<String> keywords = TextAnalyzer.extractKeywords(sampleText, 5);
        System.out.println("Top 5 keywords (excluding stopwords):");
        keywords.forEach(kw -> System.out.println("  - " + kw));

        // Example 4: Sentiment analysis
        System.out.println("\n--- Example 4: Sentiment Analysis ---");
        String positiveText = "This is a wonderful and amazing product! I love it!";
        String negativeText = "This is terrible and awful. I hate it completely.";
        String neutralText = "This is a product that exists in the market.";

        System.out.println("Text: \"" + positiveText + "\"");
        System.out.println("Sentiment: " + TextAnalyzer.sentimentAnalysis(positiveText));

        System.out.println("\nText: \"" + negativeText + "\"");
        System.out.println("Sentiment: " + TextAnalyzer.sentimentAnalysis(negativeText));

        System.out.println("\nText: \"" + neutralText + "\"");
        System.out.println("Sentiment: " + TextAnalyzer.sentimentAnalysis(neutralText));

        // Example 5: Readability score
        System.out.println("\n--- Example 5: Readability Score ---");
        double readability = TextAnalyzer.readabilityScore(sampleText);
        System.out.println("Readability score: " + readability);
        System.out.println("Interpretation: " +
            (readability > 60 ? "Easy to read" : readability > 30 ? "Moderate" : "Difficult"));

        // Example 6: N-grams
        System.out.println("\n--- Example 6: N-gram Generation ---");
        List<String> bigrams = TextAnalyzer.generateNGrams(sampleText, 2);
        System.out.println("Sample bigrams (first 5):");
        bigrams.stream().limit(5).forEach(bg -> System.out.println("  " + bg));

        List<String> trigrams = TextAnalyzer.generateNGrams(sampleText, 3);
        System.out.println("\nSample trigrams (first 5):");
        trigrams.stream().limit(5).forEach(tg -> System.out.println("  " + tg));

        // Example 7: Text transformations
        System.out.println("\n--- Example 7: Text Transformations ---");
        String text = "hello world from java";

        System.out.println("Original: " + text);
        System.out.println("Title Case: " + TextTransformer.toTitleCase(text));
        System.out.println("Camel Case: " + TextTransformer.toCamelCase(text));
        System.out.println("Snake Case: " + TextTransformer.toSnakeCase(text));
        System.out.println("Kebab Case: " + TextTransformer.toKebabCase(text));
        System.out.println("Reversed: " + TextTransformer.reverse(text));
        System.out.println("Reversed Words: " + TextTransformer.reverseWords(text));

        // Example 8: Text similarity
        System.out.println("\n--- Example 8: Text Similarity ---");
        String text1 = "The quick brown fox jumps over the lazy dog";
        String text2 = "The quick brown fox leaps over the sleeping dog";
        String text3 = "Completely different sentence about cats";

        System.out.println("Text 1: " + text1);
        System.out.println("Text 2: " + text2);
        System.out.println("Text 3: " + text3);

        System.out.println("\nSimilarity (Text 1 vs Text 2):");
        System.out.println("  Levenshtein: " +
            String.format("%.2f", TextSimilarity.levenshteinSimilarity(text1, text2)));
        System.out.println("  Jaccard: " +
            String.format("%.2f", TextSimilarity.jaccardSimilarity(text1, text2)));
        System.out.println("  Cosine: " +
            String.format("%.2f", TextSimilarity.cosineSimilarity(text1, text2)));

        System.out.println("\nSimilarity (Text 1 vs Text 3):");
        System.out.println("  Levenshtein: " +
            String.format("%.2f", TextSimilarity.levenshteinSimilarity(text1, text3)));
        System.out.println("  Jaccard: " +
            String.format("%.2f", TextSimilarity.jaccardSimilarity(text1, text3)));
        System.out.println("  Cosine: " +
            String.format("%.2f", TextSimilarity.cosineSimilarity(text1, text3)));

        // Example 9: String manipulation
        System.out.println("\n--- Example 9: String Manipulation ---");
        String longText = "This is a very long text that needs to be truncated for display purposes";
        System.out.println("Truncated: " + TextTransformer.truncate(longText, 30, "..."));

        String textWithStopwords = "The quick brown fox jumps over the lazy dog";
        System.out.println("Original: " + textWithStopwords);
        System.out.println("Without stopwords: " +
            TextTransformer.removeStopwords(textWithStopwords));

        // Example 10: Batch replacements
        System.out.println("\n--- Example 10: Batch Text Replacement ---");
        String template = "Hello [NAME], welcome to [PLACE]! Today is [DAY].";
        Map<String, String> replacements = Map.of(
            "[NAME]", "Alice",
            "[PLACE]", "Java World",
            "[DAY]", "Monday"
        );

        System.out.println("Template: " + template);
        System.out.println("Result: " + TextTransformer.replaceAll(template, replacements));

        System.out.println("\n=== Text Processing Demo Complete ===");
        System.out.println("\nKey Features:");
        System.out.println("  ✓ Text statistics (words, sentences, paragraphs)");
        System.out.println("  ✓ Word frequency analysis");
        System.out.println("  ✓ Keyword extraction");
        System.out.println("  ✓ Sentiment analysis");
        System.out.println("  ✓ Readability scoring");
        System.out.println("  ✓ N-gram generation");
        System.out.println("  ✓ Text transformations (case conversions)");
        System.out.println("  ✓ Text similarity metrics");
        System.out.println("  ✓ String manipulation utilities");
    }
}
