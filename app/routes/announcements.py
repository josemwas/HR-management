from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.employee import Employee
from datetime import datetime

bp = Blueprint('announcements', __name__, url_prefix='/api/announcements')

# Mock Announcement model
class Announcement:
    def __init__(self, id, title, content, category, priority, target_audience, author, created_date, status, views=0):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.priority = priority
        self.target_audience = target_audience
        self.author = author
        self.created_date = created_date
        self.status = status
        self.views = views
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'priority': self.priority,
            'target_audience': self.target_audience,
            'author': self.author,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'status': self.status,
            'views': self.views
        }

# Mock data
mock_announcements = [
    Announcement(1, 'Emergency System Maintenance', 'Emergency system maintenance scheduled for tonight from 10 PM to 2 AM. All systems will be temporarily unavailable during this period.', 'urgent', 'urgent', 'all', 'IT Department', datetime(2024, 12, 10), 'active', 124),
    Announcement(2, 'Holiday Party 2024', 'Join us for our annual holiday party on December 20th at 6 PM in the main conference room.', 'events', 'normal', 'all', 'HR Team', datetime(2024, 12, 8), 'active', 89),
    Announcement(3, 'Updated Remote Work Policy', 'We\'ve updated our remote work policy to provide more flexibility. Employees can now work from home up to 3 days per week.', 'policy', 'high', 'all', 'Leadership Team', datetime(2024, 12, 5), 'active', 156),
    Announcement(4, 'Q1 2025 All-Hands Meeting', 'Mark your calendars for our Q1 2025 all-hands meeting where we\'ll discuss company goals and achievements.', 'general', 'normal', 'all', 'CEO Office', datetime(2024, 12, 15), 'scheduled', 0),
]

@bp.route('', methods=['GET'])
@jwt_required()
def get_announcements():
    """Get all announcements"""
    try:
        return jsonify([ann.to_dict() for ann in mock_announcements]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['POST'])
@jwt_required()
def create_announcement():
    """Create a new announcement"""
    try:
        data = request.json
        
        new_announcement = Announcement(
            id=len(mock_announcements) + 1,
            title=data.get('title'),
            content=data.get('content'),
            category=data.get('category'),
            priority=data.get('priority', 'normal'),
            target_audience=data.get('target_audience', 'all'),
            author=data.get('author', 'System'),
            created_date=datetime.utcnow(),
            status='active'
        )
        
        mock_announcements.append(new_announcement)
        
        return jsonify(new_announcement.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:announcement_id>', methods=['GET'])
@jwt_required()
def get_announcement(announcement_id):
    """Get specific announcement"""
    try:
        announcement = next((a for a in mock_announcements if a.id == announcement_id), None)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Increment view count
        announcement.views += 1
        
        return jsonify(announcement.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:announcement_id>', methods=['PUT'])
@jwt_required()
def update_announcement(announcement_id):
    """Update announcement"""
    try:
        announcement = next((a for a in mock_announcements if a.id == announcement_id), None)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        data = request.json
        announcement.title = data.get('title', announcement.title)
        announcement.content = data.get('content', announcement.content)
        announcement.category = data.get('category', announcement.category)
        announcement.priority = data.get('priority', announcement.priority)
        announcement.status = data.get('status', announcement.status)
        
        return jsonify(announcement.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:announcement_id>', methods=['DELETE'])
@jwt_required()
def delete_announcement(announcement_id):
    """Delete announcement"""
    try:
        global mock_announcements
        mock_announcements = [a for a in mock_announcements if a.id != announcement_id]
        
        return jsonify({'message': 'Announcement deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_announcement_stats():
    """Get announcement statistics"""
    try:
        stats = {
            'total_announcements': len(mock_announcements),
            'active_announcements': len([a for a in mock_announcements if a.status == 'active']),
            'scheduled_announcements': len([a for a in mock_announcements if a.status == 'scheduled']),
            'avg_read_rate': 87
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:announcement_id>/analytics', methods=['GET'])
@jwt_required()
def get_announcement_analytics(announcement_id):
    """Get analytics for specific announcement"""
    try:
        announcement = next((a for a in mock_announcements if a.id == announcement_id), None)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        analytics = {
            'views': announcement.views,
            'read_rate': 87,  # Mock data
            'engagement_score': 4.2,
            'comments': 12
        }
        
        return jsonify(analytics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500