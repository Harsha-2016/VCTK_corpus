# Sentence Type Annotation Guidelines for VCTK Corpus

## Overview

This document provides detailed annotation rules for classifying sentences into four types:
1. **Declarative** - statements and facts
2. **Interrogative** - questions
3. **Imperative** - commands and requests
4. **Exclamatory** - expressions of strong emotion/emphasis

These guidelines are designed for speech corpus annotation, balancing linguistic theory with practical heuristics for automated candidate generation.

---

## 1. DECLARATIVE SENTENCES

### Definition
A declarative sentence makes a **statement** that conveys information, facts, descriptions, opinions, or reports. It typically expresses a complete thought that can be true or false.

### Core Characteristics

| Aspect | Details |
|--------|---------|
| **Function** | Inform, state, assert, describe |
| **Typical Word Order** | Subject + Verb + Object/Complement |
| **Punctuation** | Period (.) or sometimes no punctuation in transcripts |
| **Intonation Pattern** | Falling intonation (in speech) |
| **Example** | "The weather is nice today." |

### Annotation Rules

**Rule D1**: If a sentence does **not clearly**:
- End with `?` (making it interrogative)
- Issue a command or request (making it imperative)
- Express strong emotion or emphasis (making it exclamatory)

Then label it as **Declarative** (fallback class).

**Rule D2**: Typical declarative structure in English:

```
Subject + Predicate
"She loves music."           ✓ Declarative
"The sun rises in the east." ✓ Declarative
```

**Rule D3**: Even statements containing emotional words can be declarative if they primarily state facts without strong emotion markers (no `!`, no interjections):

```
"This is a terrible situation."  ✓ Declarative (states a negative fact)
"I don't like that movie."      ✓ Declarative (states opinion as fact)
```

**Rule D4**: If a sentence has embedded clauses or complex structure, it remains declarative if the overall function is informative:

```
"The book that she gave me is wonderful." ✓ Declarative
"Although I was tired, I finished the project." ✓ Declarative
```

### Heuristics Used in Automated Detection

- ✓ No `?` at end
- ✓ No `!` at end (unless also imperative)
- ✓ No interjection at start
- ✓ Starts with subject or adverbial phrase (not base verb)
- ✓ Does not match exclamatory patterns (e.g., "What a...", "How...")

### References

- Grammarist - Declarative, imperative, exclamatory and interrogative sentences
- Study.com - How to Identify Declarative, Interrogative, Imperative & Exclamatory Sentences

---

## 2. INTERROGATIVE SENTENCES

### Definition
An interrogative sentence is a **question** that seeks information, clarification, confirmation, or elicits a response from the listener. It is fundamentally a request for information.

### Core Characteristics

| Aspect | Details |
|--------|---------|
| **Function** | Ask, request information, confirm, challenge |
| **Typical Structure** | Wh- words at start OR Auxiliary verb + Subject |
| **Punctuation** | Question mark (?) |
| **Intonation Pattern** | Rising intonation (in speech) for yes/no questions; varied for wh- questions |
| **Example** | "What time is it?" "Do you like pizza?" |

### Annotation Rules

**Rule I1**: A sentence is **Interrogative** if:
- It ends with `?` **AND**
- It is syntactically/pragmatically a genuine question or request for information

```
"What is your name?"              ✓ Interrogative
"Did you finish your homework?"   ✓ Interrogative
"Isn't this amazing?"             ✓ Interrogative (rhetorical, but form-based = Interrogative)
```

**Rule I2**: Wh-words typically signal interrogative sentences:

```
Wh-words: who, what, when, where, why, how, which, whose

"Who is coming to the party?"    ✓ Interrogative
"When will you arrive?"          ✓ Interrogative
"How did you solve this?"        ✓ Interrogative
```

**Rule I3**: Yes/No questions often start with auxiliaries or modals:

```
Auxiliaries/Modals: Do, Did, Does, Is, Are, Have, Has, Had, Can, Could, Will, Would, Should, Must, May, Might

"Do you like coffee?"           ✓ Interrogative
"Are you coming tomorrow?"      ✓ Interrogative
"Can you help me?"              ✓ Interrogative
```

**Rule I4**: Polite requests phrased as questions are still **Interrogative** by form (priority: form > function in this annotation scheme):

```
"Could you pass the salt?"       ✓ Interrogative (pragmatically imperative, formally interrogative)
"Would you mind closing the door?" ✓ Interrogative
```

**Rule I5**: Tag questions end with interrogative tags and are **Interrogative**:

```
"You're coming, aren't you?"     ✓ Interrogative
"She doesn't like it, does she?" ✓ Interrogative
```

### Heuristics Used in Automated Detection

- ✓ Ends with `?`
- ✓ Starts with wh-word: what, why, how, when, where, who, whom, which, whose
- ✓ Starts with auxiliary: do, does, did, is, are, have, has, had, can, could, will, would, should, must, may, might
- ✓ Does not start with imperative verb
- ✓ Does not match exclamatory patterns

### References

- Grammarist - Interrogative sentences
- Study.com - Interrogative sentence identification
- Standard grammatical theory (Austin, 1962; Searle, 1969)

---

## 3. IMPERATIVE SENTENCES

### Definition
An imperative sentence **issues a command, request, instruction, prohibition, or permission**. It uses the verb in the imperative mood, typically with an implied subject "you".

### Core Characteristics

| Aspect | Details |
|--------|---------|
| **Function** | Command, request, instruct, prohibit, permit, invite |
| **Verb Form** | Base form (infinitive without "to"), often implied subject "you" |
| **Typical Structure** | (Optionally: "Please" +) Base Verb + Object/Complement |
| **Punctuation** | Period (.) or Exclamation mark (!) |
| **Intonation Pattern** | Falling or emphatic (depends on force) |
| **Example** | "Close the door." "Please sit down." |

### Annotation Rules

**Rule Im1**: A sentence is **Imperative** if it **primarily issues a command, request, or instruction**, even if it contains emotion markers:

```
"Close the door."               ✓ Imperative
"Please sit down."              ✓ Imperative
"Let's start now."              ✓ Imperative (inclusive command)
"Stop it right now!"            ✓ Imperative (with emphasis/emotion)
```

**Rule Im2**: Imperative sentences often lack an overt subject (implied "you"):

```
"Take this."                    ✓ Imperative (implied: You take this)
"Listen carefully."             ✓ Imperative (implied: You listen)
"Give me the book."             ✓ Imperative (implied: You give)
```

**Rule Im3**: Common imperative starters (base verbs):

```
Imperative verbs: take, give, go, come, listen, look, watch, tell, say, do, make, let, open, close, 
sit, stand, write, read, check, hold, turn, move, run, walk, stop, wait, get, put, keep, try, call, 
pay, mind, remember, forget, think, see, hear...

"Take your shoes off."          ✓ Imperative
"Go to bed now."                ✓ Imperative
"Listen to me."                 ✓ Imperative
```

**Rule Im4**: "Please" + Verb pattern signals imperative:

```
"Please close the window."      ✓ Imperative
"Please tell me your name."     ✓ Imperative
```

**Rule Im5**: "Let's" and "Let us" constructions are **Imperative** (inclusive commands):

```
"Let's go to the beach."        ✓ Imperative
"Let us begin."                 ✓ Imperative
```

**Rule Im6**: Negative imperatives (prohibition) with "Don't" or "Do not":

```
"Don't be late."                ✓ Imperative
"Do not touch that."            ✓ Imperative
```

**Rule Im7**: Even with `!` or strong tone, if the primary function is commanding/requesting, it is **Imperative**:

```
"Stop it right now!"            ✓ Imperative (not exclamatory, despite !)
"Sit down immediately!"         ✓ Imperative
```

### Heuristics Used in Automated Detection

- ✓ No `?` at end
- ✓ Starts with a base-form verb or "please" or "let"
- ✓ Does NOT start with subject pronoun (I, you, he, she, it, we, they) or determiner (the, a, this, that)
- ✓ Does NOT start with wh-word or auxiliary (marking questions)
- ✓ Relatively short utterance (imperative commands tend to be concise)
- ✓ Matches verb list: [take, give, go, come, listen, look, watch, tell, say, do, make, let, open, close, sit, stand, write, read, check, hold, turn, move, run, walk, stop, wait, get, put, keep, try, call, pay, mind, ...]

### References

- Magoosh - What is an Imperative Sentence?
- BYJU'S - Definition of an Imperative Sentence
- Study.com - Imperative sentence identification
- Standard grammatical theory (Quirk et al., 1985; Crystal, 2008)

---

## 4. EXCLAMATORY SENTENCES

### Definition
An exclamatory sentence **expresses strong emotion, emphasis, surprise, excitement, anger, joy, dismay, or other intense feeling**. It conveys information with heightened emotional content and typically ends with an exclamation mark.

### Core Characteristics

| Aspect | Details |
|--------|---------|
| **Function** | Express emotion, surprise, emphasis, intensity |
| **Typical Structure** | Often: Wh- noun phrase ("What a...!", "How...!") OR subject + emotional verb phrase |
| **Punctuation** | Exclamation mark (!) is hallmark; sometimes period (.) if emotion is clear |
| **Intonation Pattern** | Emphatic, higher pitch, possibly longer duration |
| **Emotion Markers** | Interjections, intensifiers (so, very, really), strong adjectives |
| **Example** | "What a beautiful day!" "I can't believe it!" |

### Annotation Rules

**Rule E1**: A sentence is clearly **Exclamatory** if it **ends with `!`** and the content expresses emotion or emphasis (not a command):

```
"What a mess!"                  ✓ Exclamatory
"This is amazing!"              ✓ Exclamatory
"She's a spy!"                  ✓ Exclamatory
```

**Rule E2**: Wh-exclamative constructions (Wh-noun phrases) express emotion and are **Exclamatory**:

```
"What a day!"                   ✓ Exclamatory
"What a wonderful idea!"        ✓ Exclamatory
"What an incredible achievement!" ✓ Exclamatory
"How beautiful this is!"        ✓ Exclamatory
"How awful!"                    ✓ Exclamatory
```

**Rule E3**: Sentences starting with interjections (expressing strong feeling) are **Exclamatory**:

```
Interjections: oh, wow, hey, ah, ouch, alas, bravo, hurray, oops, gosh, goodness, gee, aha, yikes

"Oh no!"                        ✓ Exclamatory
"Wow, that's incredible!"       ✓ Exclamatory
"Hey, watch out!"               ✓ Exclamatory
"Ouch, that hurt!"              ✓ Exclamatory
```

**Rule E4**: Sentences with intensifiers (so, very, really, too, quite, extremely, etc.) + strong emotional adjectives are **Exclamatory**:

```
Intensifiers: so, very, really, too, quite, extremely, totally, absolutely
Emotion adjectives: beautiful, wonderful, terrible, awful, amazing, horrible, fantastic, great, 
incredible, lovely, marvelous, magnificent, dreadful, splendid, brilliant, ridiculous, crazy, insane

"This is so beautiful!"         ✓ Exclamatory
"It's very wonderful!"          ✓ Exclamatory
"That's really amazing!"        ✓ Exclamatory
"She's incredibly talented!"    ✓ Exclamatory
```

**Rule E5**: Strong emotion expressions, even without `!`, can be **Exclamatory** if:
- Pragmatically the speaker is expressing strong feeling
- Context suggests emphasis or emotional load

```
"I can't believe she has been admonished." ✓ Exclamatory (emotional emphasis)
"This is such a beautiful city." ✓ Exclamatory (emphasis on beauty)
```

**Rule E6**: Distinguish exclamatory from imperative:
- If the sentence primarily **commands** (even with `!`), it is **Imperative**.
- If the sentence primarily **expresses emotion**, it is **Exclamatory**.

```
"Stop it right now!"            ✓ Imperative (primary: command)
"What an achievement!"          ✓ Exclamatory (primary: emotion)
```

### Heuristics Used in Automated Detection

**High Confidence (Exclamatory):**
- ✓ Ends with `!`
- ✓ Starts with "What a", "What an", "How" (wh-exclamatives)
- ✓ Starts with interjection (oh, wow, hey, ah, ouch, alas, etc.) + ends with `.` or `!`
- ✓ Contains explicit strong phrases: "I can't believe", "I cannot believe", "This is amazing", "this is terrible"

**Medium Confidence (Exclamatory):**
- ✓ Starts with "What" or "How" but ends with `.` (not `?`), suggesting emphasis rather than genuine question
- ✓ Contains intensifier + emotional adjective (e.g., "so beautiful", "very amazing")

**Low Confidence (Exclamatory):**
- ✓ Contains interjection anywhere in utterance
- ✓ Contains repeated punctuation like `!!`, `?!`, `!?`

### References

- Fiveable - Exclamatory sentence Definition
- BYJU'S - Definition of an Exclamatory Sentence
- Study.com - Exclamatory Sentence Definition, Uses & Examples
- Grammarist - Exclamatory sentences
- Study.com - Exclamatory sentence identification
- Linguistic theory: Huddleston & Pullum (2002); Quirk et al. (1985)

---

## 5. PRIORITY RULES FOR AMBIGUOUS CASES

When a sentence could fit multiple categories, apply these rules in order:

### Priority Decision Tree

```
┌─ Does the sentence end with '?' ?
│  └─ YES → INTERROGATIVE (highest priority)
│  └─ NO → Continue
│
├─ Does the sentence primarily issue a command/request?
│  └─ YES → IMPERATIVE
│  └─ NO → Continue
│
├─ Does the sentence primarily express strong emotion/emphasis?
│  ├─ YES (has ! or exclamative patterns or interjection) → EXCLAMATORY
│  └─ NO → Continue
│
└─ Otherwise → DECLARATIVE (default fallback)
```

### Example Ambiguities Resolved

| Sentence | Ambiguity | Resolution | Label |
|----------|-----------|-----------|-------|
| "Stop it right now!" | Command + emotion | Rule: Commands take priority over emotion. | **Imperative** |
| "Isn't this amazing?" | Question + emotion | Rule: `?` takes priority | **Interrogative** |
| "Could you close the door?" | Question + request | Rule: `?` takes priority (form-based) | **Interrogative** |
| "What a terrible mess!" | Emotion + wh-structure | Rule: Primary function is emotion expression | **Exclamatory** |
| "Really, you will!" | Emphatic + emotion | Rule: Not a command, not a question. Emotion expressed. | **Exclamatory** |
| "There was no need for such a hostel." | Emphatic + statement | Rule: Primarily a statement despite intensity | **Declarative** OR **Exclamatory** (depends on emphasis) |

---


## 7. REFERENCES AND SOURCES

### Academic & Linguistic References

[1] Austin, J. L. (1962). *How to do things with words*. Oxford University Press.

[2] Searle, J. R. (1969). *Speech acts: An essay in the philosophy of language*. Cambridge University Press.

[3] Quirk, R., Greenbaum, S., Leech, G., & Svartvik, J. (1985). *A comprehensive grammar of the English language*. Longman.

[4] Huddleston, R., & Pullum, G. K. (2002). *The Cambridge grammar of the English language*. Cambridge University Press.

[5] Crystal, D. (2008). *A dictionary of linguistics and phonetics* (6th ed.). Blackwell Publishers.

### Web References

- Fiveable - Exclamatory sentence Definition - Intro to Linguistics Key Terms
- BYJU'S - Definition of an Exclamatory Sentence
- Study.com - Exclamatory Sentence Definition, Uses & Examples
- Magoosh - What is an Imperative Sentence? Definition, Examples, & Exercises
- BYJU'S - Definition of an Imperative Sentence
- Grammarist - Declarative, imperative, exclamatory and interrogative sentences Grammar & Punctuation Rules
- Study.com - How to Identify Declarative, Interrogative, Imperative & Exclamatory Sentences
- Kaggle - VCTK Corpus

### Corpus References

VCTK Corpus: Yamagishi, J., Veaux, C., & King, S. (2016). The CSTR VCTK Corpus of English Talkers. 
University of Edinburgh. https://datashare.is.ed.ac.uk/handle/10283/2651

---

## 8. QUICK REFERENCE TABLE

| Aspect | Declarative | Interrogative | Imperative | Exclamatory |
|--------|-------------|---------------|-----------|------------|
| **Function** | Inform, state, describe | Ask, request info | Command, request action | Express emotion, emphasis |
| **Typical Ending** | `.` or no mark | `?` | `.` or `!` | `!` (sometimes `.`) |
| **Structure** | Subject + Verb + Object | Wh-word/Aux + Subject... | (Please +) Verb + Object | Wh-phrase OR interjection OR emotional phrase |
| **Example** | "The sky is blue." | "What time is it?" | "Close the door." | "What a beautiful day!" |
| **Priority** | 4 (fallback) | 1 (highest if `?`) | 2 (command > emotion) | 3 (emotion > statement) |
| **Confidence Markers** | No `?`, no `!`, subject-first | Ends with `?` | Base verb start, "please" | Ends with `!`, interjections, "What a..." |

---

**Document Version**: 1.0  
**Last Updated**: February 22, 2026  
**For**: VCTK Corpus Sentence Type Annotation Project
