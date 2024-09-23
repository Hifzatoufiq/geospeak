from flask import Flask, render_template, request, make_response, jsonify
import openai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

# Set up OpenAI API key
api_key = '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'
openai.api_key = api_key

# In-memory history storage (or use a database for production)
translation_history = []

# Function to generate embedding for text
def generate_embedding(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    embedding_vector = response['data'][0]['embedding']
    return embedding_vector

# Dummy function to retrieve relevant documents from a vector database
def retrieve_documents(embedding_vector):
    # This function should query your FAISS or similar vector database
    relevant_docs = []  # Implement database query here
    return relevant_docs

# Create a context-aware translation prompt
def create_context_aware_prompt(text, relevant_docs, target_language):
    context = "\n".join(relevant_docs)
    return f"Translate the following English text to {target_language} considering the context:\n{context}\n\nText: {text}"

# Route to display the main page
@app.route('/')
def index():
    return render_template('index.html', history=translation_history)

# Route to handle the translation process
@app.route('/translate', methods=['POST'])
def translate():
    text = request.form['text']
    target_language = request.form['language']

    # Generate embedding and retrieve relevant documents (if any)
    embedding_vector = generate_embedding(text)
    relevant_docs = retrieve_documents(embedding_vector)
    translation_prompt = create_context_aware_prompt(text, relevant_docs, target_language)

    # Call OpenAI API for translation
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": translation_prompt}
            ]
        )
        translation = response['choices'][0]['message']['content'].strip()

        # Add to translation history
        history_entry = {
            'id': len(translation_history) + 1,  # Simple ID generation
            'text': text,
            'translated': translation,
            'language': target_language
        }
        translation_history.append(history_entry)
    except Exception as e:
        translation = f"Error during translation: {str(e)}"

    # Return the updated page with translation results
    return render_template('index.html', history=translation_history, translation=translation, selected_language=target_language)

# Route to handle downloading the translation result as a PDF
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    translation = request.form['translation']
    target_language = request.form['selected_language']

    # Create a PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f'Translation to {target_language}:')
    p.drawString(100, 730, translation)
    p.save()
    buffer.seek(0)

    # Send the PDF as a response
    response = make_response(buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=translation.pdf'
    response.headers['Content-Type'] = 'application/pdf'
    return response

@app.route('/delete_history/<int:entry_id>', methods=['DELETE'])
def delete_history_entry(entry_id):
    global translation_history
    # Find entry by id and remove it
    entry = next((item for item in translation_history if item['id'] == entry_id), None)
    
    if entry:
        translation_history = [item for item in translation_history if item['id'] != entry_id]
        return jsonify({"message": "Deleted successfully"}), 200
    else:
        return jsonify({"error": "Entry not found"}), 404
    

if __name__ == '__main__':
    app.run(debug=True, port=5004)
