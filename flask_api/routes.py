from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Document

routes = Blueprint("routes", __name__)

@routes.route("/documents", methods=["GET"])
@jwt_required()
def get_documents():
    user_id = get_jwt_identity() 
    docs = Document.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": d.id,
            "title": d.title,
            "file_type": d.file_type,
            "uploaded_at": d.uploaded_at.isoformat()
        } for d in docs
    ])


@routes.route("/documents", methods=["POST"])
@jwt_required()
def create_document():
    user_id = get_jwt_identity()  # integer ID
    data = request.form
    file = request.files.get("file")
    file_type = file.filename.split('.')[-1].upper() if file else None

    new_doc = Document(
        title=data.get("title"),
        file=file.filename if file else None,
        file_type=file_type,
        user_id=user_id
    )

    db.session.add(new_doc)
    db.session.commit()

    return jsonify({"message": "Document created", "id": new_doc.id}), 201