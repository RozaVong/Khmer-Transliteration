#!/usr/bin/env python3
"""
Quick test to fix and verify the model loading
"""
import sys
import os
import pickle
import numpy as np
import re

# Set environment variables BEFORE importing
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_directly():
    """Test model directly without the complex structure"""
    
    print("=" * 60)
    print("Testing model directly...")
    print("=" * 60)
    
    # Paths
    MODEL_PATH = "model/khmer_Glish.keras"
    PICKLE_PATH = "model/khmer_Glish.pkl"
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model file not found: {MODEL_PATH}")
        return
    if not os.path.exists(PICKLE_PATH):
        print(f"❌ Pickle file not found: {PICKLE_PATH}")
        return
    
    print(f"✅ Model file found: {MODEL_PATH}")
    print(f"✅ Pickle file found: {PICKLE_PATH}")
    
    # Try different imports
    try:
        from keras.models import load_model
        from keras.preprocessing.sequence import pad_sequences
        print("✅ Using Keras 3")
    except ImportError:
        try:
            from tensorflow.keras.models import load_model
            from tensorflow.keras.preprocessing.sequence import pad_sequences
            print("✅ Using TensorFlow Keras")
        except ImportError as e:
            print(f"❌ Cannot import Keras: {e}")
            return
    
    # Load model
    print("Loading model...")
    model = load_model(MODEL_PATH)
    print("✅ Model loaded")
    
    # Load assets
    print("Loading tokenizers...")
    try:
        with open(PICKLE_PATH, 'rb') as f:
            assets = pickle.load(f)
    except Exception as e:
        print(f"❌ Pickle load error: {e}")
        # Try custom unpickler
        try:
            class CustomUnpickler(pickle.Unpickler):
                def find_class(self, module, name):
                    if module.startswith('keras.'):
                        module = module.replace('keras.', 'tensorflow.keras.')
                    elif module == 'keras':
                        module = 'tensorflow.keras'
                    elif module.startswith('keras.src.'):
                        module = module.replace('keras.src.', 'tensorflow.keras.')
                    return super().find_class(module, name)
            
            with open(PICKLE_PATH, 'rb') as f:
                unpickler = CustomUnpickler(f)
                assets = unpickler.load()
            print("✅ Loaded with custom unpickler")
        except Exception as e2:
            print(f"❌ Custom unpickler also failed: {e2}")
            return
    
    eng_tokenizer = assets['eng_tokenizer']
    khm_tokenizer = assets['khm_tokenizer']
    max_eng_len = assets['max_eng_len']
    max_khm_len = assets['max_khm_len']
    
    print(f"✅ English vocab size: {len(eng_tokenizer.word_index) + 1}")
    print(f"✅ Khmer vocab size: {len(khm_tokenizer.word_index) + 1}")
    print(f"✅ Max English length: {max_eng_len}")
    print(f"✅ Max Khmer length: {max_khm_len}")
    
    # Test words
    test_words = ["nhom", "tv", "sala", "srolanh", "hello"]
    
    print("\n" + "=" * 60)
    print("Testing predictions...")
    print("=" * 60)
    
    for word in test_words:
        print(f"\nTesting: '{word}'")
        
        # Clean input
        text = word.lower().strip()
        text = re.sub(r'[^a-z\s]', '', text)
        print(f"Cleaned: '{text}'")
        
        if len(text) == 0:
            print("❌ Cleaned text is empty")
            continue
        
        # Encode
        try:
            enc_seq = eng_tokenizer.texts_to_sequences([text])
            print(f"Encoded sequence: {enc_seq}")
            
            if not enc_seq or len(enc_seq[0]) == 0:
                print("❌ No tokens found - word not in vocabulary")
                # Try character by character
                print("Trying character-level encoding...")
                chars = list(text)
                enc_seq = []
                for char in chars:
                    if char in eng_tokenizer.word_index:
                        enc_seq.append(eng_tokenizer.word_index[char])
                    elif char == ' ':
                        enc_seq.append(1)  # Assume 1 is space
                    else:
                        enc_seq.append(0)  # OOV
                enc_seq = [enc_seq]
                print(f"Char-level encoding: {enc_seq}")
            
            enc_padded = pad_sequences(enc_seq, maxlen=max_eng_len, padding='post')
            print(f"Padded shape: {enc_padded.shape}")
            
            # Check start/end tokens
            if '\t' not in khm_tokenizer.word_index:
                print("❌ Start token not in Khmer tokenizer")
                continue
            if '\n' not in khm_tokenizer.word_index:
                print("❌ End token not in Khmer tokenizer")
                continue
            
            start_idx = khm_tokenizer.word_index['\t']
            end_idx = khm_tokenizer.word_index['\n']
            
            print(f"Start index: {start_idx}, End index: {end_idx}")
            
            # Greedy decoding (like Colab)
            decoder_seq = [start_idx]
            confidences = []
            
            for t in range(max_khm_len + 10):  # Extra buffer
                # Prepare decoder input
                dec_padded = pad_sequences([decoder_seq], maxlen=max_khm_len + 1, padding='post')
                
                # Predict
                preds = model.predict([enc_padded, dec_padded], verbose=0)
                
                # Get next token
                time_index = len(decoder_seq) - 1
                if time_index >= preds.shape[1]:
                    break
                
                probs = preds[0, time_index]
                next_token = int(np.argmax(probs))
                confidence = float(probs[next_token])
                
                confidences.append(confidence)
                decoder_seq.append(next_token)
                
                if next_token == end_idx or t == max_khm_len + 9:
                    break
            
            # Decode
            decoded_chars = []
            for idx in decoder_seq[1:]:  # Skip start token
                if idx == end_idx:
                    break
                char = khm_tokenizer.index_word.get(idx, '')
                decoded_chars.append(char)
            
            result = ''.join(decoded_chars)
            avg_conf = np.mean(confidences) * 100 if confidences else 0
            
            print(f"✅ Result: '{result}'")
            print(f"✅ Confidence: {avg_conf:.2f}%")
            print(f"✅ Tokens decoded: {len(decoded_chars)}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_model_directly()