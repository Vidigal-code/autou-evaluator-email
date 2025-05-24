import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from responder import clean_response

def test_clean_response_no_brackets():
    text = "Atenciosamente, [Seu Nome] (Gerente) {Empresa XYZ}\nObrigado!"
    cleaned = clean_response(text)
    assert "[" not in cleaned and "]" not in cleaned
    assert "(" not in cleaned and ")" not in cleaned
    assert "{" not in cleaned and "}" not in cleaned
    assert "Atenciosamente" not in cleaned