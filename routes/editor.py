from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Project

editor_bp = Blueprint('editor', __name__)

@editor_bp.route('/project/<int:project_id>')
@login_required
def open_editor(project_id):
    # Ensure project exists and is owned by current user
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    return render_template('editor.html', project=project)
