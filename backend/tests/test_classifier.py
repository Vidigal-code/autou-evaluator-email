import sys
import os
import pytest
from unittest.mock import patch

# Ajusta o sys.path para garantir que o src esteja acessível
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from classifier import classify_email

@patch("classifier.requests.post")
def test_classify_produtivo(mock_post):
    # Simula resposta esperada da IA
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"response": "produtivo"}
    email = "Gostaria de saber o status do meu pedido financeiro."
    resultado = classify_email(email)
    assert resultado == "produtivo"

@patch("classifier.requests.post")
def test_classify_improdutivo(mock_post):
    # Simula resposta esperada da IA
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"response": "improdutivo"}
    email = "Feliz aniversário para toda a equipe!"
    resultado = classify_email(email)
    assert resultado == "improdutivo"