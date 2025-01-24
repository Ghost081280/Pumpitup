from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['SOLANA_RPC_URL'] = 'https://api.devnet.solana.com'  # Use Devnet for testing
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
solana_client = Client(app.config['SOLANA_RPC_URL'])

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(44), unique=True, nullable=False)
    bio = db.Column(db.String(255))  

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('songs', lazy=True))
    total_invested = db.Column(db.Float, default=0)

@app.route('/signin', methods=['POST'])
def sign_in():
    data = request.get_json()
    try:
        wallet_address = PublicKey(data['wallet_address'])
        # Here you would typically verify the wallet signature, but for simplicity:
        access_token = create_access_token(identity=str(wallet_address))
        user = User.query.filter_by(wallet_address=str(wallet_address)).first()
        if not user:
            user = User(wallet_address=str(wallet_address), bio='')
            db.session.add(user)
            db.session.commit()
        return jsonify(access_token=access_token), 200
    except Exception as e:
        return jsonify({"message": "Invalid wallet address or signature"}), 400

@app.route('/user/profile', methods=['GET', 'PUT'])
@jwt_required()
def user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(wallet_address=current_user_id).first_or_404()
    
    if request.method == 'GET':
        return jsonify({
            "wallet_address": user.wallet_address,
            "bio": user.bio
        })
    
    if request.method == 'PUT':
        data = request.get_json()
        user.bio = data.get('bio', user.bio)
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_song():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        if not file.filename.lower().endswith(('.mp3', '.wav')):
            return jsonify({"error": "Only MP3 or WAV files are allowed"}), 400
        filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(file.filename)[1])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        current_user_id = get_jwt_identity()
        new_song = Song(filename=filename, user_id=User.query.filter_by(wallet_address=current_user_id).first().id)
        db.session.add(new_song)
        db.session.commit()
        return jsonify({"success": True, "filename": filename}), 200
    return jsonify({"error": "File upload failed"}), 400

@app.route('/songs', methods=['GET'])
@jwt_required()
def list_songs():
    songs = Song.query.all()
    return jsonify([{
        "id": song.id, 
        "filename": song.filename,
        "user": {
            "wallet_address": song.user.wallet_address,
            "bio": song.user.bio
        },
        "total_invested": song.total_invested
    } for song in songs])

@app.route('/songs/<int:song_id>/invest', methods=['POST'])
@jwt_required()
def invest_in_song(song_id):
    song = Song.query.get_or_404(song_id)
    data = request.get_json()
    amount = float(data.get('amount', 0))
    if amount <= 0:
        return jsonify({"error": "Invalid investment amount"}), 400

    # Here we would transfer SOL from the user's wallet to a designated wallet for the song
    # This is a placeholder for actual Solana transaction, you need to implement proper transaction
    try:
        # Note: This is a very basic implementation. Real-world apps would need to handle transaction signatures properly
        from_wallet = PublicKey(get_jwt_identity())  # Current user's wallet
        to_wallet = PublicKey("placeholder_wallet_address_for_song")  # Should be song's wallet address
        transaction = Transaction().add(transfer(TransferParams(from_pubkey=from_wallet, to_pubkey=to_wallet, lamports=int(amount * 1e9))))  # Convert SOL to lamports
        # In a real scenario, you'd sign this transaction with the user's private key, which you shouldn't have access to. 
        # Instead, use a method where users sign transactions client-side.

        # IMPORTANT:
        # - This code assumes you have a way to verify wallet signatures on the client-side, which isn't implemented here.
        # - You'd need to integrate with a Solana wallet provider like Phantom for actual implementation.
        # - The investment in songs would need a real Solana transaction setup where users sign transactions on their side, not on the server.
        # - Use the Solana testnet or devnet for development and testing, and always handle transactions with caution in production environments.

        # Update database with investment
        song.total_invested += amount
        db.session.commit()
        return jsonify({"message": "Investment successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/songs/<filename>')
@jwt_required()
def download_song(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
