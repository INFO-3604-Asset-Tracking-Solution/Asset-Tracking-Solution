from flask import Blueprint, render_template, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from App.controllers.assetauthorization import (
    propose_asset, 
    approve_asset, 
    reject_asset, 
    get_pending_authorizations,
    get_all_authorizations,
    update_proposal,
    delete_proposal,
    get_authorizations_by_user
)

asset_auth_views = Blueprint('asset_auth_views', __name__, template_folder='../templates')

@asset_auth_views.route('/authorizations', methods=['GET'])
@jwt_required()
def authorizations_page():
    role = current_user.role
    
    if role in ['Administrator', 'Manager']:
        pending_auths = get_pending_authorizations()
        history_auths = get_all_authorizations()
    else:
        all_user_auths = get_authorizations_by_user(current_user.user_id)
        pending_auths = [a for a in all_user_auths if a.authorization_status == 'Pending']
        history_auths = all_user_auths
        
    return render_template(
        'authorizations.html', 
        active_page='authorizations',
        pending_auths=pending_auths,
        history_auths=history_auths
    )

@asset_auth_views.route('/api/authorizations', methods=['GET'])
@jwt_required()
def get_authorizations():
    if current_user.role in ['Administrator', 'Manager']:
        auths = get_all_authorizations()
    else:
        auths = get_authorizations_by_user(current_user.user_id)
        
    return jsonify([a.get_json() for a in auths]), 200

@asset_auth_views.route('/api/authorizations/pending', methods=['GET'])
@jwt_required()
def get_pending_auths():
    if current_user.role in ['Administrator', 'Manager']:
        auths = get_pending_authorizations()
    else:
        all_user_auths = get_authorizations_by_user(current_user.user_id)
        auths = [a for a in all_user_auths if a.authorization_status == 'Pending']

    return jsonify([a.get_json() for a in auths]), 200

@asset_auth_views.route('/api/authorizations/propose', methods=['POST'])
@jwt_required()
def propose_new_asset():
    data = request.json
    if not data or 'description' not in data:
        return jsonify({'message': 'Description is required'}), 400
    
    proposal = propose_asset(
        description=data['description'],
        proposing_user_id=current_user.user_id,
        brand=data.get('brand'),
        model=data.get('model'),
        serial_number=data.get('serial_number'),
        cost=data.get('cost'),
        notes=data.get('notes'),
        status_id=data.get('status_id')
    )
    
    if proposal:
        return jsonify(proposal.get_json()), 201
    return jsonify({'message': 'Failed to create proposal'}), 500

@asset_auth_views.route('/api/authorizations/<int:auth_id>', methods=['PUT'])
@jwt_required()
def update_proposal_api(auth_id):
    data = request.json
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    proposal = update_proposal(auth_id, **data)
    if proposal:
        return jsonify({'message': 'Proposal updated successfully', 'proposal': proposal.get_json()}), 200
    return jsonify({'message': 'Proposal update failed. Ensure it exists and is pending.'}), 400

@asset_auth_views.route('/api/authorizations/<int:auth_id>', methods=['DELETE'])
@jwt_required()
def delete_proposal_api(auth_id):
    success = delete_proposal(auth_id)
    if success:
        return jsonify({'message': 'Proposal deleted successfully'}), 200
    return jsonify({'message': 'Proposal deletion failed. Note: Approved proposals cannot be deleted.'}), 400

@asset_auth_views.route('/api/authorizations/<int:auth_id>/approve', methods=['POST'])
@jwt_required()
def approve_proposal(auth_id):
    if current_user.role not in ['Administrator', 'Manager']:
        return jsonify({'message': 'Access denied: Only Managers can approve assets'}), 403

    new_asset = approve_asset(auth_id, current_user.user_id)
    if new_asset:
        return jsonify({'message': 'Asset approved and created', 'asset': new_asset.get_json()}), 200
    return jsonify({'message': 'Approval failed. Check if proposal is pending.'}), 400

@asset_auth_views.route('/api/authorizations/<int:auth_id>/reject', methods=['POST'])
@jwt_required()
def reject_proposal(auth_id):
    if current_user.role not in ['Administrator', 'Manager']:
        return jsonify({'message': 'Access denied: Only Managers can reject assets'}), 403

    proposal = reject_asset(auth_id, current_user.user_id)
    if proposal:
        return jsonify({'message': 'Proposal rejected', 'proposal': proposal.get_json()}), 200
    return jsonify({'message': 'Rejection failed'}), 400
