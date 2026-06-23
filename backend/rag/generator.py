import ollama


def answer(
question,
context
):

    prompt=f"""

Context:

{context}

Question:

{question}

Answer only using context.

"""

    r = ollama.chat(

        model="llama3.2",

        messages=[

        {
            "role":"user",
            "content":prompt
        }

        ]
    )

    return r["message"]["content"]