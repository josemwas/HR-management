from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

documents = Blueprint('documents', __name__)

# Mock Document class for demonstration
class Document:
    def __init__(self, id, title, description, file_type, file_path, category, upload_date, uploaded_by, department=None, is_confidential=False, version="1.0"):
        self.id = id
        self.title = title
        self.description = description
        self.file_type = file_type
        self.file_path = file_path
        self.category = category
        self.upload_date = upload_date
        self.uploaded_by = uploaded_by
        self.department = department
        self.is_confidential = is_confidential
        self.version = version

# Mock data
mock_documents = [
    Document(1, "Employee Handbook", "Complete guide for all employees", "PDF", "/uploads/handbook.pdf", "HR Policies", datetime.now() - timedelta(days=30), "HR Admin", "Human Resources", False, "2.1"),
    Document(2, "Privacy Policy", "Company privacy and data protection policy", "PDF", "/uploads/privacy.pdf", "Legal", datetime.now() - timedelta(days=15), "Legal Team", "Legal", False, "1.5"),
    Document(3, "Code of Conduct", "Professional behavior guidelines", "PDF", "/uploads/conduct.pdf", "HR Policies", datetime.now() - timedelta(days=20), "HR Admin", "Human Resources", False, "1.2"),
    Document(4, "IT Security Guidelines", "Information security best practices", "PDF", "/uploads/security.pdf", "IT Policies", datetime.now() - timedelta(days=10), "IT Admin", "IT", True, "3.0"),
    Document(5, "Financial Procedures", "Accounting and finance procedures", "DOCX", "/uploads/finance.docx", "Finance", datetime.now() - timedelta(days=5), "Finance Manager", "Finance", True, "1.8"),
]

@documents.route('/api/documents', methods=['GET'])
@jwt_required()
def get_documents():
    """Get all documents with filtering"""
    try:
        category = request.args.get('category')
        search = request.args.get('search', '').lower()
        department = request.args.get('department')
        
        filtered_docs = mock_documents
        
        if category:
            filtered_docs = [doc for doc in filtered_docs if doc.category == category]
        
        if department:
            filtered_docs = [doc for doc in filtered_docs if doc.department == department]
        
        if search:
            filtered_docs = [doc for doc in filtered_docs if 
                           search in doc.title.lower() or 
                           search in doc.description.lower()]
        
        documents_data = []
        for doc in filtered_docs:
            documents_data.append({
                'id': doc.id,
                'title': doc.title,
                'description': doc.description,
                'file_type': doc.file_type,
                'file_path': doc.file_path,
                'category': doc.category,
                'upload_date': doc.upload_date.isoformat(),
                'uploaded_by': doc.uploaded_by,
                'department': doc.department,
                'is_confidential': doc.is_confidential,
                'version': doc.version
            })
        
        return jsonify({
            'documents': documents_data,
            'total': len(documents_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents.route('/api/documents/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get specific document details"""
    try:
        document = next((doc for doc in mock_documents if doc.id == document_id), None)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'id': document.id,
            'title': document.title,
            'description': document.description,
            'file_type': document.file_type,
            'file_path': document.file_path,
            'category': document.category,
            'upload_date': document.upload_date.isoformat(),
            'uploaded_by': document.uploaded_by,
            'department': document.department,
            'is_confidential': document.is_confidential,
            'version': document.version
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents.route('/api/documents', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a new document"""
    try:
        data = request.json
        
        # Create new document
        new_id = max([doc.id for doc in mock_documents]) + 1
        new_document = Document(
            id=new_id,
            title=data.get('title'),
            description=data.get('description'),
            file_type=data.get('file_type', 'PDF'),
            file_path=f"/uploads/{data.get('title', 'document').lower().replace(' ', '_')}.pdf",
            category=data.get('category'),
            upload_date=datetime.now(),
            uploaded_by=get_jwt_identity(),
            department=data.get('department'),
            is_confidential=data.get('is_confidential', False),
            version="1.0"
        )
        
        mock_documents.append(new_document)
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': {
                'id': new_document.id,
                'title': new_document.title,
                'description': new_document.description,
                'file_type': new_document.file_type,
                'file_path': new_document.file_path,
                'category': new_document.category,
                'upload_date': new_document.upload_date.isoformat(),
                'uploaded_by': new_document.uploaded_by,
                'department': new_document.department,
                'is_confidential': new_document.is_confidential,
                'version': new_document.version
            }
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents.route('/api/documents/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """Delete a document"""
    try:
        global mock_documents
        
        document = next((doc for doc in mock_documents if doc.id == document_id), None)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        mock_documents = [doc for doc in mock_documents if doc.id != document_id]
        
        return jsonify({'message': 'Document deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents.route('/api/documents/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all document categories"""
    try:
        categories = list(set([doc.category for doc in mock_documents]))
        return jsonify({'categories': categories})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents.route('/api/documents/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """Get all departments with documents"""
    try:
        departments = list(set([doc.department for doc in mock_documents if doc.department]))
        return jsonify({'departments': departments})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents.route('/api/documents/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get document analytics"""
    try:
        total_documents = len(mock_documents)
        confidential_docs = len([doc for doc in mock_documents if doc.is_confidential])
        
        # Count by category
        category_stats = {}
        for doc in mock_documents:
            category_stats[doc.category] = category_stats.get(doc.category, 0) + 1
        
        # Count by department
        department_stats = {}
        for doc in mock_documents:
            if doc.department:
                department_stats[doc.department] = department_stats.get(doc.department, 0) + 1
        
        # Recent uploads (last 30 days)
        recent_date = datetime.now() - timedelta(days=30)
        recent_uploads = len([doc for doc in mock_documents if doc.upload_date >= recent_date])
        
        return jsonify({
            'total_documents': total_documents,
            'confidential_documents': confidential_docs,
            'public_documents': total_documents - confidential_docs,
            'recent_uploads': recent_uploads,
            'category_distribution': category_stats,
            'department_distribution': department_stats,
            'average_documents_per_department': round(total_documents / len(department_stats) if department_stats else 0, 1)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500