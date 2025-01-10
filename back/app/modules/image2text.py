import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def groq_text_models(documents, question):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "you are a helpful assistant that understand very well software development process"
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": f"""

                DOCUMENTS:
                {documents}

                QUESTION:
                {question}

                INSTRUCTIONS:

                """,
            }
        ],

        # The language model which will generate the completion.
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        max_tokens=1024,
        top_p=1,
        stop=None,

        # If set, partial message deltas will be sent.
        stream=False,
    )
    # Print the completion returned by the LLM.
    print(chat_completion.choices[0].message.content)


def groq_vision_models(encoded_string, 
                       prompt: str="What's in this image?",
                       model: str="llama-3.2-11b-vision-preview"):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{ encoded_string.decode('utf-8') }",
                        },
                    },
                ],
            }
        ],
        model=model,
    )

    resp = chat_completion.choices[0].message.content
    return resp