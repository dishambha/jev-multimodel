from jev_router import classify_query
from ollama_client import ask_ollama
from comfyui_client import generate_image


# ============================================================
# MODELS
# ============================================================

GENERAL_MODEL = "qwen3:8b"

CODING_MODEL = "qwen2.5-coder:7b"

SPECIALIZED_CODING_MODEL = "cieloforge/qwen2.5-coder-7b-instruct-spec:latest"


# ============================================================
# MAIN
# ============================================================


def main():

    print("=" * 55)
    print("                 JEV MULTIMODEL")
    print("=" * 55)

    print("\nAvailable routes:")
    print("GENERAL → Qwen3 8B")
    print("CODING  → Qwen2.5 Coder 7B")
    print("IMAGE   → ComfyUI / Qwen Image")

    print("\nType 'exit', 'quit', or '/bye' to stop.")

    print("=" * 55)
    print()

    while True:
        try:
            query = input("You: ").strip()

        except KeyboardInterrupt:
            print("\n\nExiting JEV.")
            break

        # ----------------------------------------------------
        # Empty input
        # ----------------------------------------------------

        if not query:
            continue

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if query.lower() in {
            "exit",
            "quit",
            "/bye",
        }:
            print("\nGoodbye!")
            break

        try:
            # =================================================
            # ROUTER
            # =================================================

            category = classify_query(query)

            # =================================================
            # GENERAL
            # =================================================

            if category == "GENERAL":
                print("\n→ Routing to Qwen3 8B...")

                response = ask_ollama(
                    model=GENERAL_MODEL,
                    prompt=query,
                    think=False,
                )

                print("\nQwen3:")
                print("-" * 55)
                print(response)

            # =================================================
            # CODING
            # =================================================

            elif category == "CODING":
                print("\n→ Routing to Qwen2.5 Coder 7B...")

                response = ask_ollama(
                    model=CODING_MODEL,
                    prompt=query,
                    think=False,
                )

                print("\nQwen2.5 Coder:")
                print("-" * 55)
                print(response)

            # =================================================
            # IMAGE
            # =================================================

            elif category == "IMAGE":
                print("\n→ Routing to ComfyUI / Qwen Image...")

                generated_images = generate_image(query)

                print("\n✓ IMAGE GENERATION COMPLETE")

                for image_path in generated_images:
                    print(f"Saved: {image_path}")

            # =================================================
            # UNKNOWN
            # =================================================

            else:
                print(f"\nJEV returned an unknown category: {category}")

        # ----------------------------------------------------
        # Errors
        # ----------------------------------------------------

        except Exception as e:
            print("\n❌ Error:")
            print(e)

        print("\n" + "=" * 55)
        print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
