from flask import Flask, request, jsonify
from flask_cors import CORS  # Importer CORS
import re
import numpy as np
import sympy as sp
import requests
from flask_cors import CORS  # Importer CORS

app = Flask(__name__)

# Activer CORS pour toutes les routes
CORS(app)  # Cela autorise toutes les origines, mais vous pouvez être plus spécifique si nécessaire.

# URL de l'API Spring Boot pour enregistrer les résultats
SPRING_BOOT_API_URL = "http://spring-app:8082/api/store-polynomial"

# Fonction pour remplacer x2 par x**2, x3 par x**3, etc., et 1x2 par 1*x**2
def preprocess_expression(expr):
    expr = re.sub(r'x(\d+)', r'x**\1', expr)  # Remplacer x2 par x**2, etc.
    expr = re.sub(r'(\d?)x(\d+)', r'\1*x**\2', expr)  # Ajouter '*' avant les puissances de x
    expr = re.sub(r'(?<=\d)x', r'*x', expr)  # Insérer '*' entre un chiffre et 'x'
    return expr

# Fonction pour calculer les racines numériques d'un polynôme à partir d'une expression
def calculate_roots_from_expression(expr):
    # Prétraiter l'expression
    expr = preprocess_expression(expr)
    
    # Convertir l'expression en polynôme sympy
    x = sp.symbols('x')
    polynome = sp.sympify(expr)
    
    # Vérifier si l'expression est bien un polynôme
    if not isinstance(polynome, sp.Poly):
        polynome = sp.Poly(polynome, x)
    
    # Extraire les coefficients du polynôme
    coefs = polynome.all_coeffs()
    
    # Calculer les racines numériques avec numpy
    roots = np.roots(coefs)
    
    # Filtrer pour ne garder que les racines complexes avec une partie imaginaire non nulle
    complex_roots = [root for root in roots if np.imag(root) != 0]
    
    return complex_roots

# Fonction pour factoriser un polynôme symbolique
def factorize_polynomial(expr):
    x = sp.symbols('x')
    expr = preprocess_expression(expr)  # Prétraitement de l'expression
    polynome = sp.sympify(expr)  # Convertir l'expression en objet SymPy
    return sp.factor(polynome)

# Fonction pour simplifier une expression symbolique
def simplify_expression(expr):
    x = sp.symbols('x')
    expr = preprocess_expression(expr)  # Prétraitement de l'expression
    polynome = sp.sympify(expr)  # Convertir l'expression en objet SymPy
    return sp.simplify(polynome)

# Fonction pour formater les expressions symboliques
def format_expression(expr):
    expr_str = str(expr)
    expr_str = re.sub(r'x\*\*(\d+)', r'x\1', expr_str)  # Remplacer x**2 par x2, etc.
    expr_str = re.sub(r'1\*x\*\*2', r'x**2', expr_str)  # Remplacer 1*x**2 par x**2
    expr_str = re.sub(r'1\*x', r'x', expr_str)  # Remplacer 1*x par x
    return expr_str

@app.route('/calculateWithNumpy', methods=['POST'])
def calculate_with_numpy():
    try:
        # Récupérer les données de la requête
        data = request.get_json()
        expression = data.get('expression', '')
        user_id = data.get('userId', None)  # Récupérer le userId

        if not expression:
            return jsonify({'error': 'No expression provided'}), 400
        if not user_id:
            return jsonify({'error': 'No userId provided'}), 400
        
        # Calcul des racines numériques
        roots = calculate_roots_from_expression(expression)
        
        # Factoriser l'expression
        factored_expression = factorize_polynomial(expression)
        formatted_factored_expression = format_expression(factored_expression)
        
        # Simplifier l'expression
        simplified_expression = simplify_expression(expression)
        formatted_simplified_expression = format_expression(simplified_expression)
        
        # Format des racines complexes pour affichage
        roots_list = [str(root) for root in roots]
        
        # Créer un dictionnaire avec les résultats
        result = {
            'userId': user_id,  # Ajouter le userId dans le résultat
            'roots': roots_list,
            'simplifiedExpression': formatted_simplified_expression,
            'factoredExpression': formatted_factored_expression
        }

        # Envoi des résultats à l'API Spring Boot
        response = requests.post(SPRING_BOOT_API_URL, json=result)
        if response.status_code == 200:
            # Inclure les résultats dans la réponse
            return jsonify(result), 200
        else:
            return jsonify({"error": "Erreur lors de l'enregistrement dans Spring Boot."}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5004, debug=True)