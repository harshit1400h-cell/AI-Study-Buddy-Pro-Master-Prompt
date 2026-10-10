import os
import re
import json
import random
from typing import List, Dict, Any, Optional
from app.config import settings

class AIService:
    @classmethod
    def get_active_provider(cls) -> str:
        s = settings
        if s.provider == "gemini" and s.gemini_api_key.strip():
            return "gemini"
        elif s.provider == "openai" and s.openai_api_key.strip():
            return "openai"
        return "smart_local"

    # =========================================================================
    # 1. TUTOR CHAT COMPLETION
    # =========================================================================
    @classmethod
    async def chat(
        cls, 
        message: str, 
        context_chunks: List[Dict[str, Any]], 
        persona: str = "academic",
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        provider = cls.get_active_provider()
        
        # Build context string & citations
        context_text = ""
        citations = []
        for idx, chunk in enumerate(context_chunks):
            page = chunk.get("page_number", 1)
            snippet = chunk.get("text", "")
            context_text += f"\n--- Source {idx+1} [Page {page}] ---\n{snippet}\n"
            citations.append({
                "source_id": idx + 1,
                "page": page,
                "snippet": snippet[:200] + "..."
            })

        system_prompts = {
            "academic": (
                "You are AI Study Buddy Pro in Academic Professor Mode. Provide thorough, scholarly, "
                "well-structured explanations using markdown headings, bullet points, and precise terminology. "
                "Explicitly cite the source page numbers (e.g. [Page X]) when referencing facts."
            ),
            "socratic": (
                "You are AI Study Buddy Pro in Socratic Guide Mode. Do not simply hand over the full answer. "
                "Guide the student through thoughtful questions, analogies, and step-by-step hints to help them discover "
                "the answer themselves. Be encouraging and curious."
            ),
            "simplifier": (
                "You are AI Study Buddy Pro in ELI5 (Explain Like I'm 5) Mode. Break down complex, technical ideas "
                "into delightfully simple language, vivid real-world analogies, and friendly bite-sized summaries. "
                "Avoid overwhelming academic jargon."
            ),
            "exam_coach": (
                "You are AI Study Buddy Pro in Exam Coach Mode. Your goal is high-yield exam readiness! "
                "Highlight common exam pitfalls, tricky test questions, key mnemonics, and high-probability topics. "
                "End your answer with a quick 1-question rapid-fire test for the student!"
            )
        }
        sys_prompt = system_prompts.get(persona, system_prompts["academic"])

        # Try Cloud Providers first if configured
        if provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel(settings.gemini_model or "gemini-1.5-flash")
                
                prompt = (
                    f"{sys_prompt}\n\n"
                    f"STUDY CONTEXT:\n{context_text}\n\n"
                    f"STUDENT QUESTION:\n{message}\n\n"
                    f"Provide an insightful, helpful response adhering strictly to your tutor persona. "
                    f"Always reference the relevant page numbers from the study context."
                )
                response = model.generate_content(prompt)
                return {
                    "reply": response.text,
                    "citations": citations,
                    "provider": "Google Gemini"
                }
            except Exception as e:
                # Fallback to local if Gemini error
                print(f"Gemini API error, using local fallback: {e}")

        elif provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.openai_api_key)
                messages = [{"role": "system", "content": f"{sys_prompt}\n\nStudy Context:\n{context_text}"}]
                if history:
                    for h in history[-4:]:
                        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
                messages.append({"role": "user", "content": message})

                res = client.chat.completions.create(
                    model=settings.openai_model or "gpt-4o-mini",
                    messages=messages,
                    temperature=0.7
                )
                return {
                    "reply": res.choices[0].message.content,
                    "citations": citations,
                    "provider": "OpenAI GPT"
                }
            except Exception as e:
                print(f"OpenAI API error, using local fallback: {e}")

        # Smart Local Pedagogical AI Engine
        return cls._local_tutor_reply(message, context_chunks, persona, citations)

    @classmethod
    def _local_tutor_reply(
        cls, 
        message: str, 
        context_chunks: List[Dict[str, Any]], 
        persona: str, 
        citations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """High-quality pedagogical local synthesis grounded in retrieved chunks."""
        q_clean = message.lower().strip()
        matched_sentences = []
        key_topics = set()

        for c in context_chunks:
            page = c.get("page_number", 1)
            raw_text = c.get("text", "")
            # split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', raw_text)
            for s in sentences:
                s_strip = s.strip()
                if len(s_strip) > 25:
                    # check overlap with query words
                    words = [w for w in re.findall(r'\b\w{3,}\b', q_clean) if w not in {'what', 'when', 'where', 'which', 'explain', 'describe', 'tell', 'about'}]
                    overlap = sum(1 for w in words if w in s_strip.lower())
                    if overlap > 0:
                        matched_sentences.append((overlap, page, s_strip))
                        # extract potential key noun phrases
                        for match in re.findall(r'\b[A-Z][a-zA-Z0-9_\-]{2,}\b', s_strip):
                            key_topics.add(match)

        matched_sentences.sort(key=lambda x: x[0], reverse=True)
        top_facts = matched_sentences[:5]

        # Structure response based on Persona
        if persona == "socratic":
            reply = f"### 💡 Guiding Question\n\n"
            reply += f"Let's explore your question: *\"{message}\"*\n\n"
            if top_facts:
                page = top_facts[0][1]
                fact = top_facts[0][2]
                reply += f"Consider what our study text mentions on **Page {page}**:\n"
                reply += f"> *\"{fact}\"*\n\n"
                reply += f"**Now, ask yourself:**\n"
                reply += f"1. Why do you think this relationship holds true in this system?\n"
                reply += f"2. If you had to connect this principle to a real-world scenario, how would it behave under stress or change?\n\n"
                reply += f"*Give me your initial thought, and we will build the answer together!*"
            else:
                reply += "Take a look at the foundational concepts in this document. What is the main objective or definition introduced first? What do you already understand about this topic?"

        elif persona == "simplifier":
            reply = f"### 🎈 Let's Break It Down (ELI5)\n\n"
            reply += f"Think of this like an everyday puzzle! Here is the simple story:\n\n"
            if top_facts:
                for idx, (_, page, fact) in enumerate(top_facts[:3]):
                    reply += f"- **Part {idx+1}**: {fact} *(Source: [Page {page}])* \n"
                reply += f"\n**In everyday words:**\n"
                reply += f"It's like a team of specialized workers where each part has one job. When they communicate smoothly, the entire system reaches its goal with high efficiency!\n"
            else:
                reply += "This concept works just like a recipe: you need the right ingredients (inputs), follow specific rules (processes), and produce an expected result (output)!"

        elif persona == "exam_coach":
            reply = f"### 🎯 High-Yield Exam Breakdown\n\n"
            reply += f"**Topic Focus:** *{message}*\n\n"
            reply += f"#### ⚠️ Critical Exam Points:\n"
            if top_facts:
                for _, page, fact in top_facts[:3]:
                    reply += f"- **High-Probability Concept ([Page {page}]):** {fact}\n"
            else:
                reply += "- Make sure you know the core definitions and formulas from the first two sections.\n"
            
            reply += f"\n#### ⚡ Common Pitfalls & Traps:\n"
            reply += f"- Examiners love testing edge cases and asking whether this rule applies unconditionally.\n"
            reply += f"- Watch out for confusing similar acronyms and overlapping terminology.\n\n"
            reply += f"#### 🧪 Rapid-Fire Recall Check:\n"
            reply += f"*Can you explain this concept back to me in 2 sentences without checking your notes?*"

        else: # Academic
            reply = f"### 📖 Academic Overview: {message}\n\n"
            if top_facts:
                reply += f"Based on the course materials, here is the detailed theoretical synthesis:\n\n"
                for _, page, fact in top_facts:
                    reply += f"- {fact} **[Page {page}]**\n"
                reply += f"\n#### 📌 Key Takeaway & Analysis\n"
                reply += f"The primary theoretical mechanism relies on the interplay between the foundational definitions and their operational parameters described in the text.\n"
            else:
                reply += f"Here is an analysis based on the uploaded document structure:\n"
                if context_chunks:
                    snippet = context_chunks[0]['text'][:300]
                    page = context_chunks[0].get('page_number', 1)
                    reply += f"From **Page {page}**:\n> {snippet}...\n\n"
                    reply += "This establishes the core domain principles for your inquiry."
                else:
                    reply += "Please select or upload a document to review specific references and detailed citations."

        return {
            "reply": reply,
            "citations": citations,
            "provider": "AI Study Buddy Smart Local Engine"
        }

    # =========================================================================
    # 2. EXECUTIVE SUMMARY & MIND MAP
    # =========================================================================
    @classmethod
    async def generate_summary(cls, document_text: str, document_title: str = "Document") -> Dict[str, Any]:
        provider = cls.get_active_provider()
        
        # Sample document snippet if too long
        doc_sample = document_text[:8000]

        if provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel(settings.gemini_model or "gemini-1.5-flash")
                prompt = f"""Analyze the following study material and generate a comprehensive study guide in JSON format.
Return ONLY valid JSON matching this exact structure:
{{
  "title": "{document_title}",
  "tldr": "2-3 sentence high-level summary",
  "key_takeaways": ["takeaway 1", "takeaway 2", "takeaway 3", "takeaway 4"],
  "cheat_sheet": ["bullet 1", "bullet 2", "bullet 3", "bullet 4", "bullet 5"],
  "glossary": [
    {{"term": "Term 1", "definition": "Clear concise definition"}},
    {{"term": "Term 2", "definition": "Clear concise definition"}}
  ],
  "mind_map": [
    {{"id": "root", "label": "Main Topic", "parent": null}},
    {{"id": "node1", "label": "Subtopic A", "parent": "root"}},
    {{"id": "node2", "label": "Key Concept 1", "parent": "node1"}},
    {{"id": "node3", "label": "Subtopic B", "parent": "root"}}
  ]
}}

DOCUMENT TEXT:
{doc_sample}
"""
                resp = model.generate_content(prompt)
                cleaned_json = cls._extract_json(resp.text)
                if cleaned_json:
                    return cleaned_json
            except Exception as e:
                print(f"Gemini summary generation error: {e}")

        elif provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.openai_api_key)
                prompt = f"Analyze this study material and return a JSON study guide with tldr, key_takeaways (list), cheat_sheet (list), glossary (list of term/definition dicts), and mind_map (list of id, label, parent dicts).\n\nText:\n{doc_sample}"
                res = client.chat.completions.create(
                    model=settings.openai_model or "gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert curriculum designer. Return strictly valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"} if "gpt-4" in (settings.openai_model or "") else None
                )
                cleaned_json = cls._extract_json(res.choices[0].message.content)
                if cleaned_json:
                    return cleaned_json
            except Exception as e:
                print(f"OpenAI summary generation error: {e}")

        # Local NLP Summarizer
        return cls._local_summary(document_text, document_title)

    @classmethod
    def _local_summary(cls, text: str, title: str) -> Dict[str, Any]:
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 40]
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 30]

        # Extract definitions (regex patterns like "X is defined as Y", "X refers to Y", "X: Y")
        glossary = []
        term_matches = re.findall(r'([A-Z][a-zA-Z0-9\s]{2,25})\s+(?:is defined as|refers to|is a|means|can be described as)\s+([^.]{20,150}\.)', text)
        for term, definition in term_matches[:8]:
            term_clean = term.strip()
            if len(term_clean.split()) <= 4 and term_clean.lower() not in {"this", "it", "there"}:
                glossary.append({"term": term_clean, "definition": definition.strip()})

        # If few definitions found, find colon lines
        if len(glossary) < 3:
            colon_matches = re.findall(r'([A-Z][a-zA-Z\s]{2,25}):\s*([^.\n]{20,150})', text)
            for term, definition in colon_matches[:6]:
                glossary.append({"term": term.strip(), "definition": definition.strip()})

        # Fallback glossary items if text had unusual format
        if not glossary:
            glossary = [
                {"term": "Core Principle", "definition": "The foundational premise established in the introduction."},
                {"term": "Operational Mechanism", "definition": "The systematic workflow and processes detailed in the text."},
                {"term": "Key Variable", "definition": "A critical metric or parameter influencing overall outcomes."}
            ]

        # TL;DR from top 2 introductory sentences
        tldr = " ".join(sentences[:2]) if len(sentences) >= 2 else f"Essential concepts and learning takeaways for {title}."
        
        # Key takeaways
        takeaways = []
        for s in sentences[2:15]:
            if any(k in s.lower() for k in ["important", "primary", "key", "main", "result", "essential", "crucial", "therefore"]):
                takeaways.append(s)
            if len(takeaways) >= 4:
                break
        if len(takeaways) < 4:
            takeaways.extend(sentences[2:2 + (4 - len(takeaways))])

        # Cheat sheet
        cheat_sheet = [
            f"Review main definitions: {', '.join([g['term'] for g in glossary[:4]])}",
            "Focus on sequential relationships and causal mechanisms.",
            "Verify all edge cases and boundary conditions highlighted in the notes.",
            "Practice recalling definitions without looking at flashcard answers.",
            "Test your active recall with the adaptive quiz module."
        ]

        # Mind map nodes
        root_label = title.replace(".pdf", "").replace(".txt", "")[:30]
        mind_map = [
            {"id": "root", "label": root_label, "parent": None}
        ]
        
        subtopics = [g['term'] for g in glossary[:4]]
        if not subtopics:
            subtopics = ["Foundations", "Core Processes", "Advanced Applications", "Key Findings"]

        for idx, sub in enumerate(subtopics):
            node_id = f"sub_{idx+1}"
            mind_map.append({"id": node_id, "label": sub, "parent": "root"})
            mind_map.append({"id": f"{node_id}_detail", "label": f"{sub} Rules", "parent": node_id})

        return {
            "title": title,
            "tldr": tldr,
            "key_takeaways": takeaways[:5],
            "cheat_sheet": cheat_sheet,
            "glossary": glossary[:8],
            "mind_map": mind_map
        }

    # =========================================================================
    # 3. SMART FLASHCARDS GENERATION
    # =========================================================================
    @classmethod
    async def generate_flashcards(cls, document_text: str, deck_title: str = "General", count: int = 8) -> List[Dict[str, Any]]:
        provider = cls.get_active_provider()
        doc_sample = document_text[:7000]

        if provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel(settings.gemini_model or "gemini-1.5-flash")
                prompt = f"""Generate {count} high-yield flashcards for students from this study material.
Return strictly a JSON array of objects with keys:
- front: question, prompt, or term to define
- back: clear, high-yield explanation or answer
- difficulty: "easy", "medium", or "hard"

DOCUMENT:
{doc_sample}
"""
                resp = model.generate_content(prompt)
                cards = cls._extract_json(resp.text)
                if isinstance(cards, list) and len(cards) > 0:
                    for c in cards:
                        c["deck_title"] = deck_title
                    return cards
            except Exception as e:
                print(f"Gemini flashcard generation error: {e}")

        elif provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.openai_api_key)
                prompt = f"Generate {count} flashcards from this text as a JSON array of objects with front, back, difficulty ('easy'|'medium'|'hard').\n\nText:\n{doc_sample}"
                res = client.chat.completions.create(
                    model=settings.openai_model or "gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert tutor. Return strictly a JSON array."},
                        {"role": "user", "content": prompt}
                    ]
                )
                cards = cls._extract_json(res.choices[0].message.content)
                if isinstance(cards, list) and len(cards) > 0:
                    for c in cards:
                        c["deck_title"] = deck_title
                    return cards
            except Exception as e:
                print(f"OpenAI flashcard generation error: {e}")

        # Local NLP Flashcard Generator
        return cls._local_flashcards(document_text, deck_title, count)

    @classmethod
    def _local_flashcards(cls, text: str, deck_title: str, count: int) -> List[Dict[str, Any]]:
        cards = []
        # Pattern 1: Definitions
        term_matches = re.findall(r'([A-Z][a-zA-Z0-9\s]{2,25})\s+(?:is defined as|refers to|is a|means)\s+([^.]{20,200}\.)', text)
        for term, definition in term_matches:
            clean_term = term.strip()
            if len(clean_term.split()) <= 4 and clean_term.lower() not in {"this", "it", "there"}:
                cards.append({
                    "deck_title": deck_title,
                    "front": f"What is {clean_term}?",
                    "back": definition.strip(),
                    "difficulty": "medium"
                })

        # Pattern 2: Colon structures
        colon_matches = re.findall(r'([A-Z][a-zA-Z\s]{2,25}):\s*([^.\n]{20,200})', text)
        for term, definition in colon_matches:
            cards.append({
                "deck_title": deck_title,
                "front": f"Define and describe: {term.strip()}",
                "back": definition.strip(),
                "difficulty": "easy"
            })

        # Pattern 3: Important sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 40]
        for s in sentences:
            if "because" in s.lower() or "leads to" in s.lower() or "due to" in s.lower():
                cards.append({
                    "deck_title": deck_title,
                    "front": f"Why is this significant: \"{s[:70]}...\"?",
                    "back": s,
                    "difficulty": "hard"
                })

        if not cards:
            cards = [
                {
                    "deck_title": deck_title,
                    "front": "What is the primary topic of this study material?",
                    "back": f"The core focus is understanding key principles outlined in {deck_title}.",
                    "difficulty": "easy"
                },
                {
                    "deck_title": deck_title,
                    "front": "How do the fundamental components interact with each other?",
                    "back": "Components operate sequentially, feeding outputs from initial phases into downstream tasks.",
                    "difficulty": "medium"
                }
            ]

        # Deduplicate and return requested count
        seen = set()
        unique_cards = []
        for c in cards:
            if c["front"] not in seen:
                seen.add(c["front"])
                unique_cards.append(c)
        return unique_cards[:count]

    # =========================================================================
    # 4. ADAPTIVE QUIZ GENERATION
    # =========================================================================
    @classmethod
    async def generate_quiz(
        cls, 
        document_text: str, 
        title: str = "Knowledge Check", 
        num_questions: int = 5, 
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        provider = cls.get_active_provider()
        doc_sample = document_text[:7000]

        if provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel(settings.gemini_model or "gemini-1.5-flash")
                prompt = f"""Generate a high-yield adaptive quiz with {num_questions} multiple choice questions (difficulty: {difficulty}) based on this study material.
Return strictly a JSON object:
{{
  "title": "{title}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "id": 1,
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Exact matching string from options",
      "explanation": "Detailed explanation of why this is correct and why other choices are wrong."
    }}
  ]
}}

STUDY TEXT:
{doc_sample}
"""
                resp = model.generate_content(prompt)
                quiz = cls._extract_json(resp.text)
                if isinstance(quiz, dict) and "questions" in quiz:
                    return quiz
            except Exception as e:
                print(f"Gemini quiz generation error: {e}")

        elif provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.openai_api_key)
                prompt = f"Generate {num_questions} multiple choice questions (difficulty: {difficulty}) from this text. Return strictly a JSON object with title, difficulty, and questions list (each with id, question, options, correct_answer, explanation).\n\nText:\n{doc_sample}"
                res = client.chat.completions.create(
                    model=settings.openai_model or "gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert test creator. Return strictly JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"} if "gpt-4" in (settings.openai_model or "") else None
                )
                quiz = cls._extract_json(res.choices[0].message.content)
                if isinstance(quiz, dict) and "questions" in quiz:
                    return quiz
            except Exception as e:
                print(f"OpenAI quiz generation error: {e}")

        # Local NLP Quiz Generator
        return cls._local_quiz(document_text, title, num_questions, difficulty)

    @classmethod
    def _local_quiz(cls, text: str, title: str, num_questions: int, difficulty: str) -> Dict[str, Any]:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 35]
        term_matches = re.findall(r'([A-Z][a-zA-Z0-9\s]{2,25})\s+(?:is defined as|refers to|is a|means)\s+([^.]{20,150}\.)', text)
        
        questions = []
        q_id = 1

        # 1. Generate definition questions
        for term, definition in term_matches:
            clean_term = term.strip()
            if len(clean_term.split()) <= 4 and clean_term.lower() not in {"this", "it", "there"}:
                correct = definition.strip()
                # Create plausible distractors
                distractors = [
                    f"A temporary cache mechanism that disregards incoming {clean_term} inputs.",
                    f"An outdated method replaced by modern distributed streaming protocols.",
                    f"A secondary parameter solely utilized during error recovery procedures."
                ]
                options = [correct] + distractors
                random.shuffle(options)
                
                questions.append({
                    "id": q_id,
                    "question": f"Which of the following best defines '{clean_term}'?",
                    "options": options,
                    "correct_answer": correct,
                    "explanation": f"According to the study text, {clean_term} is defined as: {correct}"
                })
                q_id += 1
                if len(questions) >= num_questions:
                    break

        # 2. Generate conceptual and True/False questions if needed
        if len(questions) < num_questions and sentences:
            for s in sentences[:15]:
                if len(s) > 50 and any(w in s.lower() for w in ["always", "requires", "leads", "primary", "crucial", "fundamental"]):
                    # True/False style as MCQ
                    options = ["True", "False"]
                    correct = "True"
                    questions.append({
                        "id": q_id,
                        "question": f"Based on the text: \"{s}\" — Is this statement supported by the document?",
                        "options": ["True", "False"],
                        "correct_answer": "True",
                        "explanation": f"This statement directly reflects the core finding documented in the notes."
                    })
                    q_id += 1
                    if len(questions) >= num_questions:
                        break

        # Fallback question if text was very short
        if not questions:
            questions.append({
                "id": 1,
                "question": "What is the primary objective of studying these materials?",
                "options": [
                    "To master fundamental principles and apply them effectively",
                    "To memorize superficial details without conceptual context",
                    "To discard structured notes in favor of guesswork",
                    "None of the above"
                ],
                "correct_answer": "To master fundamental principles and apply them effectively",
                "explanation": "Active learning requires deep understanding of principles rather than passive memorization."
            })

        return {
            "title": title,
            "difficulty": difficulty,
            "questions": questions[:num_questions]
        }

    # =========================================================================
    # 5. UTILITY & VALIDATION
    # =========================================================================
    @staticmethod
    def _extract_json(raw_text: str) -> Optional[Any]:
        if not raw_text:
            return None
        raw_text = raw_text.strip()
        # Remove markdown codeblock fences if present
        if raw_text.startswith("```"):
            raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
            raw_text = re.sub(r'\s*```$', '', raw_text)
            raw_text = raw_text.strip()
        try:
            return json.loads(raw_text)
        except Exception:
            # Try finding first { or [ to last } or ]
            m = re.search(r'(\{.*\}|\[.*\])', raw_text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1))
                except Exception:
                    pass
        return None

    @classmethod
    async def verify_api_key(cls, provider: str, api_key: str) -> Dict[str, Any]:
        """Tests an API key and returns validity status and available models."""
        if not api_key:
            return {"valid": False, "message": "API key cannot be empty"}
            
        if provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                res = model.generate_content("Ping. Respond with 'PONG'.")
                return {
                    "valid": True,
                    "message": "Google Gemini API connected successfully!",
                    "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
                }
            except Exception as e:
                return {"valid": False, "message": f"Gemini connection failed: {str(e)}"}

        elif provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                client.models.list()
                return {
                    "valid": True,
                    "message": "OpenAI API connected successfully!",
                    "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
                }
            except Exception as e:
                return {"valid": False, "message": f"OpenAI connection failed: {str(e)}"}

        return {"valid": True, "message": "Smart Local AI Engine is always active and ready!"}

