from flask import Flask, request, jsonify
import uuid
import os
from openai import OpenAI

app = Flask(__name__)

# LLM Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.mulerouter.ai/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen/qwen-2.5-72b-instruct")

client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)

sessions = {}

@app.route('/')
def index():
    return jsonify({
        "service": "MiroFish Swarm Adapter",
        "status": "online",
        "model": LLM_MODEL_NAME,
        "endpoints": ["/health", "/api/graph/build", "/api/simulation/start", "/api/report/generate"]
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api/graph/build', methods=['POST'])
def build_graph():
    data = request.json
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "status": "built",
        "seed_text": data.get("seed_text", ""),
        "question": data.get("prediction_question", "")
    }
    return jsonify({"session_id": session_id}), 200

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    data = request.json
    session_id = data.get("session_id")
    if session_id in sessions:
        sessions[session_id]["status"] = "running"
        return jsonify({"message": "Simulation started"}), 202
    return jsonify({"error": "Invalid session"}), 400

@app.route('/api/report/generate', methods=['GET'])
def generate_report():
    session_id = request.args.get("session_id")
    if session_id in sessions:
        sess = sessions[session_id]
        
        prompt = (
            f"You are a swarm of 20 high-frequency trading agents. "
            f"Analyze this market context:\n{sess['seed_text']}\n\n"
            f"Question: {sess['question']}\n\n"
            "Provide a definitive consensus report. MUST include one of these keywords: BULLISH, BEARISH, or NEUTRAL."
        )

        try:
            response = client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a professional crypto trading analyst swarm."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            report_text = response.choices[0].message.content
            return jsonify({"report": report_text}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid session"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
