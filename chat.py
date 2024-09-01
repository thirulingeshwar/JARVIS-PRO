# Import necessary modules
from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import wikipediaapi
import re
import string

# Initialize the Flask app and Wikipedia API
app = Flask(__name__)
wiki_wiki = wikipediaapi.Wikipedia('en')

def normalize_input(query):
    """Normalizes user input for consistent processing: lowercasing, removing punctuation."""
    query = query.lower().strip()  # Convert to lowercase and strip whitespace
    query = re.sub(rf'[{string.punctuation}]', '', query)  # Remove punctuation
    return query

def extract_keywords(query):
    """Extracts the main keywords from the user query for searching."""
    query = normalize_input(query)
    # Define common phrases to remove
    common_phrases = ["what is", "who is", "define", "tell me about", "how is"]
    for phrase in common_phrases:
        query = query.replace(phrase, "")
    return query.strip()

def search_wikipedia(query):
    """Searches Wikipedia for the given query and returns the summary of the page."""
    page = wiki_wiki.page(query)
    if page.exists():
        return page.summary[:500]  # Limiting to 500 characters
    else:
        return "Sorry, I couldn't find any information on Wikipedia."

def search_google(query):
    """Searches Google for the given query and returns the title and link of the first result."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the first search result
    search_results = soup.find_all('h3')
    if search_results:
        result_title = search_results[0].get_text()
        link_tag = search_results[0].find_parent('a', href=True)
        result_link = link_tag['href'] if link_tag else "No link found"
        return f"{result_title}\n{result_link}"
    else:
        return "Sorry, I couldn't find any relevant information on Google."

def search_bing(query):
    """Searches Bing for the given query and returns the title and link of the first result."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(f"https://www.bing.com/search?q={query}", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the first search result
    search_results = soup.find_all('li', {'class': 'b_algo'})
    if search_results:
        result_title = search_results[0].find('h2').get_text()
        link_tag = search_results[0].find('a', href=True)
        result_link = link_tag['href'] if link_tag else "No link found"
        return f"{result_title}\n{result_link}"
    else:
        return "Sorry, I couldn't find any relevant information on Bing."

def handle_query(query):
    """Handles user queries and decides whether to search Wikipedia or other search engines."""
    keywords = extract_keywords(query)
    
    # First, try Wikipedia with extracted keywords
    wiki_response = search_wikipedia(keywords)
    if "couldn't find" not in wiki_response:
        return wiki_response
    
    # If Wikipedia didn't provide a good answer, use Google and Bing
    google_response = search_google(keywords)
    if "couldn't find" not in google_response:
        return google_response

    bing_response = search_bing(keywords)
    return bing_response

# Define the home route
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sci-Fi Chat Box</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: radial-gradient(circle, #0b0c10, #1f2833);
            font-family: 'Orbitron', sans-serif;
            color: #c5c6c7;
            overflow: hidden;
        }
        .chat-container {
            width: 90%;
            max-width: 500px;
            height: 80%;
            background: rgba(31, 40, 51, 0.8);
            border: 2px solid #45a29e;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            display: flex;
            flex-direction: column;
            position: relative;
        }
        .chat-header {
            background: linear-gradient(90deg, #0b0c10, #1f2833);
            padding: 20px;
            border-bottom: 2px solid #45a29e;
            color: #66fcf1;
            font-size: 24px;
            text-align: center;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.4);
        }
        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            border-bottom: 2px solid #45a29e;
            background: rgba(31, 40, 51, 0.9);
            box-shadow: inset 0 0 15px rgba(0, 255, 255, 0.1);
            color: #c5c6c7;
        }
        .message {
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        .message p {
            margin: 0;
            padding: 10px 20px;
            background: #0b0c10;
            border-radius: 20px;
            box-shadow: 0 0 10px rgba(102, 252, 241, 0.5);
            color: #66fcf1;
        }
        .message.sent p {
            background: #45a29e;
            text-align: right;
            box-shadow: 0 0 10px rgba(69, 162, 158, 0.5);
        }
        .chat-input {
            padding: 20px;
            border-top: 2px solid #45a29e;
            background: linear-gradient(90deg, #0b0c10, #1f2833);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom-left-radius: 15px;
            border-bottom-right-radius: 15px;
        }
        .chat-input input {
            flex: 1;
            padding: 10px 15px;
            border: none;
            border-radius: 20px;
            background: #1f2833;
            color: #c5c6c7;
            box-shadow: inset 0 0 10px rgba(0, 255, 255, 0.2);
        }
        .chat-input button {
            margin-left: 10px;
            padding: 10px 20px;
            border: none;
            border-radius: 20px;
            background: #45a29e;
            color: #0b0c10;
            cursor: pointer;
            transition: background 0.3s;
            box-shadow: 0 0 10px rgba(69, 162, 158, 0.5);
        }
        .chat-input button:hover {
            background: #66fcf1;
        }
        .footer-text {
            text-align: center;
            color: #45a29e;
            padding: 10px 0;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">JARVIS PRO Chat</div>
        <div class="chat-messages" id="chat-messages">
            <div class="message"><p>Welcome, user. How may I assist you today?</p></div>
        </div>
        <div class="chat-input">
            <input type="text" id="message-input" placeholder="Type your message...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    <div class="footer-text">by: K. Thirulingeshwar</div>

    <script>
        function sendMessage() {
            const messageInput = document.getElementById('message-input');
            const chatMessages = document.getElementById('chat-messages');
            const userMessage = messageInput.value.trim();
            if (!userMessage) return;

            // Display user message
            const userMessageDiv = document.createElement('div');
            userMessageDiv.classList.add('message', 'sent');
            userMessageDiv.innerHTML = `<p>${userMessage}</p>`;
            chatMessages.appendChild(userMessageDiv);

            // Scroll to the bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Send message to server
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
            })
            .then(response => response.text())
            .then(data => {
                const aiMessageDiv = document.createElement('div');
                aiMessageDiv.classList.add('message');
                aiMessageDiv.innerHTML = `<p>${data}</p>`;
                chatMessages.appendChild(aiMessageDiv);

                // Scroll to the bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            });

            // Clear input field
            messageInput.value = '';
        }

        // Allow pressing Enter to send a message
        document.getElementById('message-input').addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>

    ''')

# Define a route to handle chat messages
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = handle_query(user_message)
    return response

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
