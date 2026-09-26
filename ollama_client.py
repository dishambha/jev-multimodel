import requests
import json


OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_ollama(
    model: str,
    prompt: str,
    think: bool = False,
    timeout: int = 900,
) -> str:

    print(f"\nLoading model: {model}")
    print("Generating:\n")

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": True,
                "think": think,
                "keep_alive": -1,
            },
            stream=True,
            timeout=timeout,
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        raise RuntimeError("Could not connect to Ollama. Make sure Ollama is running.")

    except requests.exceptions.Timeout:
        raise RuntimeError(f"Ollama request timed out after {timeout} seconds.")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ollama request failed: {e}")

    full_response = []

    try:
        for line in response.iter_lines():
            if not line:
                continue

            data = json.loads(line)

            chunk = data.get("response", "")

            if chunk:
                print(chunk, end="", flush=True)
                full_response.append(chunk)

            if data.get("done", False):
                break

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error while receiving Ollama response: {e}")

    print()

    return "".join(full_response)
