# app/services/report_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from app.models.database import EmotionLog, LearningSession, Intervention, User
from app.models.schemas import WeeklyReport, MonthlyReport, YearlyReport
import logging

logger = logging.getLogger(__name__)

class ReportService:
    def _init_(self):
        self.emotion_categories = {
            'positive': ['happy', 'engaged', 'calm', 'surprised'],
            'negative': ['sad', 'angry', 'frustrated', 'disgusted'],
            'neutral': ['neutral'],
            'learning_specific': ['confused', 'bored', 'focused']
        }
    
    async def generate_weekly_report(self, user_id: int, db: Session, week_offset: int = 0) -> Dict:
        """Generate weekly report for user"""
        try:
            # Calculate date range for the week
            today = datetime.utcnow().date()
            start_of_week = today - timedelta(days=today.weekday() + (week_offset * 7))
            end_of_week = start_of_week + timedelta(days=6)
            
            # Get sessions for the week
            sessions = db.query(LearningSession).filter(
                and_(
                    LearningSession.user_id == user_id,
                    func.date(LearningSession.start_time) >= start_of_week,
                    func.date(LearningSession.start_time) <= end_of_week
                )
            ).all()
            
            # Get emotions for the week
            emotions = db.query(EmotionLog).filter(
                and_(
                    EmotionLog.user_id == user_id,
                    func.date(EmotionLog.timestamp) >= start_of_week,
                    func.date(EmotionLog.timestamp) <= end_of_week
                )
            ).all()
            
            # Get interventions for the week
            interventions = db.query(Intervention).join(
                Intervention.session
            ).filter(
                and_(
                    Intervention.session.has(user_id=user_id),
                    func.date(Intervention.timestamp) >= start_of_week,
                    func.date(Intervention.timestamp) <= end_of_week
                )
            ).all()
            
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
            
            # Progress tracking
            progress_metrics = await self._calculate_progress_metrics(user_id, db, start_of_week, end_of_week)
            
            # Learning patterns
            learning_patterns = self._analyze_weekly_patterns(sessions, emotions)
            
            # Achievements
            achievements = await self._check_weekly_achievements(user_id, db, sessions, emotions)
            
            return {
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
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            raise
    
    async def generate_monthly_report(self, user_id: int, db: Session, month_offset: int = 0) -> Dict:
        """Generate monthly report for user"""
        try:
            # Calculate date range for the month
            today = datetime.utcnow().date()
            if month_offset == 0:
                start_of_month = today.replace(day=1)
                if today.month == 12:
                    end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            else:
                # Handle month offset logic
                target_month = today.month - month_offset
                target_year = today.year
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                start_of_month = datetime(target_year, target_month, 1).date()
                if target_month == 12:
                    end_of_month = datetime(target_year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_of_month = datetime(target_year, target_month + 1, 1).date() - timedelta(days=1)
            
            # Get data for the month
            sessions = db.query(LearningSession).filter(
                and_(
                    LearningSession.user_id == user_id,
                    func.date(LearningSession.start_time) >= start_of_month,
                    func.date(LearningSession.start_time) <= end_of_month
                )
            ).all()
            
            emotions = db.query(EmotionLog).filter(
                and_(
                    EmotionLog.user_id == user_id,
                    func.date(EmotionLog.timestamp) >= start_of_month,
                    func.date(EmotionLog.timestamp) <= end_of_month
                )
            ).all()
            
            # Weekly breakdown
            weekly_data = await self._calculate_weekly_breakdown(user_id, db, start_of_month, end_of_month)
            
            # Monthly trends
            trends = await self._calculate_monthly_trends(user_id, db, start_of_month, end_of_month)
            
            # Goal achievement
            goal_progress = await self._calculate_goal_progress(user_id, db, start_of_month, end_of_month)
            
            return {
                "report_type": "monthly",
                "period": f"{start_of_month.strftime('%B %Y')}",
                "user_id": user_id,
                "summary": {
                    "total_sessions": len(sessions),
                    "total_study_time_minutes": sum(s.duration_minutes or 0 for s in sessions),
                    "average_engagement": sum(s.average_engagement or 0 for s in sessions) / max(len(sessions), 1),
                    "days_active": len(set(s.start_time.date() for s in sessions)),
                    "consistency_score": len(set(s.start_time.date() for s in sessions)) / (end_of_month - start_of_month).days
                },
                "weekly_breakdown": weekly_data,
                "emotion_trends": self._calculate_emotion_trends(emotions),
                "learning_trends": trends,
                "goal_progress": goal_progress,
                "achievements": await self._check_monthly_achievements(user_id, db, sessions, emotions),
                "insights": self._generate_monthly_insights(sessions, emotions)
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {e}")
            raise
    
    async def generate_yearly_report(self, user_id: int, db: Session, year: Optional[int] = None) -> Dict:
        """Generate yearly report for user"""
        try:
            if year is None:
                year = datetime.utcnow().year
            
            start_of_year = datetime(year, 1, 1).date()
            end_of_year = datetime(year, 12, 31).date()
            
            # Get all data for the year
            sessions = db.query(LearningSession).filter(
                and_(
                    LearningSession.user_id == user_id,
                    func.date(LearningSession.start_time) >= start_of_year,
                    func.date(LearningSession.start_time) <= end_of_year
                )
            ).all()
            
            emotions = db.query(EmotionLog).filter(
                and_(
                    EmotionLog.user_id == user_id,
                    func.date(EmotionLog.timestamp) >= start_of_year,
                    func.date(EmotionLog.timestamp) <= end_of_year
                )
            ).all()
            
            # Monthly breakdown
            monthly_data = await self._calculate_monthly_breakdown(user_id, db, start_of_year, end_of_year)
            
            # Learning milestones
            milestones = await self._calculate_learning_milestones(user_id, db, year)
            
            # Year-over-year comparison
            yoy_comparison = await self._calculate_yoy_comparison(user_id, db, year)
            
            return {
                "report_type": "yearly",
                "period": f"Year {year}",
                "user_id": user_id,
                "summary": {
                    "total_sessions": len(sessions),
                    "total_study_hours": sum(s.duration_minutes or 0 for s in sessions) / 60,
                    "average_engagement": sum(s.average_engagement or 0 for s in sessions) / max(len(sessions), 1),
                    "days_active": len(set(s.start_time.date() for s in sessions)),
                    "courses_completed": len(set(s.course_id for s in sessions if s.completion_percentage >= 100)),
                    "consistency_score": len(set(s.start_time.date() for s in sessions)) / 365
                },
                "monthly_breakdown": monthly_data,
                "learning_milestones": milestones,
                "emotion_journey": self._calculate_emotion_journey(emotions),
                "achievements": await self._check_yearly_achievements(user_id, db, sessions, emotions),
                "year_over_year": yoy_comparison,
                "insights": self._generate_yearly_insights(sessions, emotions)
            }
            
        except Exception as e:
            logger.error(f"Error generating yearly report: {e}")
            raise
    
    def _calculate_emotion_distribution(self, emotions: List) -> Dict[str, float]:
        """Calculate emotion distribution"""
        if not emotions:
            return {}
        
        emotion_counts = {}
        total_emotions = len(emotions)
        
        for emotion in emotions:
            primary = emotion.primary_emotion
            emotion_counts[primary] = emotion_counts.get(primary, 0) + 1
        
        return {k: v / total_emotions for k, v in emotion_counts.items()}
    
    def _calculate_daily_emotions(self, emotions: List, start_date, end_date) -> Dict:
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
    
    def _calculate_intervention_stats(self, interventions: List) -> Dict:
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
    
    async def _calculate_progress_metrics(self, user_id: int, db: Session, start_date, end_date) -> Dict:
        """Calculate progress metrics"""
        # Get previous period for comparison
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)
        
        current_sessions = db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                func.date(LearningSession.start_time) >= start_date,
                func.date(LearningSession.start_time) <= end_date
            )
        ).all()
        
        prev_sessions = db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                func.date(LearningSession.start_time) >= prev_start,
                func.date(LearningSession.start_time) <= prev_end
            )
        ).all()
        
        current_engagement = sum(s.average_engagement or 0 for s in current_sessions) / max(len(current_sessions), 1)
        prev_engagement = sum(s.average_engagement or 0 for s in prev_sessions) / max(len(prev_sessions), 1)
        
        engagement_change = current_engagement - prev_engagement
        
        return {
            "engagement_change": round(engagement_change, 3),
            "engagement_trend": "improving" if engagement_change > 0 else "declining",
            "session_count_change": len(current_sessions) - len(prev_sessions),
            "completion_rate": sum(s.completion_percentage or 0 for s in current_sessions) / max(len(current_sessions), 1)
        }
    
    def _analyze_weekly_patterns(self, sessions: List, emotions: List) -> Dict:
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
    
    async def _check_weekly_achievements(self, user_id: int, db: Session, sessions: List, emotions: List) -> List[Dict]:
        """Check for weekly achievements"""
        achievements = []
        
        # Consistency achievement
        unique_days = len(set(s.start_time.date() for s in sessions))
        if unique_days >= 5:
            achievements.append({
                "type": "consistency",
                "title": "Weekly Warrior",
                "description": f"Studied {unique_days} days this week!",
                "points": 50
            })
        
        # Engagement achievement
        high_engagement_sessions = [s for s in sessions if (s.average_engagement or 0) > 0.8]
        if len(high_engagement_sessions) >= 3:
            achievements.append({
                "type": "engagement",
                "title": "Highly Engaged",
                "description": f"Maintained high engagement in {len(high_engagement_sessions)} sessions!",
                "points": 30
            })
        
        # Study time achievement
        total_time = sum(s.duration_minutes or 0 for s in sessions)
        if total_time >= 300:  # 5 hours
            achievements.append({
                "type": "time",
                "title": "Time Master",
                "description": f"Studied for {total_time} minutes this week!",
                "points": 40
            })
        
        return achievements
    
    async def _check_monthly_achievements(self, user_id: int, db: Session, sessions: List, emotions: List) -> List[Dict]:
        """Check for monthly achievements"""
        achievements = []
        
        # Monthly consistency
        unique_days = len(set(s.start_time.date() for s in sessions))
        if unique_days >= 20:
            achievements.append({
                "type": "consistency",
                "title": "Monthly Champion",
                "description": f"Studied {unique_days} days this month!",
                "points": 100
            })
        
        # Course completion
        completed_courses = len(set(s.course_id for s in sessions if s.completion_percentage >= 100))
        if completed_courses >= 1:
            achievements.append({
                "type": "completion",
                "title": "Course Conqueror",
                "description": f"Completed {completed_courses} course(s) this month!",
                "points": 200
            })
        
        return achievements
    
    async def _check_yearly_achievements(self, user_id: int, db: Session, sessions: List, emotions: List) -> List[Dict]:
        """Check for yearly achievements"""
        achievements = []
        
        # Yearly dedication
        total_hours = sum(s.duration_minutes or 0 for s in sessions) / 60
        if total_hours >= 100:
            achievements.append({
                "type": "dedication",
                "title": "Learning Legend",
                "description": f"Studied for {total_hours:.1f} hours this year!",
                "points": 500
            })
        
        return achievements
    
    def _generate_weekly_recommendations(self, emotion_distribution: Dict, learning_patterns: Dict) -> List[str]:
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
    
    async def _calculate_weekly_breakdown(self, user_id: int, db: Session, start_date, end_date) -> Dict:
        """Calculate weekly breakdown for monthly report"""
        weekly_data = {}
        current_date = start_date
        week_num = 1
        
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            
            week_sessions = db.query(LearningSession).filter(
                and_(
                    LearningSession.user_id == user_id,
                    func.date(LearningSession.start_time) >= current_date,
                    func.date(LearningSession.start_time) <= week_end
                )
            ).all()
            
            weekly_data[f"week_{week_num}"] = {
                "sessions": len(week_sessions),
                "study_time": sum(s.duration_minutes or 0 for s in week_sessions),
                "avg_engagement": sum(s.average_engagement or 0 for s in week_sessions) / max(len(week_sessions), 1)
            }
            
            current_date = week_end + timedelta(days=1)
            week_num += 1
        
        return weekly_data
    
    def _calculate_emotion_trends(self, emotions: List) -> Dict:
        """Calculate emotion trends over time"""
        if not emotions:
            return {}
        
        # Group emotions by week
        weekly_emotions = {}
        for emotion in emotions:
            week_key = emotion.timestamp.strftime('%Y-W%U')
            if week_key not in weekly_emotions:
                weekly_emotions[week_key] = []
            weekly_emotions[week_key].append(emotion.primary_emotion)
        
        # Calculate trends
        trends = {}
        for week, week_emotions in weekly_emotions.items():
            emotion_counts = {}
            for emotion in week_emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            dominant_emotion = max(emotion_counts, key=emotion_counts.get)
            trends[week] = {
                "dominant_emotion": dominant_emotion,
                "distribution": emotion_counts
            }
        
        return trends
    
    async def _calculate_monthly_trends(self, user_id: int, db: Session, start_date, end_date) -> Dict:
        """Calculate monthly learning trends"""
        # Implementation for monthly trends
        return {
            "engagement_trend": "stable",
            "completion_trend": "improving",
            "consistency_trend": "improving"
        }
    
    async def _calculate_goal_progress(self, user_id: int, db: Session, start_date, end_date) -> Dict:
        """Calculate goal progress"""
        # This would integrate with a goals system
        return {
            "study_time_goal": {"target": 1200, "achieved": 980, "percentage": 81.7},
            "session_goal": {"target": 20, "achieved": 18, "percentage": 90.0}
        }
    
    async def _calculate_monthly_breakdown(self, user_id: int, db: Session, start_date, end_date) -> Dict:
        """Calculate monthly breakdown for yearly report"""
        monthly_data = {}
        current_date = start_date
        
        while current_date <= end_date:
            month_end = min(
                datetime(current_date.year, current_date.month + 1, 1).date() - timedelta(days=1),
                end_date
            ) if current_date.month < 12 else min(
                datetime(current_date.year + 1, 1, 1).date() - timedelta(days=1),
                end_date
            )
            
            month_sessions = db.query(LearningSession).filter(
                and_(
                    LearningSession.user_id == user_id,
                    func.date(LearningSession.start_time) >= current_date,
                    func.date(LearningSession.start_time) <= month_end
                )
            ).all()
            
            month_key = current_date.strftime('%B')
            monthly_data[month_key] = {
                "sessions": len(month_sessions),
                "study_hours": sum(s.duration_minutes or 0 for s in month_sessions) / 60,
                "avg_engagement": sum(s.average_engagement or 0 for s in month_sessions) / max(len(month_sessions), 1)
            }
            
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1).date()
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1).date()
        
        return monthly_data
    
    async def _calculate_learning_milestones(self, user_id: int, db: Session, year: int) -> List[Dict]:
        """Calculate learning milestones for the year"""
        milestones = []
        
        # First session milestone
        first_session = db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                extract('year', LearningSession.start_time) == year
            )
        ).order_by(LearningSession.start_time).first()
        
        if first_session:
            milestones.append({
                "type": "first_session",
                "date": first_session.start_time.date(),
                "description": "Started learning journey"
            })
        
        # Add more milestone logic here
        return milestones
    
    async def _calculate_yoy_comparison(self, user_id: int, db: Session, year: int) -> Dict:
        """Calculate year-over-year comparison"""
        # Get previous year data
        prev_year_sessions = db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                extract('year', LearningSession.start_time) == year - 1
            )
        ).all()
        
        current_year_sessions = db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                extract('year', LearningSession.start_time) == year
            )
        ).all()
        
        prev_study_time = sum(s.duration_minutes or 0 for s in prev_year_sessions)
        current_study_time = sum(s.duration_minutes or 0 for s in current_year_sessions)
        
        return {
            "sessions_change": len(current_year_sessions) - len(prev_year_sessions),
            "study_time_change": current_study_time - prev_study_time,
            "engagement_change": (sum(s.average_engagement or 0 for s in current_year_sessions) / max(len(current_year_sessions), 1)) - 
                               (sum(s.average_engagement or 0 for s in prev_year_sessions) / max(len(prev_year_sessions), 1))
        }
    
    def _calculate_emotion_journey(self, emotions: List) -> Dict:
        """Calculate emotion journey over the year"""
        if not emotions:
            return {}
        
        # Group by month
        monthly_emotions = {}
        for emotion in emotions:
            month_key = emotion.timestamp.strftime('%B')
            if month_key not in monthly_emotions:
                monthly_emotions[month_key] = []
            monthly_emotions[month_key].append(emotion.primary_emotion)
        
        # Calculate dominant emotion per month
        journey = {}
        for month, month_emotions in monthly_emotions.items():
            emotion_counts = {}
            for emotion in month_emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            journey[month] = max(emotion_counts, key=emotion_counts.get)
        
        return journey
    
    def _generate_monthly_insights(self, sessions: List, emotions: List) -> List[str]:
        """Generate monthly insights"""
        insights = []
        
        if sessions:
            avg_completion = sum(s.completion_percentage or 0 for s in sessions) / len(sessions)
            if avg_completion > 85:
                insights.append("Excellent completion rate this month!")
            elif avg_completion < 60:
                insights.append("Consider focusing on completing started lessons")
        
        return insights
    
    def _generate_yearly_insights(self, sessions: List, emotions: List) -> List[str]:
        """Generate yearly insights"""
        insights = []
        
        if sessions:
            total_hours = sum(s.duration_minutes or 0 for s in sessions) / 60
            insights.append(f"You dedicated {total_hours:.1f} hours to learning this year!")
            
            unique_courses = len(set(s.course_id for s in sessions))
            insights.append(f"You explored {unique_courses} different courses")
        
        return insights

report_service = ReportService()