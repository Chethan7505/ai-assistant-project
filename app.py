"""
AI Assistant - Professional Edition
Real Hugging Face Transformers AI
Author: Chethan Chirag M
Date: December 31, 2025
"""

from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)

# Database setup
DB_FILE = 'ai_assistant.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            function_type TEXT,
            user_input TEXT,
            ai_response TEXT,
            timestamp DATETIME,
            helpful INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# ============================================
# LOAD AI MODELS (LIGHTWEIGHT FOR RAILWAY)
# ============================================

print("Loading AI Models (first time takes 2-3 minutes)...")

# QA Pipeline - Lightweight
try:
    qapipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    print("✅ QA model loaded")
except Exception as e:
    print(f"⚠️  QA Model error: {e}")
    qapipeline = None

# Summarization Pipeline - Lightweight
try:
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    print("✅ Summarizer model loaded")
except Exception as e:
    print(f"⚠️  Summarizer error: {e}")
    summarizer = None

# Text Generation Pipeline - Lightweight
try:
    textgenerator = pipeline("text-generation", model="distilgpt2")
    print("✅ Text generator model loaded")
except Exception as e:
    print(f"⚠️  Text generator error: {e}")
    textgenerator = None

print("All models loaded successfully!")

# ============================================
# KNOWLEDGE BASE
# ============================================

KNOWLEDGE_BASE = {
    "artificial intelligence": "AI is the simulation of human intelligence by machines. It enables systems to learn from data, recognize patterns, and make decisions with minimal human intervention. Key applications include computer vision, NLP, robotics, and autonomous systems. AI is revolutionizing healthcare, finance, transportation, and many other industries.",
    
    "machine learning": "Machine Learning is a subset of AI where systems improve through experience without explicit programming. It uses algorithms to analyze data and make predictions. Types include supervised learning (labeled data), unsupervised learning (unlabeled data), and reinforcement learning. Applications: recommendation systems, fraud detection, image recognition, autonomous vehicles.",
    
    "deep learning": "Deep Learning uses neural networks with multiple layers to learn complex patterns. It powers breakthroughs in computer vision, NLP, and speech recognition. Popular architectures: CNNs, RNNs, Transformers. Requires significant computational power and large training datasets.",
    
    "neural network": "Neural networks are inspired by biological neurons. They consist of interconnected nodes in layers: input, hidden, and output. Each connection has weights that adjust during training. They learn non-linear relationships and are fundamental to modern AI.",
    
    "transformer": "Transformers use attention mechanisms for efficient sequential data processing. They power BERT, GPT, and T5. Unlike RNNs, they process data in parallel, capturing long-range dependencies better. Revolutionary for NLP and computer vision.",
    
    "natural language processing": "NLP helps computers understand and generate human language. Applications: chatbots, translation, sentiment analysis, text classification. Modern NLP uses transformers and deep learning. Key techniques: tokenization, embeddings, attention mechanisms.",
    
    "python": "Python is a high-level language for AI, data science, web development. Features: simplicity, readability, extensive libraries (NumPy, Pandas, TensorFlow, PyTorch). Preferred for machine learning and scientific computing.",
    
    "flask": "Flask is a lightweight Python web framework for building web apps and REST APIs. Uses Jinja2 templating and Werkzeug. Perfect for rapid development, microservices, and ML integration. Minimal but extensible.",
    
    "javascript": "JavaScript powers interactive web applications. Runs in browsers. Modern JS includes arrow functions, classes, promises, async/await. Node.js enables backend development. Frameworks: React, Vue, Angular for frontend; Express for backend.",
    
    "react": "React is a JavaScript library for building UIs with reusable components. Uses virtual DOM for efficient rendering. Features: component-based architecture, hooks, JSX. Ideal for SPAs and large-scale applications.",
    
    "sql": "SQL manages and queries relational databases. Enables SELECT (retrieval), INSERT, UPDATE, DELETE operations. Features: joins, aggregations, subqueries, indexes. DBMS: PostgreSQL, MySQL, Oracle, SQL Server.",
    
    "tech career": "Tech careers offer diverse opportunities and high earning potential. Required skills: programming (Python, JavaScript, Java), data structures, databases, web frameworks, cloud platforms (AWS, Azure, GCP). Popular roles: software engineer, data scientist, DevOps engineer, ML engineer.",
    
    "learning": "Effective learning: choose your style (visual, auditory, kinesthetic), practice consistently with feedback, teach others, learn from failures, stay curious, build projects, read documentation and research papers.",
    
    "coding": "Write clean code with meaningful names and comments. Test thoroughly with unit and integration tests. Use version control (Git). Read others' code. Use linters and formatters. Follow DRY principle.",
    
    "productivity": "Set clear, time-bound goals. Prioritize by importance/urgency. Use time-blocking for focused work. Eliminate distractions. Track progress. Use tools like Todoist, Notion. Start with important tasks.",
    
    "studying": "Create detailed schedules. Break information into chunks. Use active recall and spaced repetition. Find quiet environments. Take regular breaks (Pomodoro: 25 min work, 5 min break). Form study groups.",
}

# ============================================
# ADVICE DATABASE
# ============================================

ADVICE_DATABASE = {
    "studying": [
        "Create a detailed study schedule and stick to it",
        "Break information into manageable chunks",
        "Use active recall and spaced repetition",
        "Find a quiet, distraction-free study environment",
        "Take regular breaks using Pomodoro Technique",
        "Review material multiple times before exams",
        "Form study groups to explain concepts"
    ],
    
    "productivity": [
        "Set clear, measurable, time-bound goals",
        "Prioritize by importance and urgency",
        "Use time-blocking for focused work",
        "Eliminate distractions and notifications",
        "Track progress daily",
        "Use productivity tools (Todoist, Notion, Asana)",
        "Start with the most important task first"
    ],
    
    "learning": [
        "Choose your learning method (visual, auditory, kinesthetic)",
        "Practice consistently with specific feedback",
        "Teach others to reinforce your knowledge",
        "Learn from failures as growth opportunities",
        "Stay curious and ask questions",
        "Build projects to apply what you learned",
        "Read documentation and research papers"
    ],
    
    "coding": [
        "Write clean code with meaningful names",
        "Add comments explaining complex logic",
        "Test thoroughly with unit tests",
        "Use version control (Git) for all projects",
        "Read others' code to learn patterns",
        "Use linters and formatters",
        "Follow DRY principle: Don't Repeat Yourself"
    ],
    
    "programming": [
        "Master fundamentals before advanced topics",
        "Practice daily on LeetCode or HackerRank",
        "Build real-world projects",
        "Understand data structures and algorithms",
        "Learn time and space complexity",
        "Use debugging tools effectively",
        "Keep learning new languages and frameworks"
    ],
    
    "machine learning": [
        "Master Python and libraries (NumPy, Pandas, Scikit-learn)",
        "Understand statistics and linear algebra",
        "Learn supervised and unsupervised learning",
        "Study deep learning frameworks (TensorFlow, PyTorch)",
        "Work on data cleaning and preprocessing",
        "Learn model evaluation and hyperparameter tuning",
        "Build end-to-end projects"
    ],
    
    "career": [
        "Build a strong portfolio with impressive projects",
        "Contribute to open-source projects",
        "Network with developers at meetups and conferences",
        "Keep learning relevant technologies",
        "Practice coding interviews and system design",
        "Build communication skills",
        "Seek mentorship from experienced developers"
    ],
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def find_answer_in_kb(question):
    """Search knowledge base for matching answer"""
    question_lower = question.lower()
    
    for key, answer in KNOWLEDGE_BASE.items():
        if key.lower() in question_lower:
            return answer
    
    return None

def find_advice(topic):
    """Find advice for a given topic"""
    topic_lower = topic.lower()
    
    for key, advice_list in ADVICE_DATABASE.items():
        if key.lower() in topic_lower:
            return advice_list
    
    return None

def is_valid_qa_response(response_text):
    """Check if QA response is meaningful"""
    if not response_text or len(response_text) < 15:
        return False
    
    generic_responses = ["i understand", "unclear", "not sure", "please provide"]
    response_lower = response_text.lower()
    
    for pattern in generic_responses:
        if pattern in response_lower and len(response_text) < 80:
            return False
    
    return True

def format_summary(summary_text):
    """Format summary with bullet points"""
    sentences = summary_text.split('. ')
    formatted = ""
    
    for sentence in sentences:
        if sentence.strip():
            formatted += f"• {sentence.strip()}\n"
    
    return formatted

def save_conversation(function_type, user_input, response):
    """Save conversation to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO conversations (function_type, user_input, ai_response, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (function_type, user_input, response, datetime.now()))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/answer-question', methods=['POST'])
def answer_question():
    """Answer questions using knowledge base + QA model"""
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'success': False, 'error': 'Question required'}), 400
        
        # Check knowledge base first
        kb_answer = find_answer_in_kb(question)
        if kb_answer:
            save_conversation('answer_question', question, kb_answer)
            return jsonify({
                'success': True,
                'question': question,
                'response': kb_answer,
                'model': 'Knowledge Base',
                'timestamp': datetime.now().isoformat()
            })
        
        # Use QA model
        if qapipeline:
            context = """
            AI and machine learning are revolutionizing technology. Python is essential for AI development.
            Web development uses JavaScript, React, Flask, and Node.js. Tech careers require programming skills.
            Machine learning involves supervised, unsupervised, and reinforcement learning. Databases use SQL and NoSQL.
            Cloud platforms include AWS, Azure, and GCP. APIs enable system communication.
            """
            
            result = qapipeline(question=question, context=context)
            response = result.get('answer', '').strip()
            
            if not is_valid_qa_response(response):
                response = "I'm not trained for this topic. Try asking about AI, programming, tech careers, or learning!"
        else:
            response = "I'm not trained for this topic. Try asking about AI, programming, tech careers, or learning!"
        
        save_conversation('answer_question', question, response)
        
        return jsonify({
            'success': True,
            'question': question,
            'response': response,
            'model': 'AI Model',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': 'Processing error. Please try again.'}), 500

@app.route('/api/summarize-text', methods=['POST'])
def summarize_text():
    """Summarize given text"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text or len(text) < 50:
            return jsonify({'success': False, 'error': 'Text must be at least 50 characters'}), 400
        
        if not summarizer:
            return jsonify({'success': False, 'error': 'Summarization model not available'}), 500
        
        summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
        summary_text = summary[0]['summary_text']
        formatted_summary = format_summary(summary_text)
        
        save_conversation('summarize_text', text[:100] + '...', summary_text)
        
        return jsonify({
            'success': True,
            'original_length': len(text),
            'summary': formatted_summary,
            'summary_length': len(summary_text),
            'compression_ratio': f"{round((len(summary_text)/len(text))*100, 1)}%",
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': 'Summarization failed. Try shorter text.'}), 500

@app.route('/api/generate-creative', methods=['POST'])
def generate_creative():
    """Generate creative content"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        content_type = data.get('content_type', 'story')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt required'}), 400
        
        if not textgenerator:
            return jsonify({'success': False, 'error': 'Text generation model not available'}), 500
        
        if content_type == 'story':
            full_prompt = f"Once upon a time, {prompt}. The story continues with "
            max_len = 200
        elif content_type == 'poem':
            full_prompt = f"A beautiful poem about {prompt}:\n"
            max_len = 150
        else:
            full_prompt = f"An essay about {prompt}:\n"
            max_len = 250
        
        result = textgenerator(
            full_prompt, 
            max_length=max_len,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.9,
            temperature=0.8
        )
        
        generated_text = result[0]['generated_text'].replace(full_prompt, '').strip()
        
        save_conversation('generate_creative', prompt, generated_text)
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'content_type': content_type,
            'generated_text': generated_text,
            'length': len(generated_text),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': 'Generation failed. Try a different prompt.'}), 500

@app.route('/api/get-advice', methods=['POST'])
def get_advice():
    """Provide advice on various topics"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic required'}), 400
        
        advice_list = find_advice(topic)
        
        if not advice_list:
            advice_list = [
                "Research the topic thoroughly",
                "Seek advice from experienced professionals",
                "Practice consistently",
                "Learn from your experiences",
                "Keep improving and adapting"
            ]
        
        advice_text = '\n'.join(advice_list)
        save_conversation('get_advice', topic, advice_text)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'advice': advice_list,
            'full_text': advice_text,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': 'Error retrieving advice.'}), 500

@app.route('/api/feedback', methods=['POST'])
def save_feedback():
    """Save user feedback"""
    try:
        data = request.json
        function_type = data.get('function_type')
        helpful = data.get('helpful')
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute('''
            UPDATE conversations 
            SET helpful = ? 
            WHERE function_type = ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (1 if helpful == 'yes' else 0, function_type))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Feedback saved!'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Server error'}), 500

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("="*60)
    print("AI Assistant - Built by Chethan Chirag M")
    print(f"Running on PORT: {port}")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)