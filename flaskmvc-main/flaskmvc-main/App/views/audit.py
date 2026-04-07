from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import current_user, jwt_required

from App.controllers.room import *
from App.controllers.audit import *
from App.controllers.checkevent import *
from App.controllers.user import *
from App.controllers.building import *
from App.controllers.assetassignment import *
from App.controllers.floor import *
from App.controllers.permissions import role_required
from App.controllers.relocation import create_relocation
from App.controllers.missingdevices import mark_asset_missing
from App.database import db

audit_views = Blueprint('audit_views', __name__, template_folder='../templates')


@audit_views.route('/audit-list')
@jwt_required()
def audit_list():
    audits = get_all_audits_json()
    active_audit = get_active_audit()
    return render_template('audit_list.html', audits=audits, active_audit=active_audit)


@audit_views.route('/audit-list/<audit_id>', methods=['GET'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor'])
def audit_detail(audit_id):
    audit = get_audit_by_id(audit_id)
    report = generate_final_report(audit_id)
    return render_template('audit_detail.html', audit=audit, report=report)


@audit_views.route('/start-audit', methods=['GET'])
@jwt_required()
def start_audit():
    active_audit = get_active_audit()
    if active_audit is not None:
        return redirect(url_for('audit_views.audit_detail', audit_id=active_audit.audit_id))
    
    audit = create_audit(current_user.user_id)
    return redirect(url_for('audit_views.audit_detail', audit_id=audit.audit_id))


@audit_views.route('/end-audit', methods=['GET'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor'])
def end_audit_view():
    audit = end_audit()
    if not audit:
        flash('No active audit to end, or unresolved relocation still exists', 'error')
    else:
        flash('Audit completed successfully!', 'success')
    return redirect(url_for('audit_views.audit_list'))


@audit_views.route('/compare-audits/<audit_id>/<audit_id2>', methods=['POST'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor'])
def compare_audits(audit_id, audit_id2):
    if not get_audit_by_id(audit_id) or not get_audit_by_id(audit_id2):
        return jsonify({'message': 'Audit not found'}), 404
    audit1 = get_audit_by_id(audit_id)
    audit2 = get_audit_by_id(audit_id2)
    return render_template('compare_audits.html', audits=[audit1, audit2]), 200


@audit_views.route('/audit')
@jwt_required()
def audit_page():
    buildings = get_all_buildings_json()
    return render_template('audit.html', buildings=buildings), 200


@audit_views.route('/get-audit-status')
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor'])
def get_audit_status_view():
    try:
        return jsonify({'status': get_audit_status()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@audit_views.route('/api/check-event', methods=['POST'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor'])
def create_check_event_api():
    try:
        data = request.json

        if not data:
            return jsonify({
                'success': False,
                'message': 'No request data provided'
            }), 400

        required_fields = ['asset_id', 'found_room_id', 'condition']
        missing_fields = [field for field in required_fields if field not in data or data[field] in [None, '']]

        if missing_fields:
            return jsonify({
                'success': False,
                'message': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        asset_id = data['asset_id']
        found_room_id = data['found_room_id']
        condition = data['condition']
        user_id = current_user.user_id

        audit_id = data.get('audit_id')
        if not audit_id:
            active_audit = get_active_audit()
            if not active_audit:
                return jsonify({
                    'success': False,
                    'message': 'No active audit found'
                }), 400
            audit_id = active_audit.audit_id

        current_assignment = get_current_asset_assignment(asset_id)
        if not current_assignment:
            return jsonify({
                'success': False,
                'message': 'No active assignment found for this asset'
            }), 404

        status = 'found'
        if int(current_assignment.room_id) != int(found_room_id):
            status = 'pending relocation'

        check_event = create_check_event(
            audit_id=audit_id,
            asset_id=asset_id,
            user_id=user_id,
            found_room_id=found_room_id,
            condition=condition,
            status=status
        )

        if not check_event:
            return jsonify({
                'success': False,
                'message': 'Failed to create check event'
            }), 500

        relocation = None
        if status == 'pending relocation':
            relocation = create_relocation(check_event.check_id, found_room_id)

        return jsonify({
            'success': True,
            'message': 'Check event created successfully',
            'check_event': check_event.get_json(),
            'location_discrepancy': status == 'pending relocation',
            'relocation': relocation.get_json() if relocation else None
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating check event: {str(e)}'
        }), 500


@audit_views.route('/api/mark-assets-missing', methods=['POST'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor'])
def mark_missing():
    """
    Mark a batch of asset IDs as missing for the active/current audit.
    Expects JSON:
    {
        "assetIds": ["A-000001", "A-000002"],
        "audit_id": "optional"
    }
    """
    try:
        data = request.json

        if not data or 'assetIds' not in data:
            return jsonify({
                'success': False,
                'message': 'Invalid request data: missing assetIds field'
            }), 400

        asset_ids = data['assetIds']
        if not isinstance(asset_ids, list):
            return jsonify({
                'success': False,
                'message': 'assetIds must be a list'
            }), 400

        audit_id = data.get('audit_id')
        if not audit_id:
            active_audit = get_active_audit()
            if not active_audit:
                return jsonify({
                    'success': False,
                    'message': 'No active audit found'
                }), 400
            audit_id = active_audit.audit_id

        processed_count = 0
        error_count = 0
        errors = []

        for asset_id in asset_ids:
            assignment = get_current_asset_assignment(asset_id)
            if not assignment:
                error_count += 1
                errors.append(f'No active assignment found for asset {asset_id}')
                continue

            missing = mark_asset_missing(audit_id, assignment.assignment_id)
            if missing:
                processed_count += 1
            else:
                error_count += 1
                errors.append(f'Failed to mark asset {asset_id} as missing')

        if processed_count == 0:
            return jsonify({
                'success': False,
                'message': f'Failed to mark assets as missing: {errors[0] if errors else "Unknown error"}',
                'errors': errors[:10],
                'processed_count': 0,
                'error_count': error_count
            }), 500

        return jsonify({
            'success': True,
            'message': f'{processed_count} assets marked as missing',
            'processed_count': processed_count,
            'error_count': error_count,
            'errors': errors[:10]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error marking assets as missing: {str(e)}'
        }), 500


@audit_views.route('/api/start-audit', methods=['POST'])
@jwt_required()
def start_audit_api():
    audit = create_audit(current_user.user_id)
    return jsonify(audit.get_json()), 200


@audit_views.route('/api/assets/<room_id>', methods=['GET'])
@jwt_required()
def get_room_assets(room_id):
    try:
        room_assets = get_asset_list_from_assignments_for_room_json(room_id)
        return jsonify(room_assets if room_assets else [])
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@audit_views.route('/api/audit-list', methods=['GET'])
@jwt_required()
def get_all_audits_api():
    audits = get_all_audits_json()
    return jsonify(audits), 200


@audit_views.route('/api/audit-list/<audit_id>', methods=['GET'])
@jwt_required()
def get_audit_by_id_api(audit_id):
    audit = generate_final_report(audit_id)
    return jsonify(audit), 200


@audit_views.route('/api/generate-iterim-report/<audit_id>', methods=['GET'])
@jwt_required()
def generate_iterim_report_api(audit_id):
    audit = generate_interim_report(audit_id)
    return jsonify(audit), 200


@audit_views.route('/api/compare-audits/<audit_id>/<audit_id2>', methods=['GET'])
@jwt_required()
def compare_audits_api(audit_id, audit_id2):
    if not get_audit_by_id(audit_id) or not get_audit_by_id(audit_id2):
        return jsonify({'message': 'Audit not found'}), 404
    try:
        audit1 = generate_final_report(audit_id)
        audit2 = generate_final_report(audit_id2)
        return jsonify([audit1, audit2]), 200
    except Exception:
        return jsonify({'error': 'Could not compare Audits'}), 500