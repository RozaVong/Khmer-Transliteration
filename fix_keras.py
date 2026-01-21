#!/usr/bin/env python3
"""
Quick fix for Keras 3 compatibility issues
"""
import sys
import os
import pickle

def fix_pickle_file():
    """Fix pickle file for Keras 3 compatibility"""
    pickle_path = "model/khmer_Glish.pkl"
    backup_path = "model/khmer_Glish.pkl.backup"
    
    if not os.path.exists(pickle_path):
        print(f"❌ Pickle file not found: {pickle_path}")
        return False
    
    try:
        # Backup original
        import shutil
        shutil.copy2(pickle_path, backup_path)
        print(f"✅ Backed up to: {backup_path}")
        
        # Load with custom unpickler
        class CustomUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                # Fix keras module paths
                if module.startswith('keras.src.'):
                    module = module.replace('keras.src.', 'keras.')
                elif module == 'keras.src':
                    module = 'keras'
                return super().find_class(module, name)
        
        with open(pickle_path, 'rb') as f:
            unpickler = CustomUnpickler(f)
            assets = unpickler.load()
        
        # Save with default pickle
        with open(pickle_path, 'wb') as f:
            pickle.dump(assets, f)
        
        print("✅ Pickle file fixed for Keras 3 compatibility")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing pickle file: {str(e)}")
        return False

def test_model_loading():
    """Test if model can be loaded"""
    try:
        # Try keras 3 first
        import keras
        print(f"✅ Keras version: {keras.__version__}")
        
        model_path = "model/khmer_Glish.keras"
        if os.path.exists(model_path):
            model = keras.saving.load_model(model_path)
            print("✅ Model loaded successfully with keras.saving.load_model")
            return True
        else:
            print(f"❌ Model file not found: {model_path}")
            return False
            
    except ImportError as e:
        print(f"❌ Keras import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Model load error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Keras 3 Compatibility Fix")
    print("=" * 60)
    
    print("\n1. Testing model loading...")
    if test_model_loading():
        print("✅ Model loading test passed")
    else:
        print("❌ Model loading test failed")
    
    print("\n2. Fixing pickle file...")
    if fix_pickle_file():
        print("✅ Pickle file fixed")
    else:
        print("❌ Failed to fix pickle file")
    
    print("\n3. Testing again...")
    if test_model_loading():
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed")
    
    print("\n💡 If issues persist, try:")
    print("   - pip install --upgrade keras tensorflow")
    print("   - Check model files exist in model/ directory")
    print("   - Ensure you have khmer_Glish.keras and khmer_Glish.pkl")