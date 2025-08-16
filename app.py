from flask import Flask, render_template, request, jsonify
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env.txt')  # Using env.txt since .env is blocked

app = Flask(__name__)

# Initialize Pinecone
try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    assistant = pc.assistant.Assistant(assistant_name=os.getenv("PINECONE_ASSISTANT_NAME"))
    print("✅ Pinecone initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Pinecone: {e}")
    assistant = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    if not assistant:
        return jsonify({"error": "Pinecone assistant not available"}), 500
    
    try:
        prompt = request.json.get("prompt", "")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Get response from Pinecone assistant
        resp = assistant.chat(
            messages=[Message(role="user", content=prompt)], 
            include_highlights=True
        )
        
        # Process citations
        citations = []
        if hasattr(resp, 'citations') and resp.citations:
            for citation in resp.citations:
                try:
                    citation_data = {
                        "file": citation.references[0].file.name if citation.references else "Unknown",
                        "page": citation.references[0].pages[0] if citation.references and citation.references[0].pages else 1,
                        "url": f"{citation.references[0].file.signed_url}#page={citation.references[0].references[0].pages[0]}" if citation.references and citation.references[0].file and citation.references[0].references else "#"
                    }
                    citations.append(citation_data)
                except Exception as e:
                    print(f"Error processing citation: {e}")
                    continue
        
        return jsonify({
            "content": resp.message.content,
            "citations": citations
        })
        
    except Exception as e:
        print(f"Error in ask endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "pinecone_available": assistant is not None,
        "environment": os.getenv("FLASK_ENV", "production")
    })

if __name__ == "__main__":
    print("🚀 Starting Veterans Benefits Assistant...")
    print(f"📁 Templates folder: {app.template_folder}")
    print(f"🔑 Pinecone API Key: {'✅ Set' if os.getenv('PINECONE_API_KEY') else '❌ Missing'}")
    print(f"🤖 Assistant Name: {os.getenv('PINECONE_ASSISTANT_NAME', 'Not set')}")
    
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get("PORT", 5000))
    
    app.run(debug=False, host='0.0.0.0', port=port)
