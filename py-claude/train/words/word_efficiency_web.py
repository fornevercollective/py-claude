#!/usr/bin/env python3
"""
Word Efficiency Web Interface
Flask web application for managing and visualizing word efficiency data
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import sqlite3
import json
import plotly.graph_objs as go
import plotly.utils
from datetime import datetime
import os
import tempfile
from word_efficiency_db import WordEfficiencyDB  # Import our database class

app = Flask(__name__)
app.secret_key = 'word_efficiency_secret_key_2024'

# Initialize database
db = WordEfficiencyDB()

@app.route('/')
def index():
    """Main dashboard"""
    stats = db.get_category_stats()
    
    # Create visualization data
    categories = [s['category'] for s in stats]
    word_counts = [s['word_count'] for s in stats]
    impact_types = [s['impact_type'] for s in stats]
    
    # Color mapping
    colors = {'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}
    bar_colors = [colors.get(impact, '#6c757d') for impact in impact_types]
    
    # Create bar chart
    bar_fig = go.Figure(data=[
        go.Bar(x=categories, y=word_counts, marker_color=bar_colors, name='Word Count')
    ])
    bar_fig.update_layout(
        title='Words by Category',
        xaxis_title='Category',
        yaxis_title='Number of Words',
        template='plotly_white'
    )
    
    # Create pie chart for efficiency distribution
    efficient_count = sum(1 for s in stats if s['impact_type'] == 'positive')
    inefficient_count = sum(1 for s in stats if s['impact_type'] == 'negative')
    neutral_count = sum(1 for s in stats if s['impact_type'] == 'neutral')
    
    pie_fig = go.Figure(data=[
        go.Pie(labels=['Efficient Categories', 'Inefficient Categories', 'Neutral Categories'],
               values=[efficient_count, inefficient_count, neutral_count],
               marker_colors=['#28a745', '#dc3545', '#6c757d'])
    ])
    pie_fig.update_layout(title='Category Distribution by Impact Type')
    
    # Convert plots to JSON
    bar_graph_json = json.dumps(bar_fig, cls=plotly.utils.PlotlyJSONEncoder)
    pie_graph_json = json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('dashboard.html', 
                         stats=stats,
                         bar_graph_json=bar_graph_json,
                         pie_graph_json=pie_graph_json)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Text analysis page"""
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if not text:
            flash('Please enter text to analyze', 'error')
            return redirect(url_for('analyze'))
        
        result = db.analyze_text_efficiency(text)
        return render_template('analyze.html', result=result, analyzed_text=text)
    
    return render_template('analyze.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for text analysis"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    result = db.analyze_text_efficiency(data['text'])
    return jsonify(result)

@app.route('/search')
def search():
    """Word search page"""
    pattern = request.args.get('q', '')
    category = request.args.get('category', '')
    efficiency_filter = request.args.get('efficiency', '')
    
    results = []
    if pattern:
        is_efficient = None
        if efficiency_filter == 'efficient':
            is_efficient = True
        elif efficiency_filter == 'inefficient':
            is_efficient = False
            
        results = db.search_words(pattern, category if category else None, is_efficient)
    
    # Get available categories for filter dropdown
    stats = db.get_category_stats()
    categories = [s['category'] for s in stats]
    
    return render_template('search.html', 
                         results=results, 
                         search_pattern=pattern,
                         selected_category=category,
                         selected_efficiency=efficiency_filter,
                         categories=categories)

@app.route('/categories')
def categories():
    """Categories overview page"""
    stats = db.get_category_stats()
    return render_template('categories.html', stats=stats)

@app.route('/category/<category_name>')
def category_detail(category_name):
    """Detailed view of a specific category"""
    # Get words in this category
    words = db.search_words('', category_name)
    
    # Get category info
    stats = db.get_category_stats()
    category_info = next((s for s in stats if s['category'] == category_name), None)
    
    if not category_info:
        flash(f'Category "{category_name}" not found', 'error')
        return redirect(url_for('categories'))
    
    # Separate efficient and inefficient words
    efficient_words = [w for w in words if w['is_efficient']]
    inefficient_words = [w for w in words if not w['is_efficient']]
    
    return render_template('category_detail.html',
                         category_info=category_info,
                         efficient_words=efficient_words,
                         inefficient_words=inefficient_words,
                         total_words=len(words))

@app.route('/recommendations')
def recommendations():
    """Efficiency recommendations page"""
    target = float(request.args.get('target', 80.0))
    recommendations = db.get_efficiency_recommendations(target)
    return render_template('recommendations.html', 
                         recommendations=recommendations, 
                         target=target)

@app.route('/add_words', methods=['GET', 'POST'])
def add_words():
    """Add new words to database"""
    if request.method == 'POST':
        words_text = request.form.get('words', '').strip()
        category = request.form.get('category', '').strip()
        is_efficient = request.form.get('is_efficient') == 'on'
        impact = float(request.form.get('impact', 0.0))
        
        if not words_text or not category:
            flash('Please provide both words and category', 'error')
            return redirect(url_for('add_words'))
        
        # Parse words (comma or newline separated)
        words = [w.strip() for w in words_text.replace('\n', ',').split(',') if w.strip()]
        
        if not words:
            flash('No valid words found', 'error')
            return redirect(url_for('add_words'))
        
        try:
            db.bulk_insert_words(words, category, is_efficient=is_efficient, efficiency_impact=impact)
            flash(f'Successfully added {len(words)} words to category "{category}"', 'success')
            return redirect(url_for('categories'))
        except Exception as e:
            flash(f'Error adding words: {str(e)}', 'error')
    
    # Get existing categories for dropdown
    stats = db.get_category_