"""
Sentiment Analysis Service - Analyze customer emotions
"""
from typing import Dict, List
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentService:
    """Analyze sentiment and emotions in customer messages"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Comprehensive sentiment analysis combining VADER and TextBlob
        
        Args:
            text: Text to analyze
        
        Returns:
            Dict with sentiment scores and classification
        """
        # VADER analysis (better for social media/short text)
        vader_scores = self.vader.polarity_scores(text)
        
        # TextBlob analysis (good for longer text)
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity
        
        # Combined score (weighted average)
        combined_score = (vader_scores['compound'] + textblob_polarity) / 2
        
        # Classification
        if combined_score >= 0.3:
            sentiment_label = "positive"
            emoji = "😊"
        elif combined_score <= -0.3:
            sentiment_label = "negative"
            emoji = "😟"
        else:
            sentiment_label = "neutral"
            emoji = "😐"
        
        # Confidence based on agreement between methods
        confidence = self._calculate_confidence(vader_scores['compound'], textblob_polarity)
        
        return {
            "sentiment": sentiment_label,
            "score": round(combined_score, 3),
            "confidence": confidence,
            "emoji": emoji,
            "vader": {
                "compound": vader_scores['compound'],
                "positive": vader_scores['pos'],
                "negative": vader_scores['neg'],
                "neutral": vader_scores['neu']
            },
            "textblob": {
                "polarity": round(textblob_polarity, 3),
                "subjectivity": round(textblob_subjectivity, 3)
            },
            "emotion": self.detect_emotion(text, vader_scores)
        }
    
    def detect_emotion(self, text: str, vader_scores: Dict = None) -> str:
        """
        Detect specific emotion from text
        
        Returns:
            One of: happy, sad, angry, frustrated, neutral, confused, excited
        """
        if vader_scores is None:
            vader_scores = self.vader.polarity_scores(text)
        
        text_lower = text.lower()
        
        # Emotion keywords
        angry_keywords = ['angry', 'furious', 'mad', 'hate', 'worst', 'terrible', 'horrible']
        frustrated_keywords = ['frustrated', 'annoyed', 'irritated', 'disappointed', 'again', 'still not working']
        sad_keywords = ['sad', 'unhappy', 'upset', 'disappointed', 'regret']
        happy_keywords = ['happy', 'great', 'excellent', 'thank', 'appreciate', 'love', 'perfect']
        excited_keywords = ['excited', 'amazing', 'awesome', 'wonderful', 'fantastic']
        confused_keywords = ['confused', 'don\'t understand', 'not sure', 'unclear', 'help']
        
        # Check for strong negative with anger keywords
        if vader_scores['compound'] <= -0.5:
            if any(word in text_lower for word in angry_keywords):
                return "angry"
            elif any(word in text_lower for word in frustrated_keywords):
                return "frustrated"
            elif any(word in text_lower for word in sad_keywords):
                return "sad"
            else:
                return "negative"
        
        # Check for positive emotions
        elif vader_scores['compound'] >= 0.5:
            if any(word in text_lower for word in excited_keywords):
                return "excited"
            elif any(word in text_lower for word in happy_keywords):
                return "happy"
            else:
                return "positive"
        
        # Check for confusion
        elif any(word in text_lower for word in confused_keywords):
            return "confused"
        
        return "neutral"
    
    def analyze_conversation_trend(self, messages: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Analyze sentiment trend across a conversation
        
        Args:
            messages: List of dicts with 'content' and 'timestamp' keys
        
        Returns:
            Trend analysis with overall sentiment and changes
        """
        if not messages:
            return {"trend": "neutral", "scores": [], "overall": 0}
        
        scores = []
        sentiments = []
        
        for msg in messages:
            analysis = self.analyze_sentiment(msg['content'])
            scores.append(analysis['score'])
            sentiments.append(analysis['sentiment'])
        
        # Calculate trend
        if len(scores) >= 2:
            # Simple linear trend: improving/degrading/stable
            first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
            second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
            
            if second_half_avg - first_half_avg > 0.2:
                trend = "improving"
            elif first_half_avg - second_half_avg > 0.2:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        overall_score = sum(scores) / len(scores)
        overall_sentiment = "positive" if overall_score >= 0.2 else ("negative" if overall_score <= -0.2 else "neutral")
        
        return {
            "trend": trend,
            "overall_sentiment": overall_sentiment,
            "overall_score": round(overall_score, 3),
            "scores": scores,
            "message_count": len(messages),
            "positive_count": sentiments.count("positive"),
            "negative_count": sentiments.count("negative"),
            "neutral_count": sentiments.count("neutral")
        }
    
    def is_urgent(self, text: str, sentiment_score: float = None) -> bool:
        """
        Determine if message requires urgent attention
        
        Criteria:
        - Very negative sentiment
        - Urgent keywords
        - Legal/escalation threats
        """
        if sentiment_score is None:
            analysis = self.analyze_sentiment(text)
            sentiment_score = analysis['score']
        
        urgent_keywords = [
            'urgent', 'asap', 'immediately', 'emergency',
            'critical', 'cannot wait', 'right now',
            'lawyer', 'legal action', 'sue', 'refund now',
            'cancel immediately', 'losing money'
        ]
        
        text_lower = text.lower()
        
        # Very negative sentiment
        if sentiment_score <= -0.6:
            return True
        
        # Urgent keywords
        if any(keyword in text_lower for keyword in urgent_keywords):
            return True
        
        return False
    
    def _calculate_confidence(self, vader_compound: float, textblob_polarity: float) -> int:
        """
        Calculate confidence based on agreement between VADER and TextBlob
        
        Returns:
            Confidence percentage (0-100)
        """
        # If both agree on direction (both positive or both negative)
        if (vader_compound >= 0 and textblob_polarity >= 0) or \
           (vader_compound < 0 and textblob_polarity < 0):
            # High agreement
            agreement = 1 - abs(vader_compound - textblob_polarity) / 2
            confidence = int(70 + (agreement * 30))  # 70-100%
        else:
            # Disagreement - lower confidence
            confidence = int(40 + (abs(vader_compound - textblob_polarity) * 10))  # 40-70%
        
        return min(100, max(0, confidence))


# Global sentiment service instance
sentiment_service = SentimentService()
