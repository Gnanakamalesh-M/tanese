# VISION (context only - do NOT build from this directly)

# TANese — Tamil + Japanese Constructed Language NLP/LLM Project

## PROJECT GOAL

Build a **unique, technically strong, college-level GitHub project** called **Tanese**.

Tanese is a newly designed constructed language inspired by **Tamil and Japanese**.

This is NOT intended to become a complete real-world language ecosystem.

The goal is to create a **well-designed, internally consistent experimental language** and demonstrate modern NLP/LLM engineering through it.

The project should be:

- Unique
- Technically impressive
- Realistically finishable by a college student
- Well documented
- Reproducible
- Suitable for GitHub
- Suitable for a resume
- Suitable for demonstrating NLP/LLM knowledge

Do NOT over-engineer the project.

---

# 1. CORE CONCEPT

Tanese must not simply concatenate Tamil and Japanese words.

It must have:

- Its own writing system
- Its own letters
- Its own phonology
- Its own pronunciation rules
- Its own grammar
- Its own syntax
- Its own vocabulary
- Its own word-generation rules
- Its own sentence-generation rules

Tamil and Japanese are inspirations, but Tanese must have an independent identity.

---

# 2. LANGUAGE DESIGN

Design and document:

### Phonology

- Vowels
- Consonants
- Long vowels
- Allowed sound combinations
- Syllable structure
- Word beginnings/endings
- Pronunciation rules

### Writing system

Create a new Tanese script.

Do NOT simply reuse Tamil letters or Japanese kana.

Define:

- Character inventory
- Vowel characters
- Consonant characters
- Character combinations
- Writing rules
- Character-to-sound mapping
- Romanization

A technically practical representation can be used initially.

### Grammar

Define:

- Default sentence order
- Nouns
- Verbs
- Adjectives
- Adverbs
- Pronouns
- Particles
- Questions
- Negation
- Commands
- Possession
- Pluralization
- Tense
- Aspect
- Mood
- Politeness

Do not blindly copy Tamil or Japanese grammar.

Every major rule should have a clear reason.

---

# 3. VOCABULARY SYSTEM

Create a structured Tanese vocabulary.

Each word should contain:

- Tanese form
- Script form
- Romanization
- Pronunciation
- Meaning
- Part of speech
- Root
- Derived forms
- Tamil equivalent
- Japanese equivalent
- English equivalent
- Example sentence

Start with a manageable vocabulary, approximately **300–1000 words**, rather than trying to create thousands immediately.

---

# 4. VOCABULARY GENERATION

This is one of the main unique features.

Create an algorithm for generating new Tanese vocabulary.

The system should consider:

1. Meaning/concept
2. Tanese phonology
3. Existing roots
4. Word-formation rules
5. Semantic similarity
6. Phonetic similarity
7. Existing dictionary collisions
8. Pronunciation difficulty

Pipeline:

CONCEPT
→ Candidate generation
→ Phonological validation
→ Morphological validation
→ Collision detection
→ Semantic validation
→ Candidate ranking
→ Human approval

The LLM can suggest candidates, but it must NOT automatically make them official.

---

# 5. COLLISION DETECTION

Build a system that detects:

- Exact word collisions
- Similar-sounding words
- Similar spellings
- Conflicting meanings
- Ambiguous word formations

Use:

- String similarity
- Phonetic similarity
- Embeddings
- Semantic similarity

Reject problematic candidates.

---

# 6. TANese CORPUS

Create a small but high-quality corpus.

Include:

### Vocabulary examples

Tanese ↔ Tamil ↔ Japanese ↔ English

### Grammar examples

Valid sentences

### Negative examples

Incorrect Tanese sentences

### Translation examples

Tamil → Tanese
Japanese → Tanese
English → Tanese

### Conversation examples

Simple Tanese conversations.

Focus on quality and consistency instead of dataset size.

---

# 7. NLP COMPONENTS

Implement practical NLP components.

At minimum:

### Tokenizer

Break Tanese sentences into meaningful tokens.

### Morphological analysis

Identify:

- Root
- Affixes
- Tense
- Aspect
- Person
- Number
- Other grammatical information

### Embeddings

Use sentence/word embeddings for:

- Semantic similarity
- Vocabulary validation
- Retrieval
- Translation support

### Grammar validation

Check whether a Tanese sentence follows the defined grammar.

---

# 8. LLM COMPONENT

Use an existing open-source LLM.

Do NOT train a large language model from scratch.

The LLM should support:

- Tanese sentence generation
- Tanese translation
- Grammar correction
- Vocabulary explanation
- Sentence explanation

Use appropriate fine-tuning/LoRA if practical.

If fine-tuning is not necessary, clearly explain why and use RAG or prompting where appropriate.

---

# 9. RAG SYSTEM

Create a small Tanese knowledge base containing:

- Grammar rules
- Dictionary
- Vocabulary rules
- Example sentences
- Language specification

The LLM should retrieve this information before generating answers.

The goal is to reduce:

- Hallucinations
- Grammar inconsistencies
- Incorrect vocabulary
- Rule violations

---

# 10. TRANSLATION

Support:

### Tamil → Tanese

### Japanese → Tanese

### English → Tanese

And reverse translation where practical.

Do not use simple word substitution.

Preserve the intended meaning and follow Tanese grammar.

---

# 11. TANese AI ASSISTANT

Create a simple interface where users can:

- Enter Tamil
- Enter Japanese
- Enter English
- Translate into Tanese
- Generate Tanese sentences
- Check Tanese grammar
- Explain Tanese vocabulary
- Convert Romanized Tanese to Tanese script

The assistant must rely on the official Tanese specification and dictionary.

---

# 12. EVALUATION

This is essential.

Do not only demonstrate that the system works.

Measure it.

Evaluate:

### Vocabulary generation

- Collision rate
- Validity rate
- Semantic consistency

### Grammar

- Valid sentence accuracy
- Invalid sentence detection
- Grammar correction accuracy

### Translation

Use suitable metrics such as:

- BLEU
- chrF
- BERTScore
- Semantic similarity

Also include a small human evaluation if possible.

### RAG

Measure:

- Retrieval accuracy
- Context relevance
- Answer correctness
- Hallucination rate

---

# 13. WEB APPLICATION

Build a simple, clean web interface.

Suggested sections:

### Translator

Tamil/Japanese/English → Tanese

### Tanese Generator

Generate Tanese sentences.

### Dictionary

Search Tanese vocabulary.

### Grammar Checker

Enter Tanese and receive:

- Correct/incorrect
- Detected issue
- Corrected sentence
- Explanation

### Script Converter

Romanized Tanese ↔ Tanese script.

### AI Assistant

Ask questions about Tanese.

Do not build a huge complicated UI.

Keep it clean and professional.

---

# 14. PROJECT ARCHITECTURE

Use a modular structure similar to:

```text
tanese/
│
├── docs/
│   ├── language-specification.md
│   ├── grammar.md
│   ├── phonology.md
│   ├── script.md
│   └── vocabulary-rules.md
│
├── data/
│   ├── vocabulary/
│   ├── grammar/
│   ├── translations/
│   ├── conversations/
│   └── evaluation/
│
├── tanese_nlp/
│   ├── tokenizer/
│   ├── morphology/
│   ├── embeddings/
│   ├── grammar/
│   ├── vocabulary/
│   └── translation/
│
├── llm/
│   ├── prompts/
│   ├── rag/
│   ├── fine_tuning/
│   └── evaluation/
│
├── backend/
│   └── api/
│
├── frontend/
│
├── tests/
│
├── notebooks/
│
├── requirements.txt
└── README.md
```

Adjust the structure if a better architecture is justified.

---

# 15. DEVELOPMENT ORDER

Do not code everything at once.

Follow this order:

## PHASE 1 — Language specification

Create:

- Language identity
- Tamil/Japanese influence model
- Phonology
- Script
- Romanization
- Grammar
- Syntax
- Morphology
- Tense/aspect/mood
- Pronouns
- Particles
- Politeness
- Vocabulary rules

Deliverable:

**Tanese Language Specification v0.1**

---

## PHASE 2 — Vocabulary

Create:

- Initial root vocabulary
- Word-generation algorithm
- Derivation rules
- Collision detector
- Dictionary

Deliverable:

**Tanese Dictionary v0.1**

---

## PHASE 3 — Corpus

Create:

- Example sentences
- Translation pairs
- Grammar examples
- Incorrect/correct examples
- Small conversations

Deliverable:

**Tanese Corpus v0.1**

---

## PHASE 4 — NLP

Implement:

- Tokenizer
- Morphological analyzer
- Grammar checker
- Embedding system
- Semantic similarity
- Vocabulary validator

Deliverable:

**Tanese NLP Toolkit**

---

## PHASE 5 — LLM

Implement:

- RAG
- Tanese generation
- Translation
- Grammar correction
- Vocabulary explanation

Add fine-tuning/LoRA if useful and technically justified.

Deliverable:

**Tanese LLM System**

---

## PHASE 6 — Web application

Build the simple interface.

Deliverable:

**Tanese Web App**

---

## PHASE 7 — Evaluation

Run experiments and generate:

- Metrics
- Tables
- Error analysis
- Examples
- Limitations
- Conclusions

Deliverable:

**Tanese Evaluation Report**

---

# 16. GITHUB QUALITY

The repository must include:

### README

Explain:

- What Tanese is
- Why it was created
- Problem/idea
- Architecture
- NLP techniques
- LLM techniques
- Example Tanese sentences
- Screenshots
- Results
- Installation
- Usage
- Limitations
- Future work

### Documentation

Clearly document the language specification.

### Tests

Create unit tests for:

- Vocabulary generation
- Collision detection
- Tokenization
- Morphology
- Grammar
- Translation

### Demo

Provide a simple runnable demo.

---

# 17. IMPORTANT LIMITATIONS

This is a student GitHub project.

Do NOT attempt:

- Training a foundation model from scratch
- Massive datasets
- Full production-scale infrastructure
- STT/TTS
- Mobile application
- Unicode standardization
- Complex language-evolution simulation
- Huge learning platform
- Enterprise deployment

These can be listed under **future work** if desired.

---

# 18. FUTURE WORK

After the core project works, possible extensions include:

- Tanese speech recognition
- Tanese text-to-speech
- Mobile keyboard
- Larger corpus
- Better fine-tuned LLM
- Multimodal Tanese model
- Tanese learning application
- Advanced translation
- Language evolution experiments
- Public API
- Community vocabulary contribution
- Larger research benchmark

Do NOT implement these in the first version unless there is a strong reason.

---

# 19. DEVELOPMENT RULE

The project should prioritize:

**Quality > Quantity**

**Consistency > Complexity**

**Understanding > API usage**

**Evaluation > Demo**

**Originality > Feature count**

The final project should demonstrate that the developer understands:

- Classical NLP
- Word representations
- Embeddings
- Transformers
- LLMs
- RAG
- Fine-tuning concepts
- Evaluation
- NLP system design
- Deployment

rather than simply calling an LLM API.

---

# 20. FIRST TASK

For now, DO NOT write application code.

Create **Tanese Language Specification v0.1**.

Start by designing:

1. Language identity
2. Tamil/Japanese influence strategy
3. Phonology
4. New writing system concept
5. Character inventory
6. Romanization
7. Orthography
8. Basic grammar
9. Sentence structure
10. Pronouns
11. Particles
12. Tense/aspect/mood
13. Politeness
14. Vocabulary-generation rules

For every major decision:

- Explain why it was chosen.
- Consider alternatives.
- Identify possible problems.
- Ensure consistency with the rest of the language.

At the end provide:

1. Final Tanese v0.1 specification
2. Design decisions
3. Unresolved decisions
4. Potential problems
5. Recommended corrections
6. Implementation roadmap
7. Future-work ideas

Do NOT begin full implementation until the language specification is internally consistent.

Remember:

**Tanese is a constructed language + NLP/LLM engineering project, not an attempt to build an entire commercial language ecosystem.**