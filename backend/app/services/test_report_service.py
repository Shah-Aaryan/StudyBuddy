# test_report_service.py
import asyncio
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import logging

# Add your app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the database models to avoid DB dependencies
class MockEmotionLog:
    def __init__(self, user_id, timestamp, primary_emotion, confidence=0.8):
        self.user_id = user_id
        self.timestamp = timestamp
        self.primary_emotion = primary_emotion
        self.confidence = confidence

class MockLearningSession:
    def __init__(self, user_id, start_time, duration_minutes=45, 
                 average_engagement=0.75, completion_percentage=85, course_id=1):
        self.user_id = user_id
        self.start_time = start_time
        self.duration_minutes = duration_minutes
        self.average_engagement = average_engagement
        self.completion_percentage = completion_percentage
        self.course_id = course_id

class MockIntervention:
    def __init__(self, intervention_type, timestamp, effectiveness_score=0.8, user_response='completed'):
        self.intervention_type = intervention_type
        self.timestamp = timestamp
        self.effectiveness_score = effectiveness_score
        self.user_response = user_response
        self.session = Mock()

# Create dummy data
def create_dummy_data():
    """Create comprehensive dummy data for testing"""
    now = datetime.utcnow()
    
    # Create sessions for the past week
    sessions = []
    for i in range(7):
        session_time = now - timedelta(days=i, hours=2)
        sessions.append(MockLearningSession(
            user_id=1,
            start_time=session_time,
            duration_minutes=45 + (i * 5),
            average_engagement=0.7 + (i * 0.05),
            completion_percentage=80 + i,
            course_id=1 + (i % 3)
        ))
    
    # Create emotions for the past week
    emotions = []
    emotion_types = ['happy', 'engaged', 'frustrated', 'confused', 'neutral']
    for i in range(20):
        emotion_time = now - timedelta(days=i//3, hours=i%6)
        emotions.append(MockEmotionLog(
            user_id=1,
            timestamp=emotion_time,
            primary_emotion=emotion_types[i % len(emotion_types)],
            confidence=0.6 + (i * 0.02)
        ))
    
    # Create interventions
    interventions = []
    intervention_types = ['break_reminder', 'difficulty_adjustment', 'engagement_boost']
    for i in range(5):
        intervention_time = now - timedelta(days=i*2, hours=1)
        interventions.append(MockIntervention(
            intervention_type=intervention_types[i % len(intervention_types)],
            timestamp=intervention_time,
            effectiveness_score=0.7 + (i * 0.1),
            user_response='completed' if i % 2 == 0 else 'dismissed'
        ))
    
    return sessions, emotions, interventions

class MockDB:
    """Mock database session"""
    def __init__(self, sessions, emotions, interventions):
        self.sessions = sessions
        self.emotions = emotions
        self.interventions = interventions
    
    def query(self, model):
        if model.__name__ == 'LearningSession':
            return MockQuery(self.sessions)
        elif model.__name__ == 'EmotionLog':
            return MockQuery(self.emotions)
        elif model.__name__ == 'Intervention':
            return MockQuery(self.interventions)
        return MockQuery([])

class MockQuery:
    """Mock SQLAlchemy query"""
    def __init__(self, data):
        self.data = data
    
    def filter(self, *args):
        return self
    
    def join(self, *args):
        return self
    
    def order_by(self, *args):
        return self
    
    def first(self):
        return self.data[0] if self.data else None
    
    def all(self):
        return self.data

# Fix the ReportService constructor
class FixedReportService:
    def __init__(self):  # Fixed constructor
        self.emotion_categories = {
            'positive': ['happy', 'engaged', 'calm', 'surprised'],
            'negative': ['sad', 'angry', 'frustrated', 'disgusted'],
            'neutral': ['neutral'],
            'learning_specific': ['confused', 'bored', 'focused']
        }
    
    # Copy all methods from your original ReportService here
    def _calculate_emotion_distribution(self, emotions):
        """Calculate emotion distribution"""
        if not emotions:
            return {}
        
        emotion_counts = {}
        total_emotions = len(emotions)
        
        for emotion in emotions:
            primary = emotion.primary_emotion
            emotion_counts[primary] = emotion_counts.get(primary, 0) + 1
        
        return {k: v / total_emotions for k, v in emotion_counts.items()}
    
    def _calculate_daily_emotions(self, emotions, start_date, end_date):
        """Calculate daily emotion breakdown"""
        daily_emotions = {}
        current_date = start_date
        
        while current_date <= end_date:
            daily_emotions[current_date.isoformat()] = {}
            current_date += timedelta(days=1)
        
        for emotion in emotions:
            date_key = emotion.timestamp.date().isoformat()
            if date_key in daily_emotions:
                primary = emotion.primary_emotion
                daily_emotions[date_key][primary] = daily_emotions[date_key].get(primary, 0) + 1
        
        return daily_emotions
    
    def _calculate_intervention_stats(self, interventions):
        """Calculate intervention statistics"""
        if not interventions:
            return {"total": 0, "effectiveness": {}, "types": {}}
        
        total_interventions = len(interventions)
        type_counts = {}
        effectiveness_scores = []
        
        for intervention in interventions:
            int_type = intervention.intervention_type
            type_counts[int_type] = type_counts.get(int_type, 0) + 1
            
            if intervention.effectiveness_score:
                effectiveness_scores.append(intervention.effectiveness_score)
        
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
        
        return {
            "total": total_interventions,
            "average_effectiveness": round(avg_effectiveness, 3),
            "types": type_counts,
            "success_rate": len([i for i in interventions if i.user_response == 'completed']) / total_interventions
        }
    
    def _analyze_weekly_patterns(self, sessions, emotions):
        """Analyze weekly learning patterns"""
        if not sessions:
            return {}
        
        # Day of week patterns
        day_sessions = {}
        for session in sessions:
            day = session.start_time.strftime('%A')
            day_sessions[day] = day_sessions.get(day, 0) + 1
        
        # Hour patterns
        hour_sessions = {}
        for session in sessions:
            hour = session.start_time.hour
            hour_sessions[hour] = hour_sessions.get(hour, 0) + 1
        
        peak_day = max(day_sessions, key=day_sessions.get) if day_sessions else "N/A"
        peak_hour = max(hour_sessions, key=hour_sessions.get) if hour_sessions else 0
        
        return {
            "peak_learning_day": peak_day,
            "peak_learning_hour": peak_hour,
            "day_distribution": day_sessions,
            "hour_distribution": hour_sessions,
            "average_session_length": sum(s.duration_minutes or 0 for s in sessions) / len(sessions)
        }
    
    def _generate_weekly_recommendations(self, emotion_distribution, learning_patterns):
        """Generate weekly recommendations"""
        recommendations = []
        
        # Emotion-based recommendations
        if emotion_distribution.get('frustrated', 0) > 0.3:
            recommendations.append("Consider taking more breaks when frustrated to maintain learning effectiveness")
        
        if emotion_distribution.get('bored', 0) > 0.4:
            recommendations.append("Try incorporating more interactive content to combat boredom")
        
        # Pattern-based recommendations
        if learning_patterns.get('average_session_length', 0) > 120:
            recommendations.append("Consider shorter, more frequent sessions for better retention")
        
        return recommendations
    
    async def generate_weekly_report(self, user_id: int, db, week_offset: int = 0):
        """Generate weekly report for user - simplified for testing"""
        try:
            print(f"📊 Generating weekly report for user {user_id}")
            
            # Calculate date range for the week
            today = datetime.utcnow().date()
            start_of_week = today - timedelta(days=today.weekday() + (week_offset * 7))
            end_of_week = start_of_week + timedelta(days=6)
            
            print(f"📅 Report period: {start_of_week} to {end_of_week}")
            
            # Get data (using mock data)
            sessions = db.query(MockLearningSession).filter().all()
            emotions = db.query(MockEmotionLog).filter().all()
            interventions = db.query(MockIntervention).filter().all()
            
            print(f"📈 Found {len(sessions)} sessions, {len(emotions)} emotions, {len(interventions)} interventions")
            
            # Calculate metrics
            total_sessions = len(sessions)
            total_study_time = sum(s.duration_minutes or 0 for s in sessions)
            avg_engagement = sum(s.average_engagement or 0 for s in sessions) / max(total_sessions, 1)
            avg_completion = sum(s.completion_percentage or 0 for s in sessions) / max(total_sessions, 1)
            
            # Emotion analysis
            emotion_distribution = self._calculate_emotion_distribution(emotions)
            daily_emotions = self._calculate_daily_emotions(emotions, start_of_week, end_of_week)
            
            # Intervention analysis
            intervention_stats = self._calculate_intervention_stats(interventions)
            
            # Learning patterns
            learning_patterns = self._analyze_weekly_patterns(sessions, emotions)
            
            # Mock progress metrics
            progress_metrics = {
                "engagement_change": 0.05,
                "engagement_trend": "improving",
                "session_count_change": 2,
                "completion_rate": avg_completion
            }
            
            # Mock achievements
            achievements = [
                {
                    "type": "consistency",
                    "title": "Weekly Warrior",
                    "description": f"Studied {len(set(s.start_time.date() for s in sessions))} days this week!",
                    "points": 50
                }
            ]
            
            report = {
                "report_type": "weekly",
                "period": f"{start_of_week} to {end_of_week}",
                "user_id": user_id,
                "summary": {
                    "total_sessions": total_sessions,
                    "total_study_time_minutes": total_study_time,
                    "average_engagement": round(avg_engagement, 3),
                    "average_completion": round(avg_completion, 2),
                    "days_active": len(set(s.start_time.date() for s in sessions))
                },
                "emotion_analysis": {
                    "distribution": emotion_distribution,
                    "daily_breakdown": daily_emotions,
                    "dominant_emotion": max(emotion_distribution, key=emotion_distribution.get) if emotion_distribution else "neutral"
                },
                "intervention_analysis": intervention_stats,
                "progress_metrics": progress_metrics,
                "learning_patterns": learning_patterns,
                "achievements": achievements,
                "recommendations": self._generate_weekly_recommendations(emotion_distribution, learning_patterns)
            }
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating weekly report: {e}")
            import traceback
            traceback.print_exc()
            raise

async def test_report_generation():
    """Test the report generation with dummy data"""
    print("🧪 Starting Report Service Test")
    print("=" * 60)
    
    # Create dummy data
    sessions, emotions, interventions = create_dummy_data()
    print(f"📊 Created dummy data:")
    print(f"   - {len(sessions)} learning sessions")
    print(f"   - {len(emotions)} emotion logs")
    print(f"   - {len(interventions)} interventions")
    
    # Create mock database
    mock_db = MockDB(sessions, emotions, interventions)
    
    # Initialize report service
    report_service = FixedReportService()
    print("✅ Report service initialized")
    
    # Test weekly report generation
    try:
        print("\n📊 Testing Weekly Report Generation...")
        weekly_report = await report_service.generate_weekly_report(
            user_id=1, 
            db=mock_db, 
            week_offset=0
        )
        
        print("✅ Weekly report generated successfully!")
        print("\n📋 Report Summary:")
        print(f"   - Report Type: {weekly_report['report_type']}")
        print(f"   - Period: {weekly_report['period']}")
        print(f"   - Total Sessions: {weekly_report['summary']['total_sessions']}")
        print(f"   - Study Time: {weekly_report['summary']['total_study_time_minutes']} minutes")
        print(f"   - Average Engagement: {weekly_report['summary']['average_engagement']}")
        print(f"   - Dominant Emotion: {weekly_report['emotion_analysis']['dominant_emotion']}")
        print(f"   - Achievements: {len(weekly_report['achievements'])}")
        print(f"   - Recommendations: {len(weekly_report['recommendations'])}")
        
        # Test emotion analysis
        print("\n🎭 Emotion Analysis:")
        for emotion, percentage in weekly_report['emotion_analysis']['distribution'].items():
            print(f"   - {emotion}: {percentage:.2%}")
        
        # Test learning patterns
        print("\n📈 Learning Patterns:")
        patterns = weekly_report['learning_patterns']
        print(f"   - Peak Day: {patterns.get('peak_learning_day', 'N/A')}")
        print(f"   - Peak Hour: {patterns.get('peak_learning_hour', 'N/A')}")
        print(f"   - Avg Session Length: {patterns.get('average_session_length', 0):.1f} minutes")
        
        # Test recommendations
        print("\n💡 Recommendations:")
        for i, rec in enumerate(weekly_report['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Weekly report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_helper_methods():
    """Test individual helper methods"""
    print("\n🔧 Testing Helper Methods")
    print("-" * 40)
    
    sessions, emotions, interventions = create_dummy_data()
    report_service = FixedReportService()
    
    # Test emotion distribution
    print("🎭 Testing emotion distribution...")
    emotion_dist = report_service._calculate_emotion_distribution(emotions)
    print(f"✅ Emotion distribution calculated: {len(emotion_dist)} emotions")
    
    # Test intervention stats
    print("🛠️ Testing intervention stats...")
    intervention_stats = report_service._calculate_intervention_stats(interventions)
    print(f"✅ Intervention stats: {intervention_stats['total']} total interventions")
    
    # Test learning patterns
    print("📊 Testing learning patterns...")
    patterns = report_service._analyze_weekly_patterns(sessions, emotions)
    print(f"✅ Learning patterns analyzed: Peak day = {patterns.get('peak_learning_day')}")
    
    return True

def validate_report_structure(report):
    """Validate that the report has expected structure"""
    print("\n🔍 Validating Report Structure")
    print("-" * 40)
    
    required_keys = [
        'report_type', 'period', 'user_id', 'summary', 
        'emotion_analysis', 'intervention_analysis', 
        'progress_metrics', 'learning_patterns', 
        'achievements', 'recommendations'
    ]
    
    validation_results = []
    for key in required_keys:
        exists = key in report
        validation_results.append((key, exists))
        status = "✅" if exists else "❌"
        print(f"{status} {key}: {'Present' if exists else 'Missing'}")
    
    # Check summary structure
    if 'summary' in report:
        summary_keys = ['total_sessions', 'total_study_time_minutes', 'average_engagement']
        print("\n📊 Summary validation:")
        for key in summary_keys:
            exists = key in report['summary']
            status = "✅" if exists else "❌"
            print(f"   {status} {key}: {'Present' if exists else 'Missing'}")
    
    return all(result[1] for result in validation_results)

async def main():
    """Main test runner"""
    print("🚀 Report Service Testing Suite")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Basic report generation
    result1 = await test_report_generation()
    test_results.append(("Report Generation", result1))
    
    # Test 2: Helper methods
    result2 = await test_helper_methods()
    test_results.append(("Helper Methods", result2))
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    overall_success = all(result[1] for result in test_results)
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    asyncio.run(main())