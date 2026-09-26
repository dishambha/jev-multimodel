import json
import time
import uuid
from pathlib import Path

import requests


# ============================================================
# CONFIGURATION
# ============================================================

COMFYUI_URL = "http://127.0.0.1:8188"

BASE_DIR = Path(__file__).resolve().parent

WORKFLOW_FILE = BASE_DIR / "workflow_api.json"

OUTPUT_DIR = BASE_DIR / "generated_images"


# ============================================================
# LOAD WORKFLOW
# ============================================================

def load_workflow():
    """
    Load the ComfyUI API workflow JSON.
    """

    if not WORKFLOW_FILE.exists():
        raise FileNotFoundError(
            f"Workflow file not found:\n{WORKFLOW_FILE}"
        )

    with open(WORKFLOW_FILE, "r", encoding="utf-8") as file:
        workflow = json.load(file)

    return workflow


# ============================================================
# FIND TEXT INPUTS
# ============================================================

def find_text_inputs(workflow):
    """
    Find possible text/string inputs inside the workflow.

    This helps us discover where the Qwen prompt lives.
    """

    matches = []

    for node_id, node in workflow.items():

        inputs = node.get("inputs", {})

        for input_name, value in inputs.items():

            if isinstance(value, str) and value.strip():

                matches.append(
                    {
                        "node_id": node_id,
                        "input_name": input_name,
                        "value": value,
                        "class_type": node.get("class_type"),
                    }
                )

    return matches


# ============================================================
# REPLACE PROMPT
# ============================================================

def replace_prompt(workflow, prompt):
    """
    Try to replace the main text prompt in the workflow.

    Qwen workflows can use different node types, so we check
    common prompt-related input names.
    """

    preferred_inputs = [
        "text",
        "prompt",
        "positive",
        "positive_prompt",
        "text_prompt",
    ]

    # First look for obvious prompt fields.
    for node_id, node in workflow.items():

        inputs = node.get("inputs", {})

        for input_name in preferred_inputs:

            if input_name in inputs:

                value = inputs[input_name]

                # Don't replace linked node connections.
                if isinstance(value, str):

                    print(
                        f"Updating prompt node "
                        f"{node_id} → {input_name}"
                    )

                    inputs[input_name] = prompt

                    return True

    # Fallback:
    # Look for a node containing text.
    text_matches = find_text_inputs(workflow)

    for match in text_matches:

        node_id = match["node_id"]
        input_name = match["input_name"]

        value = match["value"]

        # Skip filename-like fields.
        if input_name.lower() in {
            "filename_prefix",
            "filename",
            "file",
        }:
            continue

        print(
            f"Updating text node "
            f"{node_id} → {input_name}"
        )

        workflow[node_id]["inputs"][input_name] = prompt

        return True

    return False


# ============================================================
# CHECK COMFYUI
# ============================================================

def check_comfyui():
    """
    Check whether ComfyUI is running.
    """

    try:
        response = requests.get(
            f"{COMFYUI_URL}/system_stats",
            timeout=5,
        )

        response.raise_for_status()

        return True

    except requests.exceptions.RequestException:

        return False


# ============================================================
# SEND WORKFLOW
# ============================================================

def queue_workflow(workflow):
    """
    Send the workflow to ComfyUI.
    """

    client_id = str(uuid.uuid4())

    payload = {
        "prompt": workflow,
        "client_id": client_id,
    }

    response = requests.post(
        f"{COMFYUI_URL}/prompt",
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(
            f"ComfyUI rejected workflow:\n{data['error']}"
        )

    prompt_id = data.get("prompt_id")

    if not prompt_id:
        raise RuntimeError(
            f"ComfyUI did not return a prompt_id:\n{data}"
        )

    return prompt_id


# ============================================================
# WAIT FOR GENERATION
# ============================================================

def wait_for_generation(prompt_id, timeout=600):
    """
    Wait until ComfyUI finishes the workflow.
    """

    start_time = time.time()

    print("\nWaiting for ComfyUI generation...")

    while True:

        if time.time() - start_time > timeout:
            raise TimeoutError(
                "ComfyUI generation timed out."
            )

        try:

            response = requests.get(
                f"{COMFYUI_URL}/history/{prompt_id}",
                timeout=10,
            )

            response.raise_for_status()

            history = response.json()

            if prompt_id in history:

                result = history[prompt_id]

                status = result.get("status", {})

                status_string = status.get(
                    "status_str"
                )

                if status_string == "success":

                    print("Generation completed.")

                    return result

                if status_string == "error":

                    messages = status.get(
                        "messages",
                        []
                    )

                    raise RuntimeError(
                        f"ComfyUI generation failed:\n"
                        f"{messages}"
                    )

        except requests.exceptions.RequestException:
            pass

        time.sleep(1)


# ============================================================
# DOWNLOAD OUTPUT IMAGE
# ============================================================

def download_image(filename, subfolder="", image_type="output"):
    """
    Download a generated image from ComfyUI.
    """

    params = {
        "filename": filename,
        "subfolder": subfolder,
        "type": image_type,
    }

    response = requests.get(
        f"{COMFYUI_URL}/view",
        params=params,
        timeout=60,
    )

    response.raise_for_status()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = OUTPUT_DIR / filename

    # Avoid path traversal problems.
    output_path = OUTPUT_DIR / Path(filename).name

    with open(output_path, "wb") as file:
        file.write(response.content)

    return output_path


# ============================================================
# GENERATE IMAGE
# ============================================================

def generate_image(prompt):
    """
    Complete ComfyUI image generation pipeline.

    1. Check ComfyUI
    2. Load workflow
    3. Replace prompt
    4. Queue workflow
    5. Wait for generation
    6. Download output image
    """

    print("\n" + "=" * 60)
    print("COMFYUI IMAGE GENERATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Check ComfyUI
    # --------------------------------------------------------

    if not check_comfyui():

        raise RuntimeError(
            "ComfyUI is not running.\n\n"
            "Start ComfyUI first using:\n"
            "start_comfyui.bat"
        )

    print("✓ ComfyUI is running")

    # --------------------------------------------------------
    # Load workflow
    # --------------------------------------------------------

    workflow = load_workflow()

    print("✓ Workflow loaded")

    # --------------------------------------------------------
    # Replace prompt
    # --------------------------------------------------------

    replaced = replace_prompt(
        workflow,
        prompt,
    )

    if not replaced:

        raise RuntimeError(
            "Could not automatically find the "
            "prompt field in qwen_reference_workflow.json."
        )

    print("✓ Prompt updated")

    # --------------------------------------------------------
    # Queue workflow
    # --------------------------------------------------------

    prompt_id = queue_workflow(
        workflow
    )

    print(f"✓ Workflow queued")
    print(f"Prompt ID: {prompt_id}")

    # --------------------------------------------------------
    # Wait
    # --------------------------------------------------------

    result = wait_for_generation(
        prompt_id
    )

    # --------------------------------------------------------
    # Find output images
    # --------------------------------------------------------

    outputs = result.get(
        "outputs",
        {}
    )

    generated_files = []

    for node_id, node_output in outputs.items():

        images = node_output.get(
            "images",
            []
        )

        for image_info in images:

            filename = image_info.get(
                "filename"
            )

            subfolder = image_info.get(
                "subfolder",
                ""
            )

            image_type = image_info.get(
                "type",
                "output"
            )

            if filename:

                path = download_image(
                    filename,
                    subfolder,
                    image_type,
                )

                generated_files.append(
                    path
                )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not generated_files:

        raise RuntimeError(
            "ComfyUI finished successfully, "
            "but no output image was found."
        )

    print("\nGenerated image:")

    for path in generated_files:
        print(path)

    print("=" * 60)

    return generated_files