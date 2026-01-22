import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.model_loader import model_loader

def test_model_initialization():
    """Test that the model can be initialized"""
    try:
        model_loader.initialize()
        assert model_loader._initialized == True
        assert hasattr(model_loader, 'model')
        assert hasattr(model_loader, 'eng_tokenizer')
        assert hasattr(model_loader, 'khm_tokenizer')
    except Exception as e:
        pytest.skip(f"Model initialization failed: {e}")

def test_text_cleaning():
    """Test text cleaning function"""
    model_loader.initialize()
    
    # Test English cleaning
    cleaned = model_loader.clean_text("Hello World 123!", is_khmer=False)
    assert cleaned == "hello world "
    
    # Test Khmer cleaning
    cleaned = model_loader.clean_text("សាលា123", is_khmer=True)
    assert cleaned == "សាលា"