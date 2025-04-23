from transformers import pipeline

class EmotionDetector:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
    
    def detect_emotion(self, text: str) -> str:
        results = self.classifier(text)[0]
        return max(results, key=lambda x: x['score'])['label']