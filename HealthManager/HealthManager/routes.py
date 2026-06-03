from flask import Blueprint, request, jsonify
try:
    from .agent import generate_health_response
except ImportError:
    from agent import generate_health_response

qwen_bp = Blueprint('qwen_agent', __name__)

@qwen_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    messages = data.get("messages", [])
    user_context = data.get("user_context", {})

    if not messages:
        return jsonify({"error": "Empty messages"}), 400

    # 为了安全起见以及规范化前端请求格式，这里确保前端传来的 messages 是合理格式的 list
    # 例: [{"role": "user", "content": "你好"}, {"role": "bot", "content": "..."}]
    # openai 接口要 {"role": "assistant"}
    formatted_messages = []
    for msg in messages:
        role = "assistant" if msg.get("role") == "bot" else "user"
        formatted_messages.append({
            "role": role,
            "content": msg.get("content", "")
        })


    result = generate_health_response(formatted_messages, user_context)
    if isinstance(result, dict):
        response_text = result.get("reply", "")
        thinking_process = result.get("thinking_process", [])
    else:
        response_text = str(result)
        thinking_process = []

    return jsonify({
        "success": True,
        "reply": response_text,
        "thinking_process": thinking_process,
    })


