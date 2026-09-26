import os
from pathlib import Path

from dotenv import load_dotenv
from typesafe_sdk import Noul, TypeSafeClient


# --------------------------------------------------
# Environment
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env", override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise SystemExit(
        "Missing OPENROUTER_API_KEY in .env"
    )


# --------------------------------------------------
# JEV / OpenRouter
# --------------------------------------------------

client = TypeSafeClient(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api",
)


# --------------------------------------------------
# Ollama
# --------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"


# --------------------------------------------------
# Models
# --------------------------------------------------

GENERAL_MODEL = "qwen3:8b"

CODING_MODEL = "qwen2.5-coder:7b"

SPECIALIZED_CODING_MODEL = (
    "cieloforge/qwen2.5-coder-7b-instruct-spec:latest"
)


# --------------------------------------------------
# JEV Router
# --------------------------------------------------

def classify_query(query: str) -> str:
    """
    Ask JEV to classify the user's query.

    Possible results:

        GENERAL
        CODING
        IMAGE
    """

    result = client.system_one(
        state=query,

        questions={

            # ------------------------------------------
            # General purpose
            # ------------------------------------------

            "general": Noul(
                instructions="""
Is the user's request primarily a general-purpose
question, conversation, explanation, reasoning,
writing request, knowledge question, advice,
or normal assistant interaction?

Examples:

- Explain the OSI model.
- What is inflation?
- Help me understand this concept.
- Write an email.
- Explain this topic simply.

Return a confidence score:

1.0 = definitely general purpose
0.0 = definitely not general purpose.
"""
            ),

            # ------------------------------------------
            # Coding
            # ------------------------------------------

            "coding": Noul(
                instructions="""
Is the user's request primarily related to
programming or software development?

This includes:

- Python
- C++
- Java
- JavaScript
- SQL
- FastAPI
- APIs
- debugging
- algorithms
- data structures
- writing code
- explaining code
- fixing code
- software architecture

Return a confidence score:

1.0 = definitely coding
0.0 = definitely not coding.
"""
            ),

            # ------------------------------------------
            # Image generation
            # ------------------------------------------

            "image": Noul(
                instructions="""
Is the user asking to create, generate, edit,
modify, redesign, transform, or otherwise produce
an image?

Examples:

- Create an image of a superhero.
- Generate a futuristic city.
- Change the character's clothes.
- Make this image realistic.
- Create a cinematic scene.
- Edit this image.

Return a confidence score:

1.0 = definitely image generation/editing
0.0 = definitely not image generation/editing.
"""
            ),
        },
    )


    # --------------------------------------------------
    # Get scores
    # --------------------------------------------------

    scores = {
        "GENERAL": result.answers["general"].noul,
        "CODING": result.answers["coding"].noul,
        "IMAGE": result.answers["image"].noul,
    }


    # --------------------------------------------------
    # Select highest score
    # --------------------------------------------------

    category = max(
        scores,
        key=scores.get
    )


    # --------------------------------------------------
    # Display routing decision
    # --------------------------------------------------

    print("\n------------------------------")
    print("JEV ROUTER")
    print("------------------------------")

    print(f"GENERAL : {scores['GENERAL']:.2f}")
    print(f"CODING  : {scores['CODING']:.2f}")
    print(f"IMAGE   : {scores['IMAGE']:.2f}")

    print("------------------------------")
    print(f"SELECTED: {category}")
    print("------------------------------")


    return category