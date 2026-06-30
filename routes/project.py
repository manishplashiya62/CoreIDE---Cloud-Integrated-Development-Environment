import io
import zipfile
import os
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, send_file, flash
from flask_login import login_required, current_user
from models import db, Project, File, ExecutionHistory
from datetime import datetime, timezone

project_bp = Blueprint('project', __name__)

# Helper to detect language
def get_language_from_filename(filename):
    if '.' not in filename:
        return 'text'
    ext = filename.rsplit('.', 1)[-1].lower()
    lang_map = {
        'py': 'python',
        'js': 'javascript',
        'c': 'c',
        'cpp': 'cpp',
        'h': 'c',
        'hpp': 'cpp',
        'java': 'java',
        'html': 'html',
        'css': 'css',
        'json': 'javascript'
    }
    return lang_map.get(ext, 'text')

@project_bp.route('/dashboard')
@login_required
def dashboard():
    user_projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).all()
    
    # Calculate stats
    total_projects = len(user_projects)
    total_executions = ExecutionHistory.query.filter_by(user_id=current_user.id).count()
    
    # Get recent executions
    recent_executions = ExecutionHistory.query.filter_by(user_id=current_user.id)\
        .order_by(ExecutionHistory.created_at.desc()).limit(5).all()
        
    return render_template(
        'dashboard.html', 
        projects=user_projects, 
        total_projects=total_projects,
        total_executions=total_executions,
        recent_executions=recent_executions
    )

# --- Project CRUD APIs ---

@project_bp.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    template_lang = data.get('template') # optional: e.g. python, c, cpp, java, javascript
    
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
        
    new_project = Project(user_id=current_user.id, project_name=project_name)
    db.session.add(new_project)
    db.session.commit()
    
    # Pre-create default entry file if template selected
    if template_lang:
        filename_map = {
            'python': 'main.py',
            'javascript': 'index.js',
            'c': 'main.c',
            'cpp': 'main.cpp',
            'java': 'Main.java'
        }
        content_map = {
            'python': 'print("Hello from Python!")\n',
            'javascript': 'console.log("Hello from JavaScript!");\n',
            'c': '#include <stdio.h>\n\nint main() {\n    printf("Hello from C!\\n");\n    return 0;\n}\n',
            'cpp': '#include <iostream>\n\nint main() {\n    std::cout << "Hello from C++!" << std::endl;\n    return 0;\n}\n',
            'java': 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java!");\n    }\n}\n'
        }
        
        filename = filename_map.get(template_lang, 'main.py')
        content = content_map.get(template_lang, '# Start writing code\n')
        
        default_file = File(
            project_id=new_project.id,
            name=filename,
            is_folder=False,
            parent_id=None,
            language=template_lang,
            content=content
        )
        db.session.add(default_file)
        db.session.commit()
        
    return jsonify(new_project.to_dict()), 201

@project_bp.route('/api/projects/<int:project_id>', methods=['PUT', 'DELETE'])
@login_required
def modify_project(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted successfully'})
        
    elif request.method == 'PUT':
        data = request.get_json() or {}
        project_name = data.get('project_name')
        if not project_name:
            return jsonify({'error': 'Project name is required'}), 400
        project.project_name = project_name
        project.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify(project.to_dict())

# --- File Manager APIs ---

@project_bp.route('/api/projects/<int:project_id>/tree')
@login_required
def get_project_tree(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    files = File.query.filter_by(project_id=project.id).all()
    return jsonify([f.to_dict() for f in files])

@project_bp.route('/api/projects/<int:project_id>/files', methods=['POST'])
@login_required
def create_file(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}
    name = data.get('name')
    is_folder = data.get('is_folder', False)
    parent_id = data.get('parent_id')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
        
    # Check parent node
    if parent_id:
        parent = File.query.filter_by(id=parent_id, project_id=project.id, is_folder=True).first()
        if not parent:
            return jsonify({'error': 'Parent folder does not exist'}), 400
            
    language = get_language_from_filename(name) if not is_folder else None
    
    new_node = File(
        project_id=project.id,
        name=name,
        is_folder=is_folder,
        parent_id=parent_id,
        language=language,
        content="" if not is_folder else None
    )
    db.session.add(new_node)
    
    # Update project updated timestamp
    project.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify(new_node.to_dict()), 201

@project_bp.route('/api/files/<int:file_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def file_operations(file_id):
    # Check file exists and is owned by the current user
    file_node = File.query.join(Project).filter(File.id == file_id, Project.user_id == current_user.id).first_or_404()
    project = Project.query.filter_by(id=file_node.project_id).first()
    
    if request.method == 'GET':
        return jsonify(file_node.to_dict())
        
    elif request.method == 'DELETE':
        db.session.delete(file_node)
        project.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({'message': 'File or folder deleted successfully'})
        
    elif request.method == 'PUT':
        data = request.get_json() or {}
        name = data.get('name')
        content = data.get('content')
        
        if name:
            file_node.name = name
            if not file_node.is_folder:
                file_node.language = get_language_from_filename(name)
                
        if content is not None and not file_node.is_folder:
            file_node.content = content
            
        file_node.updated_at = datetime.now(timezone.utc)
        project.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify(file_node.to_dict())

# --- ZIP Export and Import Routes ---

@project_bp.route('/project/<int:project_id>/download')
@login_required
def download_project(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    all_nodes = File.query.filter_by(project_id=project.id).all()
    node_map = {node.id: node for node in all_nodes}
    
    def resolve_path(node):
        parts = []
        curr = node
        while curr:
            parts.insert(0, curr.name)
            if curr.parent_id:
                curr = node_map.get(curr.parent_id)
            else:
                curr = None
        return "/".join(parts)
        
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for node in all_nodes:
            path = resolve_path(node)
            if node.is_folder:
                # Add folder entry
                zip_file.writestr(path + "/", "")
            else:
                zip_file.writestr(path, node.content or "")
                
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{project.project_name}.zip"
    )

@project_bp.route('/project/upload', methods=['POST'])
@login_required
def upload_project():
    if 'file' not in request.files:
        flash('No file provided.', 'danger')
        return redirect(url_for('project.dashboard'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('project.dashboard'))
        
    if file and file.filename.endswith('.zip'):
        try:
            zip_data = io.BytesIO(file.read())
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                project_name = file.filename.rsplit('.', 1)[0]
                
                project = Project(user_id=current_user.id, project_name=project_name)
                db.session.add(project)
                db.session.commit()
                
                path_to_node = {}
                namelist = sorted(zip_ref.namelist(), key=lambda p: p.count('/'))
                
                for path in namelist:
                    if not path.strip() or path.startswith('__MACOSX') or '.DS_Store' in path:
                        continue
                        
                    parts = [p for p in path.split('/') if p]
                    if not parts:
                        continue
                        
                    is_folder = path.endswith('/')
                    name = parts[-1]
                    
                    parent_path = "/".join(parts[:-1])
                    parent_node = path_to_node.get(parent_path) if parent_path else None
                    parent_id = parent_node.id if parent_node else None
                    
                    lang = None
                    if not is_folder:
                        lang = get_language_from_filename(name)
                        
                    content = ""
                    if not is_folder:
                        try:
                            content = zip_ref.read(path).decode('utf-8')
                        except Exception:
                            content = "// (Binary file or decoding issue)"
                            
                    new_node = File(
                        project_id=project.id,
                        name=name,
                        is_folder=is_folder,
                        parent_id=parent_id,
                        language=lang,
                        content=content if not is_folder else None
                    )
                    db.session.add(new_node)
                    db.session.commit()
                    
                    resolved_path = "/".join(parts)
                    path_to_node[resolved_path] = new_node
                    
            flash('Project uploaded and imported successfully!', 'success')
        except Exception as e:
            flash(f'Error importing project: {str(e)}', 'danger')
    else:
        flash('Invalid file format. Please upload a .zip file.', 'danger')
        
    return redirect(url_for('project.dashboard'))
