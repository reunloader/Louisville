"""
Derby City Watch Chatbot
Flask application for chatbot interface to query scanner updates.
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
from scanner_parser import ScannerParser
from ai_service import AIService
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Initialize services
posts_dir = os.getenv('POSTS_DIRECTORY', '../_posts')
ai_provider = os.getenv('AI_PROVIDER', 'gemini')

print(f"Initializing Derby City Watch Chatbot...")
print(f"Posts directory: {posts_dir}")
print(f"AI Provider: {ai_provider}")

scanner_parser = ScannerParser(posts_dir)
ai_service = AIService(provider=ai_provider)


@app.route('/')
def index():
    """Render the chatbot interface."""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Get conversation history from session
        if 'conversation' not in session:
            session['conversation'] = []

        # Get scanner data context
        scanner_data = scanner_parser.get_all_data_for_ai()

        # Generate AI response
        response = ai_service.generate_response(
            user_message=user_message,
            scanner_data=scanner_data,
            conversation_history=session['conversation']
        )

        # Update conversation history
        session['conversation'].append({'role': 'user', 'content': user_message})
        session['conversation'].append({'role': 'assistant', 'content': response})

        # Keep only last 10 messages to manage session size
        if len(session['conversation']) > 10:
            session['conversation'] = session['conversation'][-10:]

        session.modified = True

        return jsonify({
            'response': response,
            'success': True
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': str(e),
            'response': "I'm having trouble processing your request. Please try again.",
            'success': False
        }), 500


@app.route('/api/reload', methods=['POST'])
def reload_data():
    """Reload scanner data (useful for updates)."""
    try:
        global scanner_parser
        scanner_parser.load_all_posts()
        return jsonify({
            'success': True,
            'message': f'Reloaded {len(scanner_parser.incidents)} scanner updates'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about loaded data."""
    try:
        categories = {}
        statuses = {}

        for incident in scanner_parser.incidents:
            # Count categories
            for cat in incident.get('categories', []):
                categories[cat] = categories.get(cat, 0) + 1

            # Count statuses
            status = incident.get('status', 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1

        return jsonify({
            'success': True,
            'total_incidents': len(scanner_parser.incidents),
            'categories': categories,
            'statuses': statuses,
            'ai_provider': ai_provider
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history."""
    session['conversation'] = []
    return jsonify({'success': True, 'message': 'Conversation cleared'})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'incidents_loaded': len(scanner_parser.incidents)})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    print(f"\n{'='*60}")
    print(f"Derby City Watch Chatbot is running!")
    print(f"Loaded {len(scanner_parser.incidents)} scanner updates")
    print(f"AI Provider: {ai_provider}")
    print(f"Server: http://localhost:{port}")
    print(f"{'='*60}\n")

    app.run(host='0.0.0.0', port=port, debug=debug)
