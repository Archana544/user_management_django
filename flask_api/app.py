from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from database import db
from routes import routes
from models import User
from dotenv import load_dotenv
import os
from utils.env_validator import validate_env

validate_env()

# Load .env variables
load_dotenv()

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

db.init_app(app)
jwt = JWTManager(app)
app.register_blueprint(routes, url_prefix="/api")

with app.app_context():
    db.create_all()

# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()  
    username = data.get("username")

    if not username:
        return jsonify({"msg": "Username required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)


if __name__ == "__main__":
    app.run(debug=True)