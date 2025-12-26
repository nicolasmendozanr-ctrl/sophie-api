from flask import Flask, request, jsonify
from supabase import create_client
import os

app = Flask(__name__)

# Connexion Supabase
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        query = data.get('query', '').lower()
        
        # Chercher dans manuel_vinci par mots-clés
        response = supabase.table('manuel_vinci').select('*').execute()
        
        best_match = None
        best_score = 0
        
        for row in response.data:
            score = 0
            mots_cles = row.get('mots_cles', [])
            
            # Compter les mots-clés qui matchent
            for mot in mots_cles:
                if mot.lower() in query:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = row
        
        if best_match and best_score > 0:
            return jsonify({
                'success': True,
                'reponse': best_match['reponse'],
                'categorie': best_match['categorie']
            })
        else:
            return jsonify({
                'success': True,
                'reponse': 'Notre standard est nominatif. Puis-je avoir le nom de la personne que vous souhaitez joindre ?',
                'categorie': 'default'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/log_appel', methods=['POST'])
def log_appel():
    try:
        data = request.json
        
        # Enregistrer l'appel dans la base
        response = supabase.table('appels_log').insert({
            'appelant_nom': data.get('nom'),
            'appelant_societe': data.get('societe'),
            'objet': data.get('objet'),
            'issue': data.get('issue'),
            'resume': data.get('resume'),
            'duree_secondes': data.get('duree')
        }).execute()
        
        return jsonify({'success': True, 'id': response.data[0]['id']})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/add_learning', methods=['POST'])
def add_learning():
    try:
        data = request.json
        
        # Sophie ajoute une note d'apprentissage
        response = supabase.table('sophie_learning').insert({
            'situation': data.get('situation'),
            'ce_qui_a_marche': data.get('ce_qui_a_marche'),
            'ce_qui_a_pas_marche': data.get('ce_qui_a_pas_marche'),
            'amelioration': data.get('amelioration'),
            'nouvelle_regle': data.get('nouvelle_regle'),
            'appel_id': data.get('appel_id')
        }).execute()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'sophie-api'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
