# Emotion categories
EMOTIONS = {
    'POSITIVE': ['happy', 'engaged', 'calm', 'surprised'],
    'NEGATIVE': ['sad', 'angry', 'frustrated', 'disgusted'],
    'NEUTRAL': ['neutral'],
    'LEARNING_SPECIFIC': ['confused', 'bored', 'focused']
}

# Intervention types
INTERVENTION_TYPES = {
    'VIDEO': 'video',
    'GAME': 'game',
    'BREAK': 'break',
    'CHATBOT': 'chatbot',
    'ENCOURAGEMENT': 'encouragement'
}

# Emotion thresholds
EMOTION_THRESHOLDS = {
    'CONFUSION': 0.7,
    'FRUSTRATION': 0.6,
    'BOREDOM': 0.65,
    'ENGAGEMENT': 0.8
}

# Audio processing constants
AUDIO_CONFIG = {
    'SAMPLE_RATE': 22050,
    'N_MFCC': 13,
    'HOP_LENGTH': 512,
    'N_FFT': 2048
}

# Image processing constants
IMAGE_CONFIG = {
    'FACE_SIZE': (48, 48),
    'COLOR_CHANNELS': 1,  # Grayscale
    'NORMALIZE': True
}

# API response codes
API_RESPONSES = {
    'SUCCESS': 200,
    'CREATED': 201,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'NOT_FOUND': 404,
    'INTERNAL_ERROR': 500
}

# WebSocket message types
WS_MESSAGE_TYPES = {
    'EMOTION_DATA': 'emotion_data',
    'EMOTION_RESPONSE': 'emotion_response',
    'INTERVENTION': 'intervention',
    'HEARTBEAT': 'heartbeat',
    'ERROR': 'error'
}