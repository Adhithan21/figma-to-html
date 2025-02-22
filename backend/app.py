from flask import Flask, request, jsonify
import requests
import json
import traceback

app = Flask(__name__)

OPENAI_API_KEY = "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"
FIGMA_ACCESS_TOKEN = "figd_LRcwhMHOQ92D9BwHNnL0qW_oM4p7mV4dm6Pu4qhi"

FIGMA_API_URL = "https://api.figma.com/v1/files/"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

cached_figma_json = {}

@app.route('/fetch-figma', methods=['POST'])
def fetch_figma_json():
    """Fetch Figma JSON using file key"""
    try:
        data = request.json
        file_key = data.get("file_key")

        if not file_key:
            return jsonify({"error": "File key is required!"}), 400

        headers = {"X-Figma-Token": FIGMA_ACCESS_TOKEN}
        response = requests.get(f"{FIGMA_API_URL}{file_key}", headers=headers, timeout=30)
        response.raise_for_status()

        figma_json = response.json()
        
        if not figma_json:
            return jsonify({"error": "Empty JSON received from Figma"}), 400

        cached_figma_json[file_key] = figma_json
        return jsonify({"message": "Figma JSON fetched successfully!", "figma_json": figma_json})

    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return jsonify({"error": f"Error fetching JSON from Figma: {str(e)}"}), 500


@app.route('/convert-to-html', methods=['POST'])
def convert_to_html():
    """Convert Figma JSON to HTML & CSS using OpenAI API"""
    try:
        data = request.json
        file_key = data.get("file_key")

        if not file_key:
            return jsonify({"error": "File key is required!"}), 400

        if file_key not in cached_figma_json:
            return jsonify({"error": "Figma JSON not found. Fetch it first."}), 400

        figma_json = cached_figma_json[file_key]

        if not figma_json:
            return jsonify({"error": "Figma JSON is empty. Fetch a valid file."}), 400

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": f"Convert this Figma JSON into clean HTML and CSS: {json.dumps(figma_json)}"
                }
            ],
            "temperature": 0.6,
            "top_p": 0.7,
            "max_tokens": 4096
        }

        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        api_response = response.json()
        
        if "choices" not in api_response or not api_response["choices"]:
            return jsonify({"error": "Invalid response from OpenAI"}), 500

        html_css_code = api_response["choices"][0]["message"]["content"]

        return jsonify({"message": "Conversion Successful!", "html_css_code": html_css_code})

    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return jsonify({"error": f"Error in AI Conversion: {str(e)}"}), 500

    except json.JSONDecodeError:
        traceback.print_exc()
        return jsonify({"error": "Invalid JSON format received"}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
