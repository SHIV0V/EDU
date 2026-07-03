from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from urllib.parse import urlparse  # For URL parsing
import re  # For URL detection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True  
app.config['MAIL_USE_SSL'] = False  
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

# Initialize database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Gmail model
class Gmail(db.Model):
    __tablename__ = 'gmail'
    id = db.Column(db.Integer, primary_key=True)
    gmail = db.Column(db.Text, nullable=False)
    query = db.Column(db.Text, nullable=False)

# Profession model
class Profession(db.Model):
    __tablename__ = 'professions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    big_description = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)  # Renamed: description -> big_description
    jobs = db.Column(db.Text, nullable=True)
    relevant = db.Column(db.Text, nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)
    no_of_searches = db.Column(db.Integer, default=0)
    offered_by = db.Column(db.String(255), nullable=True)  # Added: Offered by
    expected_salary = db.Column(db.String(255), nullable=True)  # Added: Expected salary
    know_more = db.Column(db.Text, nullable=True)  # Added: Know more
    type = db.Column(db.String(2), nullable=False)  # Added: Type (c, cl, e, j)
    average_fee = db.Column(db.String(255), nullable=True)  # Added: Average Fee

# Link model
class Link(db.Model):
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True)
    name_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)  # Foreign key to professions table
    sub_column = db.Column(db.String(255), nullable=False)  # Sub-column name
    link = db.Column(db.String(255), nullable=False)  # Link URL

    profession = db.relationship('Profession', foreign_keys=[name_id], backref='links')

# Profession Relations model (Many-to-Many)
class ProfessionRelations(db.Model):
    __tablename__ = 'profession_relations'

    id = db.Column(db.Integer, primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)
    related_profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)

    profession = db.relationship('Profession', foreign_keys=[profession_id], backref='related_to')
    related_profession = db.relationship('Profession', foreign_keys=[related_profession_id])

# Function to send email
def send_email(to_email, subject, body):
    try:
        print("Starting email function...")  # Debugging
        print(f"Sending email to: {to_email}")  # Debugging

        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            print("Connecting to SMTP server...")  # Debugging
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            print("Login successful!")  # Debugging
            server.send_message(msg)
            print("Email sent successfully!")  # Debugging
        return True
    except Exception as e:
        print(f"Error sending email: {e}")  # Debugging
        return False

# Route to save support data
@app.route('/save_support_data', methods=['POST'])
def save_support_data():
    data = request.get_json()
    email = data.get('email')
    description = data.get('description')

    if not email or not description:
        return jsonify({'success': False, 'error': 'Email and description are required'}), 400

    try:
        # Save to database
        new_entry = Gmail(gmail=email, query=description)
        db.session.add(new_entry)
        db.session.commit()
        print("✅ Data saved to database.")  # Debug Log
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Database Error: {e}")  # Debug Log
        return jsonify({'success': False, 'error': str(e)}), 500

# Route to send support email
@app.route('/send_support_email', methods=['POST'])
def send_support_email():
    data = request.get_json()
    email = data.get('email')
    description = data.get('description')

    if not email or not description:
        return jsonify({'success': False, 'error': 'Email and description are required'}), 400

    try:
        # Send confirmation email
        subject = "Thank you for contacting us!"
        body = f"Thank you for reaching out! We have received your query:\n\n{description}\n\nWe will get back to you soon."
        email_sent = send_email(email, subject, body)

        if email_sent:
            print("📤 Email sent successfully!")  # Debug Log
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to send email'}), 500
    except Exception as e:
        print(f"❌ Email Error: {e}")  # Debug Log
        return jsonify({'success': False, 'error': str(e)}), 500

# Routes (existing routes remain unchanged)
@app.route('/')
def main_page():
    """Render the main course selection page."""
    return render_template('course.html')

@app.route('/course')
def course_page():
    """Explicit route for course.html to ensure accessibility."""
    return render_template('course.html')

@app.route('/search')
def search_page():
    """Render the search page."""
    return render_template('search1.html')

@app.route('/ai')
def ai_page():
    """Render the AI page."""
    return render_template('AI.html')

@app.route('/about')
def about_page():
    """Render the about page."""
    return render_template('about.html')

@app.route('/help')
def help_page():
    """Render the help page."""
    return render_template('help.html')

@app.route('/support')
def support_page():
    """Render the support page."""
    return render_template('support.html')

@app.route('/old-route')
def old_route():
    return redirect(url_for('main_page'))

@app.route('/change')
def change_page():
    """Render the change page."""
    return render_template('change.html')

@app.route('/cat')
def cat_page():
    """Render the categories page."""
    return render_template('cat.html')

@app.route('/search_professions', methods=['GET'])
def search_professions():
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10  

    if not query:
        return jsonify({'error': 'Search query cannot be empty'}), 400

    results = Profession.query.filter(Profession.name.ilike(f"%{query}%")).order_by(
        Profession.no_of_searches.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'professions': [
            {
                'id': p.id, 
                'name': p.name, 
                'big_description': p.big_description,  # Updated: description -> big_description
                'description': p.description,
                'jobs': p.jobs,   
                'relevant': p.relevant,            
                'image': f"/image/{p.id}" if p.image else None,
                'offered_by': p.offered_by,  # Added: Offered by
                'expected_salary': p.expected_salary,  # Added: Expected salary
                'know_more': p.know_more,  # Added: Know more
                'type': p.type,  # Added: Type
                'average_fee': p.average_fee  # Added: Average Fee
            }
            for p in results.items
        ],
        'total': results.total,
        'page': results.page,
        'pages': results.pages
    })

@app.route('/get_profession', methods=['GET'])
def get_profession():
    profession_id = request.args.get('id', '').strip()

    if not profession_id:
        return jsonify({'error': 'Profession ID is required'}), 400

    profession = Profession.query.get(profession_id)

    if not profession:
        return jsonify({'error': 'Profession not found'}), 404

    # Increment search count
    try:
        profession.no_of_searches += 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'id': profession.id,
        'name': profession.name,
        'big_description': profession.big_description,  # Updated: description -> big_description
        'description': profession.description,
        'jobs': profession.jobs,
        'relevant': profession.relevant,
        'image': f"/image/{profession.id}" if profession.image else None,
        'offered_by': profession.offered_by,  # Added: Offered by
        'expected_salary': profession.expected_salary,  # Added: Expected salary
        'know_more': profession.know_more,  # Added: Know more
        'type': profession.type,  # Added: Type
        'average_fee': profession.average_fee  # Added: Average Fee
    })

@app.route('/get_relevant_data', methods=['GET'])
def get_relevant_data():
    profession_id = request.args.get('profession_id', '').strip()

    if not profession_id:
        return jsonify({'error': 'Profession ID is required'}), 400

    relevant_professions = ProfessionRelations.query.filter_by(profession_id=profession_id).all()

    return jsonify([{
        'id': rel.related_profession.id,
        'name': rel.related_profession.name,
        'image': f"/image/{rel.related_profession.id}" if rel.related_profession.image else 'default-placeholder.png',
        'description': rel.related_profession.description,
        'big_description': rel.related_profession.big_description,
        'jobs': rel.related_profession.jobs,  # Updated: description -> big_description
        'offered_by': rel.related_profession.offered_by,  # Added: Offered by
        'relevant': rel.related_profession.relevant,
        'expected_salary': rel.related_profession.expected_salary,  # Added: Expected salary
        'know_more': rel.related_profession.know_more,  # Added: Know more
        'type': rel.related_profession.type,  # Added: Type
        'average_fee': rel.related_profession.average_fee  # Added: Average Fee
    } for rel in relevant_professions])

@app.route('/image/<int:profession_id>')
def get_image(profession_id):
    profession = Profession.query.get_or_404(profession_id)

    if not profession.image:
        return Response('', mimetype='image/jpeg')

    return Response(profession.image, mimetype='image/jpeg')

@app.route('/submit_support', methods=['POST'])
def submit_support():
    """Handle the support form submission.""" 
    email = request.form.get('email', '').strip()
    description = request.form.get('description', '').strip()

    print(f"📩 Form Submitted | Email: {email}, Description: {description}")  # Debug Log

    if not email or not description:
        flash('All fields are required!', 'error')
        return redirect(url_for('support_page'))

    try:
        # Save to database
        new_entry = Gmail(gmail=email, query=description)
        db.session.add(new_entry)
        db.session.commit()
        print("✅ Data saved to database.")  # Debug Log

        # Send confirmation email
        subject = "Thank you for contacting us!"
        body = f"Thank you for reaching out! We have received your query:\n\n{description}\n\nWe will get back to you soon."

        email_sent = send_email(email, subject, body)
        print(f"📤 Email Sent Status: {email_sent}")  # Debug Log

        if email_sent:
            flash('Thank you! Your request has been received. We will get back to you soon.', 'success')
        else:
            flash('Failed to send confirmation email. Please try again later.', 'error')

    except Exception as e:
        db.session.rollback()
        print(f"❌ Database Error: {e}")  # Debug Log
        flash('An error occurred. Please try again later.', 'error')

    return redirect(url_for('support_page')) 

@app.route('/get_relevant_courses', methods=['GET'])
def get_relevant_courses():
    """Fetch all courses (professions) from the database.""" 
    courses = Profession.query.all()

    return jsonify([{'name': course.name} for course in courses])

@app.route('/details')
def details():
    profession_id = request.args.get('id')  # Get the profession ID from the query parameter
    if not profession_id:
        return "Profession ID not provided.", 400

    # Fetch profession details from the database
    profession = Profession.query.get(profession_id)

    if not profession:
        return "Profession not found.", 404

    # Fetch links associated with this profession
    links = Link.query.filter_by(name_id=profession_id).all()

    # Pass profession details and links to the template
    return render_template('details.html', profession=profession, links=links)

@app.route('/get_results', methods=['GET'])
def get_results():
    type = request.args.get('type', '').strip()

    if not type:
        return jsonify({'error': 'Type is required'}), 400

    # Fetch professions based on type
    professions = Profession.query.filter_by(type=type).all()

    return jsonify([{
        'id': p.id,
        'name': p.name,
        'big_description': p.big_description,  # Updated: description -> big_description
        'description': p.description,
        'jobs': p.jobs,
        'relevant': p.relevant,
        'image': f"/image/{p.id}" if p.image else 'default-placeholder.png',
        'offered_by': p.offered_by,  # Added: Offered by
        'expected_salary': p.expected_salary,  # Added: Expected salary
        'know_more': p.know_more,  # Added: Know more
        'type': p.type,  # Added: Type
        'average_fee': p.average_fee  # Added: Average Fee
    } for p in professions])

@app.route('/get_top_searches', methods=['GET'])
def get_top_searches():
    try:
        # Fetch top 3 professions with the highest no_of_searches
        top_searches = Profession.query.order_by(Profession.no_of_searches.desc()).limit(3).all()

        return jsonify({
            'top_searches': [
                {
                    'id': p.id,
                    'name': p.name,
                    
                    'description': p.description,
                    'jobs': p.jobs,
                    'relevant': p.relevant,
                    'image': f"/image/{p.id}" if p.image else None,
                    'offered_by': p.offered_by,
                    'expected_salary': p.expected_salary,
                    'know_more': p.know_more,
                    'type': p.type,
                    'average_fee': p.average_fee
                }
                for p in top_searches
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=True)