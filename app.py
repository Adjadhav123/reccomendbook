from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np

import os
popular_df = pickle.load(open(os.path.join('models', 'popular.pkl'), 'rb'))
pt = pickle.load(open(os.path.join('models', 'pt.pkl'), 'rb'))
books = pickle.load(open(os.path.join('models', 'books.pkl'), 'rb'))
similarity_score = pickle.load(open(os.path.join('models', 'similarity_score.pkl'), 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['Num_rating'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    if user_input not in pt.index:
        return render_template('recommend.html', 
                             error="Sorry, we couldn't find that book in our database. Please try another title.")
    
    # Show loading indicator for better UX
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    if not data:
        return render_template('recommend.html', no_results=True)

    return render_template('recommend.html', data=data)

@app.route('/get_suggestions')
def get_suggestions():
    query = request.args.get('query', '').lower()
    
    if not query or len(query) < 3:
        return jsonify({'suggestions': []})
    
    # Get all book titles from the pivot table
    all_titles = list(pt.index)
    
    # Filter titles that contain the query (case insensitive)
    suggestions = [title for title in all_titles if query in title.lower()]
    
    # Limit to top 10 suggestions
    suggestions = suggestions[:10]
    
    return jsonify({'suggestions': suggestions})

if __name__ == '__main__':
    app.run(debug=True)
