from typing import Dict, List
import random

class ResourceRecommender:
    def __init__(self):
        self.content_database = {
            "explanatory_videos": [
                {
                    "id": "exp_001",
                    "title": "Concept Breakdown",
                    "url": "/videos/explanation/concept_breakdown.mp4",
                    "duration": 180,
                    "difficulty": "easy",
                    "topics": ["fundamentals", "basics"]
                },
                {
                    "id": "exp_002", 
                    "title": "Step by Step Guide",
                    "url": "/videos/explanation/step_by_step.mp4",
                    "duration": 240,
                    "difficulty": "medium",
                    "topics": ["process", "methodology"]
                }
            ],
            "interactive_games": [
                {
                    "id": "game_001",
                    "title": "Quiz Challenge",
                    "url": "/games/quiz_challenge",
                    "duration": 300,
                    "points": 50,
                    "topics": ["review", "assessment"]
                },
                {
                    "id": "game_002",
                    "title": "Drag and Drop",
                    "url": "/games/drag_drop",
                    "duration": 180,
                    "points": 30,
                    "topics": ["categorization", "matching"]
                }
            ],
            "mindful_breaks": [
                {
                    "id": "break_001",
                    "title": "Breathing Exercise",
                    "url": "/breaks/breathing",
                    "duration": 300,
                    "type": "guided_meditation"
                },
                {
                    "id": "break_002",
                    "title": "Quick Stretch",
                    "url": "/breaks/stretch",
                    "duration": 180,
                    "type": "physical_activity"
                }
            ]
        }
    
    async def get_explanatory_content(self, lesson_id: str, topic: str) -> Dict:
        """Get explanatory video content for confusion"""
        videos = self.content_database["explanatory_videos"]
        
        # Filter by topic if available
        relevant_videos = [v for v in videos if any(t in topic.lower() for t in v["topics"])]
        if not relevant_videos:
            relevant_videos = videos
        
        selected_video = random.choice(relevant_videos)
        return {
            "id": selected_video["id"],
            "title": selected_video["title"],
            "url": selected_video["url"],
            "duration": selected_video["duration"],
            "type": "explanatory_video",
            "metadata": {
                "lesson_id": lesson_id,
                "topic": topic,
                "difficulty": selected_video["difficulty"]
            }
        }
    
    async def get_simplified_content(self, lesson_id: str, current_difficulty: str) -> Dict:
        """Get simplified content for frustration"""
        videos = self.content_database["explanatory_videos"]
        
        # Get easier content
        easy_videos = [v for v in videos if v["difficulty"] == "easy"]
        if not easy_videos:
            easy_videos = videos
        
        selected_video = random.choice(easy_videos)
        return {
            "id": selected_video["id"],
            "title": f"Simplified: {selected_video['title']}",
            "url": selected_video["url"],
            "duration": selected_video["duration"],
            "type": "simplified_content",
            "metadata": {
                "lesson_id": lesson_id,
                "original_difficulty": current_difficulty,
                "simplified": True
            }
        }
    
    async def get_interactive_game(self, lesson_id: str, topic: str) -> Dict:
        """Get interactive game for boredom"""
        games = self.content_database["interactive_games"]
        
        # Filter by topic if available
        relevant_games = [g for g in games if any(t in topic.lower() for t in g["topics"])]
        if not relevant_games:
            relevant_games = games
        
        selected_game = random.choice(relevant_games)
        return {
            "id": selected_game["id"],
            "title": selected_game["title"],
            "url": selected_game["url"],
            "duration": selected_game["duration"],
            "points": selected_game["points"],
            "type": "interactive_game",
            "metadata": {
                "lesson_id": lesson_id,
                "topic": topic,
                "gamified": True
            }
        }
    
    async def get_interactive_content(self, lesson_id: str, topic: str) -> Dict:
        """Get interactive content for engagement"""
        # Mix of videos and light games
        all_content = self.content_database["explanatory_videos"] + self.content_database["interactive_games"]
        selected_content = random.choice(all_content)
        
        return {
            "id": selected_content["id"],
            "title": selected_content["title"],
            "url": selected_content["url"],
            "duration": selected_content["duration"],
            "type": "interactive_content",
            "metadata": {
                "lesson_id": lesson_id,
                "topic": topic,
                "interactive": True
            }
        }
    
    async def get_break_activity(self, break_type: str = "breathing") -> Dict:
        """Get mindful break activity"""
        breaks = self.content_database["mindful_breaks"]
        
        # Filter by break type
        relevant_breaks = [b for b in breaks if b["type"] == break_type]
        if not relevant_breaks:
            relevant_breaks = breaks
        
        selected_break = random.choice(relevant_breaks)
        return {
            "id": selected_break["id"],
            "title": selected_break["title"],
            "url": selected_break["url"],
            "duration": selected_break["duration"],
            "type": "mindful_break",
            "activity_type": selected_break["type"]
        }

resource_recommender = ResourceRecommender()