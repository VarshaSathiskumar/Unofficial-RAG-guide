"""
generate.py - Answer a query using retrieved chunks as context (RAG).
"""

import os
from dotenv import load_dotenv
from groq import Groq
from retrieve import retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT_TEMPLATE = """\
You are a helpful assistant for Colorado School of Mines graduate students.
Answer the question using ONLY the information in the provided documents below.
If the documents do not contain enough information to answer, say:
"I don't have enough information on that." Don't add resources for questions you don't have enough information to answer.

Cite the source document(s) at the end of your answer in this format:
Sources: <document name(s)>

Documents:
{context}

Question: {question}
"""


def generate(query: str, k: int = 5) -> str:
    chunks  = retrieve(query, k=k)
    context = "\n\n---\n\n".join(
        f"[{os.path.basename(r['source'])}]\n{r['chunk']}" for r in chunks
    )

    prompt = PROMPT_TEMPLATE.format(context=context, question=query)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()

    if "i don't have enough information" in answer.lower():
        answer = "I don't have enough information on that."

    return answer


if __name__ == "__main__":
    test_queries = [
        "What happens if a student receives an incomplete grade?",
        "What are the CS degree options at Mines?",
        "What is the tuition refund policy?",
        "What is the academic integrity policy?",
        "How do I apply for graduation?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Q: {query}")
        print(f"{'='*60}")
        print(generate(query))
