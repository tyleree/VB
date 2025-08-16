from flask import Flask, render_template, request, jsonify
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import os

app = Flask(__name__)
pc = Pinecone(api_key=os.getenv("pcsk_4iKPMf_FVi5ZRfyXdqAaL98LFFUP3TGfp4CntYVRsxHgG7NjtoapPKE5f7jCkkpzgnE2NK"))
assistant = pc.assistant.Assistant(assistant_name=os.getenv("vb"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    prompt = request.json.get("prompt", "")
    resp = assistant.chat(messages=[Message(role="user", content=prompt)], include_highlights=True)
    return jsonify({
        "content": resp.message.content,
        "citations": [{
            "file": c.references[0].file.name,
            "page": c.references[0].pages[0],
            "url": f"{c.references[0].file.signed_url}#page={c.references[0].references[0].pages[0]}" 
        } for c in resp.citations]
    })

if __name__ == "__main__":
    app.run(debug=True)
