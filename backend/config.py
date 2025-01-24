import os

class Config:
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'default-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///site.db'
    SOLANA_RPC_URL = os.environ.get('SOLANA_RPC_URL') or 'https://api.devnet.solana.com'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
