"""
AI Assistant - Professional Edition (ENHANCED - FINAL)
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

# Load AI Models
print("Loading AI Models (first time takes 2-3 minutes)...")

try:
    qa_pipeline = pipeline("question-answering", 
                          model="deepset/roberta-base-squad2")
    print("✅ Question Answering model loaded")
except Exception as e:
    print(f"⚠️ QA Model error: {e}")
    qa_pipeline = None

try:
    summarizer = pipeline("summarization", 
                         model="facebook/bart-large-cnn")
    print("✅ Summarization model loaded")
except Exception as e:
    print(f"⚠️ Summarization model error: {e}")
    summarizer = None

try:
    text_generator = pipeline("text-generation", 
                             model="gpt2-medium",
                             max_length=300,
                             do_sample=True,
                             top_p=0.95,
                             temperature=0.8)
    print("✅ Text Generation model loaded")
except Exception as e:
    print(f"⚠️ Text Generation model error: {e}")
    text_generator = None

print("\n✅ All models loaded successfully!\n")


# ============================================
# COMPREHENSIVE KNOWLEDGE BASE (ENHANCED)
# ============================================

KNOWLEDGE_BASE = {
    # AI & ML Topics
    "artificial intelligence": "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines. It enables systems to learn from data, recognize patterns, make decisions with minimal human intervention, and improve over time. AI is revolutionizing healthcare, finance, transportation, and countless other industries. Key applications include computer vision, natural language processing, robotics, and autonomous systems.",
    
    "machine learning": "Machine Learning is a subset of AI where systems improve their performance through experience without being explicitly programmed. It uses algorithms to analyze data, identify patterns, and make predictions. Types include supervised learning (labeled data), unsupervised learning (unlabeled data), and reinforcement learning (rewards/penalties). Common applications include recommendation systems, fraud detection, image recognition, and autonomous vehicles.",
    
    "deep learning": "Deep Learning uses artificial neural networks with multiple layers to learn complex patterns in large datasets. It powers modern breakthroughs in computer vision, natural language processing, and speech recognition. Popular architectures include CNNs (Convolutional Neural Networks), RNNs (Recurrent Neural Networks), and Transformers. Deep learning requires significant computational power and large amounts of training data.",
    
    "neural network": "Neural networks are computing systems inspired by biological neurons. They consist of interconnected nodes (neurons) organized in layers: input layer, hidden layers, and output layer. Each connection has a weight that adjusts during training using backpropagation. Neural networks can learn non-linear relationships and are fundamental to modern deep learning and AI applications.",
    
    "transformer": "Transformers are neural network architectures using attention mechanisms to process sequential data efficiently. They power state-of-the-art models like BERT, GPT, and T5. Unlike RNNs, transformers can process data in parallel, making them faster and better at capturing long-range dependencies. Transformers revolutionized NLP and have applications in computer vision and other domains.",
    
    "natural language processing": "NLP is a field of AI that helps computers understand, interpret, and generate human language. Applications include chatbots, machine translation, sentiment analysis, text classification, question answering, and information extraction. Modern NLP uses transformer-based models and deep learning. Key techniques include tokenization, embeddings, and attention mechanisms.",
    
    # Programming Languages & Tools
    "python": "Python is a high-level, interpreted programming language known for simplicity and readability. It's the leading language for AI, data science, web development, automation, and scientific computing. Python has extensive libraries like NumPy, Pandas, TensorFlow, PyTorch, and Scikit-learn. Features: dynamic typing, large standard library, strong community support, and cross-platform compatibility.",
    
    "flask": "Flask is a lightweight Python web framework for building web applications and REST APIs. It follows the WSGI standard and provides flexibility for both small and large projects. Flask uses Jinja2 templating and Werkzeug WSGI toolkit. Perfect for rapid development, microservices, and integrating with machine learning models. Minimal but extensible with blueprints and plugins.",
    
    "javascript": "JavaScript is a versatile programming language primarily used for web development. It runs in web browsers and enables interactive web applications. Modern JavaScript (ES6+) includes features like arrow functions, classes, promises, and async/await. Node.js allows using JavaScript for backend development. Frameworks: React, Vue, Angular for frontend; Express for backend.",
    
    "react": "React is a JavaScript library for building user interfaces using reusable components. Developed by Facebook, React uses a virtual DOM for efficient rendering and state management. Features: component-based architecture, one-way data binding, JSX syntax, hooks for state management. Ideal for single-page applications (SPAs), progressive web apps, and large-scale applications.",
    
    "node.js": "Node.js is a JavaScript runtime built on Chrome's V8 engine. It allows developers to use JavaScript for backend development with high performance and scalability. Uses event-driven, non-blocking I/O model. Perfect for building scalable network applications, real-time applications, streaming applications, and APIs. Popular frameworks: Express, NestJS, Fastify.",
    
    "sql": "SQL (Structured Query Language) is used for managing and querying relational databases. It enables data retrieval (SELECT), insertion (INSERT), updates (UPDATE), and deletion (DELETE) operations. Features: joins, aggregations, subqueries, indexes, transactions. DBMS examples: PostgreSQL, MySQL, Oracle, SQL Server. Essential for backend development and data analysis.",
    
    # Career & Skills
    "tech career": "A tech career offers diverse opportunities and high earning potential. Key skills needed: programming languages (Python, JavaScript, Java), data structures and algorithms, system design, databases (SQL/NoSQL), web development frameworks, cloud platforms (AWS, Azure, GCP), and soft skills (communication, problem-solving, teamwork). Popular roles: software engineer, data scientist, DevOps engineer, full-stack developer, machine learning engineer.",
    
    "career options in ai": "Career options in AI include: Machine Learning Engineer (design and train AI models), Data Scientist (analyze data and build models), AI Researcher (develop new algorithms), NLP Engineer (natural language processing), Computer Vision Engineer (image/video processing), AI Product Manager, AI Ethics Specialist. Requirements: strong math/statistics, programming skills, deep learning knowledge, domain expertise.",
    
    "tech skills": "Essential tech skills include: programming (Python, JavaScript, Java), version control (Git), databases (SQL, MongoDB), web development (HTML/CSS, frameworks), cloud platforms (AWS, Azure), DevOps (Docker, Kubernetes), system design, data structures & algorithms, API design, testing & debugging. Soft skills: communication, problem-solving, teamwork, continuous learning.",
    
    # Geography
    "paris": "Paris is the capital and largest city of France. Located in the north-central part of the country on the Seine River. Known as the 'City of Light' for its beautiful architecture and innovative street lighting. Famous landmarks: Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, Arc de Triomphe, Sacré-Cœur. Home to world-class art museums, restaurants, and fashion centers.",
    
    "london": "London is the capital and largest city of the United Kingdom. Located on the River Thames in southeastern England. Major global financial and cultural center. Landmarks: Big Ben, Tower Bridge, Tower of London, Buckingham Palace, Westminster Abbey. Known for diverse culture, historic sites, museums, theater (West End), and modern architecture.",
    
    "tokyo": "Tokyo is the capital and largest metropolitan area in Japan. The political, economic, and cultural center of Japan. Known for advanced technology, traditional temples, bustling markets, modern skyscrapers, and vibrant nightlife. Landmarks: Tokyo Tower, Senso-ji Temple, Shibuya Crossing, Meiji Shrine, modern shopping districts.",
    
    "new delhi": "New Delhi is the capital of India, located in northern India. Seat of the Indian government and home to the President's residence and Parliament. Major cultural, political, and economic hub with significant historical importance. Landmarks: India Gate, Raj Ghat, Rashtrapati Bhavan, Jama Masjid, Red Fort.",
    
    "washington": "Washington, D.C. is the capital of the United States. Located on the east coast, it serves as the seat of the federal government. Home to the White House, Capitol Building, Supreme Court, and world-class museums including the Smithsonian Institution. Major landmarks: Lincoln Memorial, Washington Monument, Library of Congress.",
}


# ============================================
# ADVICE DATABASE (ENHANCED)
# ============================================

ADVICE_DATABASE = {
    "studying": [
        "Create a detailed study schedule and stick to it consistently",
        "Break information into smaller, manageable chunks for better retention",
        "Use active recall and spaced repetition techniques for long-term memory",
        "Find a quiet, distraction-free study environment with good lighting",
        "Take regular breaks using the Pomodoro Technique (25 min work, 5 min break)",
        "Review material multiple times before exams using different study methods",
        "Form study groups to explain concepts to peers and learn from others"
    ],
    
    "productivity": [
        "Set clear, measurable, and time-bound goals for each day and week",
        "Prioritize tasks by importance and urgency using the Eisenhower matrix",
        "Use time-blocking to allocate specific time slots for focused work",
        "Eliminate distractions: silence notifications and block social media",
        "Track your progress daily and review accomplishments regularly",
        "Use productivity tools like Todoist, Notion, or Asana for task management",
        "Start your day with the most important or challenging task first"
    ],
    
    "learning": [
        "Choose the learning method that works for you (visual, auditory, kinesthetic)",
        "Practice consistently and deliberately with specific goals and feedback",
        "Teach others to reinforce your own knowledge and identify gaps",
        "Learn from failures and mistakes as opportunities for growth",
        "Stay curious and ask questions when concepts are unclear",
        "Build projects to apply what you've learned in practical scenarios",
        "Read documentation, source code, and research papers to deepen knowledge"
    ],
    
    "coding": [
        "Write clean, readable code with meaningful variable names and comments",
        "Comment your code explaining complex logic and design decisions",
        "Test your code thoroughly with unit tests and integration tests",
        "Use version control (Git) for all projects to track changes",
        "Read other people's code to learn best practices and patterns",
        "Use linters and formatters to maintain consistent code style",
        "Follow the DRY principle: Don't Repeat Yourself, use functions and modules"
    ],
    
    "tech career": [
        "Build a strong portfolio with 5-10 impressive projects showcasing your skills",
        "Contribute to open-source projects to gain real-world experience",
        "Network with other developers through meetups, conferences, and online communities",
        "Keep learning new technologies and frameworks relevant to your field",
        "Practice coding interviews and system design problems for interviews",
        "Build strong communication skills to explain technical concepts clearly",
        "Seek mentorship from experienced developers in your desired field"
    ],
    
    "programming": [
        "Master programming fundamentals before diving into advanced topics",
        "Practice problem-solving daily on LeetCode, HackerRank, or CodeSignal",
        "Build real-world projects to apply your skills and create a portfolio",
        "Understand data structures (arrays, lists, trees, graphs, hash tables)",
        "Learn algorithms and their time/space complexity for optimization",
        "Use debugging tools effectively to find and fix bugs quickly",
        "Keep learning new languages, frameworks, and development practices"
    ],
    
    "machine learning": [
        "Master Python programming and essential libraries (NumPy, Pandas, Scikit-learn)",
        "Understand statistics and linear algebra for ML mathematics",
        "Learn supervised learning (regression, classification) and unsupervised learning",
        "Understand deep learning frameworks like TensorFlow and PyTorch",
        "Work with datasets: data cleaning, preprocessing, feature engineering",
        "Learn model evaluation techniques: cross-validation, metrics, hyperparameter tuning",
        "Build projects from data collection through model deployment"
    ],
    
    "exam preparation": [
        "Start studying 4-6 weeks before the exam with a structured plan",
        "Create a detailed study schedule breaking down topics by difficulty",
        "Practice with previous years' question papers and mock tests",
        "Take multiple mock tests to assess your readiness and identify weak areas",
        "Focus on understanding concepts, not just memorizing facts",
        "Sleep well the night before the exam for better focus and memory",
        "Stay calm and confident during the exam, manage your time wisely"
    ]
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
    """Check if QA response is meaningful (not just defaults)"""
    # If response is too short or seems generic, consider it invalid
    if not response_text or len(response_text) < 15:
        return False
    
    # Check for common default/empty responses
    generic_responses = [
        "i understand",
        "could you provide",
        "please provide",
        "more specific information",
        "unclear",
        "not sure"
    ]
    
    response_lower = response_text.lower()
    
    # If it matches generic patterns, it's likely untrained
    for pattern in generic_responses:
        if pattern in response_lower and len(response_text) < 80:
            return False
    
    return True


def format_poem(text):
    """Format generated text as a proper poem with stanzas"""
    lines = text.split('.')
    poem_lines = []
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 5:
            poem_lines.append(line)
    
    # Group into stanzas
    stanzas = []
    for i in range(0, len(poem_lines), 4):
        stanza = '\n'.join(poem_lines[i:i+4])
        stanzas.append(stanza)
    
    return '\n\n'.join(stanzas) if stanzas else text


def format_summary(summary_text):
    """Format summary with bullet points"""
    sentences = summary_text.split('. ')
    formatted = ""
    
    for sentence in sentences:
        if sentence.strip():
            formatted += f"• {sentence.strip()}\n"
    
    return formatted


# ============================================
# API Routes
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
        
        # Check knowledge base first (PRIORITY)
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
        
        # Use QA model with expanded context
        if qa_pipeline:
            context = """
            Artificial Intelligence powers modern technology with machine learning and deep learning algorithms.
            Python is essential for AI/ML development with TensorFlow and PyTorch libraries.
            Web development uses JavaScript, React, Flask, and Node.js for building applications.
            Tech careers require strong programming skills, problem-solving ability, and continuous learning.
            Machine learning involves supervised learning, unsupervised learning, and deep neural networks.
            Data science requires understanding statistics, data analysis, and visualization.
            Cloud platforms like AWS, Azure, GCP provide infrastructure for scalable applications.
            APIs enable communication between systems using REST, GraphQL, or gRPC protocols.
            Databases include relational (SQL) and non-relational (NoSQL) options for data storage.
            Software engineering best practices: version control, testing, code review, documentation.
            """
            
            result = qa_pipeline(question=question, context=context)
            response = result.get('answer', '').strip()
            
            # Check if response is valid/meaningful
            if not is_valid_qa_response(response):
                response = "I'm not trained for this topic. Try asking about AI, programming, tech careers, or other related subjects!"
        else:
            response = "I'm not trained for this topic. Try asking about AI, programming, tech careers, or other related subjects!"
        
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
        
        if not text_generator:
            return jsonify({'success': False, 'error': 'Text generation model not available'}), 500
        
        if content_type == 'story':
            full_prompt = f"Once upon a time, there was {prompt}. The story begins when "
            min_len = 100
            max_len = 350
        elif content_type == 'poem':
            full_prompt = f"A beautiful poem about {prompt}:\n\n"
            min_len = 80
            max_len = 280
        else:
            full_prompt = f"An informative essay on {prompt}:\n\nIntroduction:\n{prompt} is an important topic. "
            min_len = 120
            max_len = 400
        
        result = text_generator(
            full_prompt, 
            max_length=max_len,
            min_length=min_len,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.92,
            temperature=0.85,
            repetition_penalty=1.2
        )
        
        generated_text = result[0]['generated_text']
        
        lines = generated_text.split('. ')
        unique_lines = []
        seen = set()
        
        for line in lines:
            line_clean = line.strip().lower()
            if line_clean and line_clean not in seen and len(line_clean) > 5:
                unique_lines.append(line + '. ')
                seen.add(line_clean)
        
        if len(unique_lines) > 15:
            unique_lines = unique_lines[:15]
        
        generated_text = ''.join(unique_lines).strip()
        
        if content_type == 'poem':
            generated_text = format_poem(generated_text)
        
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
        
        # Check advice database
        advice_list = find_advice(topic)
        
        if not advice_list:
            advice_list = [
                "Research the topic thoroughly to understand it deeply",
                "Seek advice from experienced professionals in the field",
                "Practice what you learn consistently and deliberately",
                "Reflect on your experiences and lessons learned",
                "Keep improving and adapting your approach"
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


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Server error'}), 500


# ============================================
# Run Server
# ============================================

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("="*60)
    print(f"AI Assistant - Built by Chethan Chirag M")
    print(f"Running on PORT: {port}")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)