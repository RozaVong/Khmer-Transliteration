from datetime import datetime
import uuid

class Prediction:
    def __init__(self, input_text: str, output_text: str, confidence: float):
        self.id = str(uuid.uuid4())
        self.input_text = input_text
        self.output_text = output_text
        self.confidence = confidence
        self.timestamp = datetime.utcnow()
        self.user_ip = None
        self.user_agent = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'input_text': self.input_text,
            'output_text': self.output_text,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'user_ip': self.user_ip,
            'user_agent': self.user_agent
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Prediction from dictionary"""
        prediction = cls(
            input_text=data['input_text'],
            output_text=data['output_text'],
            confidence=data['confidence']
        )
        prediction.id = data.get('id', str(uuid.uuid4()))
        if 'timestamp' in data:
            prediction.timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        prediction.user_ip = data.get('user_ip')
        prediction.user_agent = data.get('user_agent')
        return prediction