from flask import Flask, request
from flask_restx import Api, Resource, fields
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os

from services import (
    data_ingestion, calculate_embedding_cost, create_vector_store,
    load_vector_store, get_claude_llm, get_llama2_llm, get_response_llm
)

app = Flask(__name__)
api = Api(app, title="Bot-as-a-Service", version="1.0", doc="/swagger")

ns = api.namespace("bot", description="PDF Knowledge Bot APIs")

chat_input = api.model("ChatInput", {
    "query": fields.String(required=True, description="Query for the bot"),
    "model": fields.String(required=True, enum=["claude", "llama"], description="LLM to use"),
})

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True,
                           help='PDF file to upload')
upload_parser.add_argument('kb_id', location='form',
                           type=str, required=True,
                           help='Knowledge Base ID to upload the file under')


@ns.route('/upload')
@ns.expect(upload_parser)
class Upload(Resource):
    @ns.doc(description="Upload PDF files to a specific knowledge base ID")
    def post(self):
        args = upload_parser.parse_args()
        file = args['file']
        kb_id = args['kb_id']

        if not file.filename.endswith('.pdf'):
            return {"message": "Only PDF files are allowed."}, 400

        save_path = f"./data/{kb_id}"
        os.makedirs(save_path, exist_ok=True)
        filepath = os.path.join(save_path, file.filename)
        file.save(filepath)

        return {"message": f"File '{file.filename}' uploaded under knowledge base ID '{kb_id}'."}, 200


@ns.route("/embedding-cost/<string:kb_id>")
class EmbeddingCost(Resource):
    @api.doc(description="Calculate estimated embedding cost for a knowledge base")
    def get(self, kb_id):
        docs = data_ingestion(kb_id)
        cost = calculate_embedding_cost(docs)
        return {"kb_id": kb_id, "embedding_cost_estimate": cost}, 200


@ns.route("/create-embeddings/<string:kb_id>")
class CreateEmbeddings(Resource):
    @api.doc(description="Create and store FAISS embeddings for a knowledge base")
    def post(self, kb_id):
        docs = data_ingestion(kb_id)
        create_vector_store(docs, kb_id)
        return {"message": f"Embeddings created and stored for knowledge base '{kb_id}'"}, 200


@ns.route("/chat/<string:kb_id>")
class Chat(Resource):
    @api.expect(chat_input)
    @api.doc(description="Ask questions to the bot using a specific knowledge base and LLM")
    def post(self, kb_id):
        data = request.get_json()
        query = data.get("query")
        model = data.get("model")

        vectorstore = load_vector_store(kb_id)

        llm = get_claude_llm() if model == "claude" else get_llama2_llm()
        response = get_response_llm(llm, vectorstore, query)

        return {"response": response}, 200


if __name__ == "__main__":
    app.run(debug=True)