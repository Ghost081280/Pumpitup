from flask import current_app
from .models import Song
from collections import defaultdict
import random

class AILyricsRecommender:
    def __init__(self):
        # In a real scenario, you might use more sophisticated AI or ML models here
        # We'll simulate with a simple content-based recommendation system
        self.song_keywords = defaultdict(list)
    
    def update_song_keywords(self):
        """Update keywords for each song. Here we'll simulate with random tags."""
        all_songs = Song.query.all()
        for song in all_songs:
            # In reality, you'd analyze lyrics or audio features for real keywords
            self.song_keywords[song.id] = [f"genre_{random.choice(['rock', 'pop', 'jazz', 'electronic'])}",
                                           f"mood_{random.choice(['happy', 'sad', 'energetic', 'relaxed'])}"]
    
    def recommend_songs(self, user_preferences):
        """
        Recommend songs based on user preferences.
        
        :param user_preferences: List of keywords representing user's taste
        :return: List of song IDs recommended
        """
        self.update_song_keywords()  # Update or load keywords
        
        # Simple matching system - count how many preferences match each song's keywords
        recommendations = []
        for song_id, keywords in self.song_keywords.items():
            match_count = sum(1 for pref in user_preferences if any(pref in kw for kw in keywords))
            if match_count > 0:
                recommendations.append((song_id, match_count))
        
        # Sort by match count in descending order and take top 5
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [song_id for song_id, _ in recommendations[:5]]

# Example usage - this would typically be in a route or integrated into existing logic
def get_recommended_songs(user_preferences):
    recommender = AILyricsRecommender()
    return recommender.recommend_songs(user_preferences)

def register_ai_recommender(app):
    """
    Register the AI recommender with the Flask app context.
    """
    with app.app_context():
        app.cli.add_command(update_song_keywords_command)

def update_song_keywords_command():
    """Command to update song keywords for recommendations."""
    AILyricsRecommender().update_song_keywords()
    print("Song keywords updated for AI recommendations.")

# In your main app file (song_investment_app.py or similar), you would add:
# register_ai_recommender(app)
