from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, ExecutionHistory
from compiler.runner import run_code
import requests

compiler_bp = Blueprint('compiler', __name__)

def generate_mock_ai_response(query, code):
    query_lower = query.lower()
    if 'explain' in query_lower:
        return """### Code Explanation
I analyzed your active code. Here is a summary of its structure:

1. **Approach**: It represents a standard script/logic block.
2. **Key APIs Used**: Standard I/O libraries according to the active language.
3. **Complexity**: The time complexity is O(N) depending on loops, and space complexity is minimal.

**Recommendations**:
- Ensure variables have descriptive names.
- Handle potential edge cases for user input."""
    elif 'debug' in query_lower or 'error' in query_lower:
        bugs = []
        if 'print' in code and '(' not in code and 'import' not in code:
            bugs.append("Python print function missing parenthesis: `print('...')` in Python 3.")
        if ('main' in code or 'printf' in code) and ';' not in code:
            bugs.append("C/C++ missing semicolons at line ends.")
        
        if bugs:
            warnings = "\n".join([f"- **Warning**: {b}" for b in bugs])
            return f"""### Debugger Analysis
I found potential bugs in your file:

{warnings}

Please review your code syntax and try recompiling. Let me know if you need specific corrections!"""
        return """### Debugger Analysis
I scanned your active source code and did not find obvious grammatical bugs (like mismatched parenthesis or unclosed string literals). 

If you are seeing runtime exceptions, double check:
1. Division by zero conditions.
2. Index out of bounds checks.
3. Proper feeding of standard inputs inside the **Input** textarea."""
    elif 'optimize' in query_lower:
        return """### Code Optimization Suggestions
To improve the efficiency of your code:
- **Minimize Overhead**: Avoid re-allocating arrays inside loops.
- **Buffer Output**: For C++, use `std::ios_base::sync_with_stdio(false)` to speed up operations.
- **Memory Check**: Release unneeded pointers/objects once their lifecycle ends."""
    elif 'generate' in query_lower or 'boilerplate' in query_lower:
        return """### Code Generation
Here is a template to help you get started:
```python
def main():
    # Write your logic here
    print("Welcome to CoreIDE!")

if __name__ == "__main__":
    main()
```"""
    return """### AI Assistant Response
I'm here to help you code! Since no live Gemini API Key is configured in `.env`, I am running in mock developer mode.

To enable live AI generation:
1. Obtain an API Key from Google AI Studio.
2. Open the `.env` file in the project folder.
3. Set `AI_API_KEY` to your key:
   `AI_API_KEY=AIzaSy...`
4. Restart the Flask server.
"""

@compiler_bp.route('/api/compiler/run', methods=['POST'])
@login_required
def run_compiler():
    data = request.get_json() or {}
    language = data.get('language')
    source_code = data.get('source_code')
    stdin_data = data.get('stdin_data', "")
    
    if not language or not source_code:
        return jsonify({'error': 'Language and source code are required'}), 400
        
    # Execute the code
    result = run_code(language, source_code, stdin_data)
    
    # Save to history database
    history = ExecutionHistory(
        user_id=current_user.id,
        language=language,
        source_code=source_code,
        output=result.get('stdout'),
        error=result.get('stderr') or result.get('compile_error'),
        execution_time=result.get('execution_time'),
        memory_usage=result.get('memory_usage')
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify(result)

@compiler_bp.route('/api/compiler/history', methods=['GET'])
@login_required
def get_history():
    history_items = ExecutionHistory.query.filter_by(user_id=current_user.id)\
        .order_by(ExecutionHistory.created_at.desc()).limit(50).all()
    return jsonify([h.to_dict() for h in history_items])

@compiler_bp.route('/history')
@login_required
def history_page():
    from flask import render_template
    lang_filter = request.args.get('lang', '')
    query = ExecutionHistory.query.filter_by(user_id=current_user.id)
    if lang_filter:
        query = query.filter_by(language=lang_filter)
    history_items = query.order_by(ExecutionHistory.created_at.desc()).limit(100).all()
    
    # Get distinct languages for filter dropdown
    all_langs = db.session.query(ExecutionHistory.language).filter_by(user_id=current_user.id)\
        .distinct().all()
    languages = sorted([l[0] for l in all_langs])
    
    return render_template('history.html', history=history_items, languages=languages, active_filter=lang_filter)

@compiler_bp.route('/api/compiler/chat', methods=['POST'])
@login_required
def chat_assistant():
    data = request.get_json() or {}
    prompt = data.get('prompt')
    code = data.get('code', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
        
    api_key = current_app.config.get('AI_API_KEY', '')
    api_url = current_app.config.get('AI_API_URL', '')
    
    # If the user has not configured the API key, return mock response
    if not api_key or api_key == 'your_gemini_api_key_here':
        response_text = generate_mock_ai_response(prompt, code)
        return jsonify({'response': response_text, 'mocked': True})
        
    try:
        # Construct content payload for Gemini API
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"You are an expert AI software developer embedded in CoreIDE.io, a browser-based Web IDE.\n"
                            f"The developer is editing the following code:\n"
                            f"```\n{code}\n```\n\n"
                            f"Developer's request: {prompt}\n"
                            f"Provide a clear, formatted markdown response. Be concise."
                }]
            }]
        }
        
        url = f"{api_url}?key={api_key}" if "?" not in api_url else f"{api_url}&key={api_key}"
        
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
        
        if response.status_code == 200:
            res_json = response.json()
            try:
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                return jsonify({'response': text, 'mocked': False})
            except (KeyError, IndexError):
                return jsonify({'error': 'Malformed response structure from Gemini API', 'raw': res_json}), 502
        else:
            return jsonify({'error': f'API error status {response.status_code}', 'details': response.text}), 502
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'API connection error: {str(e)}'}), 500

