from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from models import db, User, Project, ExecutionHistory

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access denied. Administrators only.', 'danger')
        return redirect(url_for('project.dashboard'))
        
    users = User.query.all()
    projects_count = Project.query.count()
    executions_count = ExecutionHistory.query.count()
    
    # Calculate average execution time
    histories = ExecutionHistory.query.all()
    avg_exec_time = 0.0
    if histories:
        avg_exec_time = sum(h.execution_time or 0.0 for h in histories) / len(histories)
        
    return render_template(
        'admin.html',
        users=users,
        projects_count=projects_count,
        executions_count=executions_count,
        avg_exec_time=round(avg_exec_time, 3)
    )

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    if current_user.id == user_id:
        return jsonify({'error': 'You cannot delete yourself'}), 400
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User {user.username} deleted successfully.", 'success')
    return redirect(url_for('admin.admin_panel'))
