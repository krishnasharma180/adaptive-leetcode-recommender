# 📌 LeetCode Adaptive Recommender System

A personalized recommender system that suggests **what LeetCode problems to solve next** based on a user’s past solve history, topic mastery, and difficulty preference.

Instead of random practice or static sheets, this project generates a **balanced learning set** that adapts to how the user actually progresses.

---

## 🎯 Motivation

Typical LeetCode practice often suffers from:
- random problem selection
- overemphasis on hard problems
- repetition of the same topics
- no personalization based on progress

This project explores a simple idea:

> *Problem recommendations should adapt to the learner, not the other way around.*

---

## 🧠 Core Idea

Each recommendation balances three goals:
- **Reinforcement** of known concepts
- **Progression** at an appropriate difficulty
- **Exploration** of new topics in a controlled way

The system uses:
- past solve history
- topic-level mastery with time decay
- soft difficulty preferences
- controlled randomness to avoid stagnation

---

## 🗂️ Data

- **progress.csv**  
  User’s solved/attempted problems (difficulty, submissions, timestamps, topic tags)

- **questions.csv**  
  Full LeetCode problem set (difficulty, topic tags, status)

> LeetCode topic tags are noisy and often over-inclusive.  
> This system explicitly accounts for that.

---

## ⚙️ System Design

### 1. Topic Mastery Modeling
- Each solved problem contributes to topic mastery
- Weighted by:
  - difficulty
  - number of submissions
  - **time decay** (recent activity matters more)

---

### 2. Core Topic Filtering
To reduce noise from over-tagged problems:
- Only the **top 40% strongest topics** (by mastery score) are treated as core
- All recommendation logic is based on these trusted topics

---

### 3. Candidate Generation
From all unsolved problems:
- Require overlap with at least one core topic
- Track:
  - overlap with known topics
  - number of unseen topics

---

### 4. Novelty Buckets

| Bucket   | Meaning |
|--------|--------|
| safe   | No new topics |
| stretch | One new topic |
| explore | Multiple new topics |

---

### 5. Difficulty Handling
- Difficulty is treated as a **soft preference**, not a hard filter
- Medium difficulty is preferred
- Easy problems reinforce fundamentals
- Hard problems appear occasionally

---

### 6. Scoring
Each candidate problem is scored as:

 final_score =topic_relevance × difficulty_weight − novelty_penalty


---

### 7. Session Construction
A learning session:
- samples difficulty preferences probabilistically
- enforces topic intent (safe / stretch / explore)
- ranks candidates by score
- avoids duplicates

The result is a **balanced 5-problem learning set**.

---

## 📌 Takeaway

This project shows that **careful system design and clean abstractions** can enable meaningful personalization — even without heavy machine learning.

The hardest part was not modeling, but deciding **which signals to trust and which to ignore**.

