import os
import asyncio
import json
import pickle
import fitz
import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from transformers import pipeline
from flask import Flask, request, jsonify
from flask_cors import CORS

# ------------------ Configuration ------------------ #
os.environ["GOOGLE_API_KEY"] = "AIzaSyAyFvbsVvDeEqqfiisSLU9aQQqZ9-83Wcs"  # Replace with real key
pdf_folder = "/Users/kirtipatel/Downloads/ai_chatbot/backend/data/"
chunks_file = os.path.join(pdf_folder, "pdf_chunks.json")
dataset_file = os.path.join(pdf_folder, "enhanced_qa_dataset.json")
index_path = os.path.join(pdf_folder, "faiss_index.pkl")
pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Zero-shot intent classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# ------------------ Utilities ------------------ #

async def chunk_text(text, chunk_size=512, overlap=100):
    if len(text) <= chunk_size:
        return [text]
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]

async def extract_text_async(pdf_path, executor):
    loop = asyncio.get_event_loop()
    def extract(pdf_path):
        try:
            doc = fitz.open(pdf_path)
            text = "".join(page.get_text("text") or "" for page in doc)
            doc.close()
            return text
        except Exception as e:
            print(f"⚠️ Failed to extract {pdf_path}: {e}")
            return ""
    return await loop.run_in_executor(executor, extract, pdf_path)

def fetch_legal_web_content(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        print(f"⚠️ Failed to fetch from {url}: {e}")
        return ""

# ------------------ Data Preparation ------------------ #

async def load_and_chunk_pdfs():
    if os.path.exists(chunks_file):
        with open(chunks_file, "r") as f:
            pages = json.load(f)
        print(f"✅ Loaded {len(pages)} chunks from cache")
        return pages

    pages = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [extract_text_async(pdf, executor) for pdf in pdf_files]
        results = await asyncio.gather(*tasks)
        for pdf, raw_text in zip(pdf_files, results):
            if raw_text:
                chunks = await chunk_text(raw_text)
                pages.extend(chunks)
                print(f"✅ Processed {pdf} with {len(chunks)} chunks")

    # Optional: Web URLs
    web_urls = ["https://indiankanoon.org/doc/123456/"]  # Add more as needed
    for url in web_urls:
        web_text = fetch_legal_web_content(url)
        if web_text:
            chunks = await chunk_text(web_text)
            pages.extend(chunks)
            print(f"✅ Added {len(chunks)} chunks from {url}")

    with open(chunks_file, "w") as f:
        json.dump(pages, f)
    return pages

async def create_or_load_vector_store():
    if os.path.exists(index_path):
        with open(index_path, "rb") as f:
            db = pickle.load(f)
        print(f"✅ Loaded FAISS index")
    else:
        pages = await load_and_chunk_pdfs()
        if not pages:
            print("❌ No text found in PDFs or web content.")
            exit()
        db = FAISS.from_texts(texts=pages, embedding=embedding_model)
        with open(index_path, "wb") as f:
            pickle.dump(db, f)
        print(f"✅ Created FAISS index with {len(pages)} chunks")
    return db

# ------------------ Intent + Legal Logic ------------------ #

def detect_intent(query):
    labels = ["penalty", "procedure", "eligibility", "general"]
    result = classifier(query, candidate_labels=labels)
    return result["labels"][0]

def is_judiciary_related(query):
    keywords = {
        "law", "court", "fine", "section", "ipc", "crpc", "motor", "divorce",
        "contract", "police", "judiciary", "legal", "act", "penalty", "case", "justice"
    }
    return any(k in query.lower() for k in keywords) or detect_intent(query) != "general"

# ------------------ Response Pipeline ------------------ #

async def generate_enhanced_response(query, db, conversation_history, user_type="layperson"):
    if not is_judiciary_related(query):
        return "This assistant is designed to answer judiciary-related questions. Please ask a legal query."

    try:
        intent = detect_intent(query)

        # Initial legal response generation
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", max_output_tokens=300)
        initial_prompt = f"""
        You are a legal assistant with expertise in Indian law. Provide a clear and practical response for a {user_type}, referencing laws like IPC, CrPC, or Motor Vehicles Act where relevant. Use bullet points if helpful.

        Query: {query}
        """
        initial_result = await llm.ainvoke(initial_prompt)
        initial_answer = initial_result.content.strip()

        # Vector search context
        relevant_docs = await asyncio.to_thread(db.similarity_search, query, k=3)
        pdf_context = "\n".join(doc.page_content for doc in relevant_docs) if relevant_docs else ""

        # Final response prompt
        final_prompt = f"""
        Enhance this response by combining legal reasoning and any useful references from prior context. Avoid duplication. Be precise and user-friendly.

        Query: {query}
        Intent: {intent}
        Legal Response Draft: {initial_answer}
        Related Documents: {pdf_context}
        Previous Conversation: {" ".join(conversation_history[-3:])}
        """
        final_result = await llm.ainvoke(final_prompt)
        enhanced_answer = final_result.content.strip()

        # Save for dataset
        dataset_entry = {
            "query": query,
            "intent": intent,
            "legal_reasoning": initial_answer,
            "pdf_context": pdf_context,
            "enhanced_answer": enhanced_answer
        }
        if os.path.exists(dataset_file):
            with open(dataset_file, "r") as f:
                dataset = json.load(f)
        else:
            dataset = []
        dataset.append(dataset_entry)
        with open(dataset_file, "w") as f:
            json.dump(dataset, f, indent=2)

        return enhanced_answer
    except Exception as e:
        return f"⚠️ Error generating response: {e}"

# ------------------ Flask App ------------------ #

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.get_json()
        query = data.get("message", "")
        user_type = data.get("user_type", "layperson")
        if not query:
            return jsonify({"reply": "No message provided"}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        db = loop.run_until_complete(create_or_load_vector_store())
        conversation_history = [query]
        reply = loop.run_until_complete(generate_enhanced_response(query, db, conversation_history, user_type))
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
