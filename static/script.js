const API_BASE = '/api';
const messagesDiv = document.getElementById('messages');
const inputPanels = document.querySelectorAll('.input-panel');
const menuItems = document.querySelectorAll('.menu-item');
const loadingSpinner = document.getElementById('loadingSpinner');
const feedbackMenu = document.getElementById('feedbackMenu');

let lastFunction = '';
let lastMessageElement = null;

// Loading messages
const loadingMessages = [
    'Thinking...',
    'Analyzing...',
    'Processing...',
    'Finding answer...',
    'One moment...',
    'Almost there...'
];

function showLoading() {
    const randomMsg = loadingMessages[Math.floor(Math.random() * loadingMessages.length)];
    document.getElementById('loadingText').textContent = randomMsg;
    loadingSpinner.classList.remove('hidden');
}

function hideLoading() {
    loadingSpinner.classList.add('hidden');
}

// Sidebar menu switching
menuItems.forEach(item => {
    item.addEventListener('click', () => {
        const tab = item.dataset.tab;
        
        menuItems.forEach(m => m.classList.remove('active'));
        item.classList.add('active');
        
        inputPanels.forEach(p => p.classList.remove('active'));
        document.getElementById(tab).classList.add('active');
        
        const titles = {
            questions: { title: 'Ask Anything', desc: 'Get accurate answers to any question' },
            summarize: { title: 'Summarize Text', desc: 'Extract key points from articles and documents' },
            creative: { title: 'Create Content', desc: 'Write stories, poems, and essays' },
            advice: { title: 'Get Advice', desc: 'Professional recommendations on any topic' },
            guide: { title: 'User Guide', desc: 'Learn how to use all features' }
        };
        
        document.getElementById('chat-title').textContent = titles[tab].title;
        document.getElementById('chat-desc').textContent = titles[tab].desc;
        
        // Hide feedback menu when switching tabs
        hideFeedbackMenu();
    });
});

// Clear chat
function clearChat() {
    messagesDiv.innerHTML = `
        <div class="message assistant-msg welcome">
            <div class="message-content">
                <h2>Welcome to AI Assistant</h2>
                <p>Powered by Advanced AI Models</p>
                <p style="font-size: 13px; color: #9ca3af; margin-top: 8px;">Ask questions, summarize text, create content, or get advice.</p>
                <div class="quick-prompts">
                    <button class="prompt-btn" onclick="askQuestion('What are essential programming skills for a tech career?')">Tech Career</button>
                    <button class="prompt-btn" onclick="askQuestion('How do neural networks work?')">Neural Networks</button>
                    <button class="prompt-btn" onclick="askQuestion('Explain machine learning in simple terms')">Machine Learning</button>
                </div>
            </div>
        </div>
    `;
    hideFeedbackMenu();
}

// Add message to chat
function addMessage(content, isUser = false) {
    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user-msg' : 'assistant-msg'}`;
    div.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return div;
}

// Show feedback menu in chat
function showFeedbackMenu() {
    feedbackMenu.classList.remove('hidden');
    messagesDiv.appendChild(feedbackMenu);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideFeedbackMenu() {
    feedbackMenu.classList.add('hidden');
}

// Submit feedback
function submitFeedback(helpful) {
    fetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            function_type: lastFunction,
            helpful: helpful
        })
    }).then(r => r.json())
      .then(data => {
          // Brief feedback confirmation
          const oldText = feedbackMenu.querySelector('.feedback-label').textContent;
          feedbackMenu.querySelector('.feedback-label').textContent = helpful === 'yes' ? '✅ Thanks for feedback!' : '👍 Noted!';
          
          setTimeout(() => {
              feedbackMenu.querySelector('.feedback-label').textContent = oldText;
          }, 2000);
      })
      .catch(e => console.error('Feedback error:', e));
}

// Ask question
async function askQuestion(question = null) {
    const input = question || document.getElementById('questionInput').value.trim();
    
    if (!input) return;
    
    addMessage(input, true);
    document.getElementById('questionInput').value = '';
    
    showLoading();
    lastFunction = 'answer_question';
    
    try {
        const response = await fetch(`${API_BASE}/answer-question`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: input })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            addMessage(data.response, false);
            showFeedbackMenu();
        } else {
            addMessage('Error: ' + (data.error || 'Unable to process'), false);
        }
    } catch (error) {
        hideLoading();
        addMessage('Network error. Please try again.', false);
    }
}

// Summarize text
async function summarizeText() {
    const text = document.getElementById('textInput').value.trim();
    
    if (!text) return;
    
    addMessage(`Summarizing...`, true);
    
    showLoading();
    lastFunction = 'summarize_text';
    
    try {
        const response = await fetch(`${API_BASE}/summarize-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            const summaryMessage = `Summary:\n\n${data.summary}\n\nCompression: ${data.compression_ratio}`;
            addMessage(summaryMessage, false);
            showFeedbackMenu();
            document.getElementById('textInput').value = '';
        } else {
            addMessage('Error: ' + (data.error || 'Could not summarize'), false);
        }
    } catch (error) {
        hideLoading();
        addMessage('Network error. Please try again.', false);
    }
}

// Generate creative content
async function generateCreative() {
    const prompt = document.getElementById('creativePrompt').value.trim();
    const type = document.getElementById('contentType').value;
    
    if (!prompt) return;
    
    addMessage(`Creating ${type}...`, true);
    
    showLoading();
    lastFunction = 'generate_creative';
    
    try {
        const response = await fetch(`${API_BASE}/generate-creative`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, content_type: type })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            addMessage(data.generated_text, false);
            showFeedbackMenu();
            document.getElementById('creativePrompt').value = '';
        } else {
            addMessage('Error: ' + (data.error || 'Could not generate'), false);
        }
    } catch (error) {
        hideLoading();
        addMessage('Network error. Please try again.', false);
    }
}

// Get advice
async function getAdvice() {
    const topic = document.getElementById('adviceTopic').value.trim();
    
    if (!topic) return;
    
    addMessage(`Getting advice for: ${topic}...`, true);
    
    showLoading();
    lastFunction = 'get_advice';
    
    try {
        const response = await fetch(`${API_BASE}/get-advice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            const adviceText = data.advice.map((item, i) => `${i + 1}. ${item}`).join('\n');
            addMessage(adviceText, false);
            showFeedbackMenu();
            document.getElementById('adviceTopic').value = '';
        } else {
            addMessage('Error: ' + (data.error || 'Could not retrieve advice'), false);
        }
    } catch (error) {
        hideLoading();
        addMessage('Network error. Please try again.', false);
    }
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// ============================================
// KEYBOARD SUPPORT
// ============================================

document.getElementById('questionInput')?.addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        askQuestion();
    }
});

document.getElementById('textInput')?.addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        summarizeText();
    }
});

document.getElementById('creativePrompt')?.addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        generateCreative();
    }
});

document.getElementById('adviceTopic')?.addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        getAdvice();
    }
});

// Disable/enable inputs during processing
function disableInputs(disabled = true) {
    const buttons = document.querySelectorAll('.send-btn');
    buttons.forEach(btn => btn.disabled = disabled);
}

const originalShowLoading = showLoading;
showLoading = function() {
    originalShowLoading();
    disableInputs(true);
};

const originalHideLoading = hideLoading;
hideLoading = function() {
    originalHideLoading();
    disableInputs(false);
};