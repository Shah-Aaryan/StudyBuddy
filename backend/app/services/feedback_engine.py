from typing import Dict, List
from app.models.schemas import InterventionRequest, InterventionResponse
from app.services.resource_recommender import resource_recommender
import random

class FeedbackEngine:
    def __init__(self):
        self.intervention_strategies = {
            'confused': self._handle_confusion,
            'frustrated': self._handle_frustration,
            'bored': self._handle_boredom,
            'engaged': self._reinforce_engagement
        }
        
        self.intervention_history = {}  # Track user intervention history
    
    async def generate_intervention(self, request: InterventionRequest, user_id: int) -> InterventionResponse:
        """Generate appropriate intervention based on detected emotion"""
        
        emotion = request.emotion
        confidence = request.confidence
        context = request.context
        
        # Get user's intervention history
        user_history = self.intervention_history.get(user_id, [])
        
        # Select intervention strategy
        if emotion in self.intervention_strategies:
            intervention = await self.intervention_strategies[emotion](
                confidence, context, user_history
            )
        else:
            intervention = await self._default_intervention(confidence, context)
        
        # Update history
        if user_id not in self.intervention_history:
            self.intervention_history[user_id] = []
        self.intervention_history[user_id].append({
            'emotion': emotion,
            'intervention_type': intervention.type,
            'timestamp': context.get('timestamp')
        })
        
        return intervention
    
    async def _handle_confusion(self, confidence: float, context: Dict, history: List) -> InterventionResponse:
        """Handle confusion with explanatory resources"""
        
        # Check recent confusion interventions
        recent_confusion = [h for h in history[-5:] if h['emotion'] == 'confused']
        
        if len(recent_confusion) >= 2:
            # Escalate to human help or comprehensive review
            return InterventionResponse(
                type="chatbot",
                resource={
                    "type": "ai_tutor",
                    "message": "I notice you've been having some challenges. Let me connect you with additional help.",
                    "escalation": True
                },
                message="Let's get you some personalized help!",
                priority=3
            )
        
        # Progressive intervention based on confidence
        if confidence > 0.8:
            # High confidence confusion - provide immediate help
            resource = await resource_recommender.get_explanatory_content(
                context.get('lesson_id', ''),
                context.get('current_topic', '')
            )
            return InterventionResponse(
                type="video",
                resource=resource,
                message="Let me show you this in a different way!",
                priority=2
            )
        else:
            # Moderate confusion - suggest review
            return InterventionResponse(
                type="chatbot",
                resource={
                    "type": "quick_help",
                    "message": "Would you like me to explain this concept differently?",
                    "options": ["Yes, show me a video", "Give me an example", "Skip for now"]
                },
                message="Need a quick clarification?",
                priority=1
            )
    
    async def _handle_frustration(self, confidence: float, context: Dict, history: List) -> InterventionResponse:
        """Handle frustration with calming and supportive interventions"""
        
        if confidence > 0.7:
            # High frustration - suggest break
            return InterventionResponse(
                type="break",
                resource={
                    "type": "mindful_break",
                    "duration": 5,
                    "activity": "breathing_exercise",
                    "message": "Take a moment to breathe and reset."
                },
                message="Let's take a quick breather together.",
                priority=3
            )
        else:
            # Moderate frustration - encouraging message + easier content
            resource = await resource_recommender.get_simplified_content(
                context.get('lesson_id', ''),
                context.get('difficulty_level', 'medium')
            )
            return InterventionResponse(
                type="video",
                resource=resource,
                message="You're doing great! Let's try a different approach.",
                priority=2
            )
    
    async def _handle_boredom(self, confidence: float, context: Dict, history: List) -> InterventionResponse:
        """Handle boredom with engaging and interactive content"""
        
        # Check if user prefers certain types of content
        preferred_type = self._analyze_preferences(history)
        
        if preferred_type == "game" or random.random() < 0.6:
            # Gamified content
            resource = await resource_recommender.get_interactive_game(
                context.get('lesson_id', ''),
                context.get('current_topic', '')
            )
            return InterventionResponse(
                type="game",
                resource=resource,
                message="Ready for a fun challenge?",
                priority=2
            )
        else:
            # Interactive video or quiz
            resource = await resource_recommender.get_interactive_content(
                context.get('lesson_id', ''),
                context.get('current_topic', '')
            )
            return InterventionResponse(
                type="video",
                resource=resource,
                message="Let's spice things up a bit!",
                priority=1
            )
    
    async def _reinforce_engagement(self, confidence: float, context: Dict, history: List) -> InterventionResponse:
        """Reinforce positive engagement"""
        
        encouragement_messages = [
            "You're on fire! Keep up the excellent work!",
            "Great focus! You're really getting this.",
            "Awesome progress! You're in the zone!",
            "Fantastic! Your dedication is showing."
        ]
        
        return InterventionResponse(
            type="encouragement",
            resource={
                "type": "positive_feedback",
                "message": random.choice(encouragement_messages),
                "badge": "focused_learner",
                "points": 10
            },
            message="Keep up the amazing work!",
            priority=0
        )
    
    async def _default_intervention(self, confidence: float, context: Dict) -> InterventionResponse:
        """Default intervention when emotion is unclear"""
        
        return InterventionResponse(
            type="chatbot",
            resource={
                "type": "check_in",
                "message": "How are you feeling about the material?",
                "options": ["Going well", "Need help", "Taking a break"]
            },
            message="Just checking in on your progress!",
            priority=0
        )
    
    def _analyze_preferences(self, history: List) -> str:
        """Analyze user preferences from intervention history"""
        if not history:
            return "video"
        
        # Count intervention types that were likely successful
        type_counts = {}
        for intervention in history[-10:]:  # Look at last 10 interventions
            int_type = intervention.get('intervention_type', 'video')
            type_counts[int_type] = type_counts.get(int_type, 0) + 1
        
        return max(type_counts, key=type_counts.get) if type_counts else "video"

feedback_engine = FeedbackEngine()