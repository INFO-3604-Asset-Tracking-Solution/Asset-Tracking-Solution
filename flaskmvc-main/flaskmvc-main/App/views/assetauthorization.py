from flask import Blueprint, render_template, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from App.controllers.assetauthorization import (
    propose_asset, 
    approve_asset, 
    reject_asset, 
    get_pending_authorizations,
    get_all_authorizations,
    update_proposal,
    delete_proposal
)

asset_auth_views = Blueprint('asset_auth_views', __name__, template_folder='../templates')

@asset_auth_views.route('/authorizations', methods=['GET'])
@jwt_required()
def authorizations_page():
    return render_template('authorizations.html')

@asset_auth_views.route('/api/authorizations', methods=['GET'])
@jwt_required()
def get_authorizations():
    auths = get_all_authorizations()
    return jsonify([a.get_json() for a in auths]), 200

@asset_auth_views.route('/api/authorizations/pending', methods=['GET'])
@jwt_required()
def get_pending_auths():
    auths = get_pending_authorizations()
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
    data = request.json
    asset_tag = data.get('asset_tag')
    if not asset_tag:
        return jsonify({'message': 'Asset tag is required for approval'}), 400
    
    new_asset = approve_asset(auth_id, current_user.user_id, asset_tag)
    if new_asset:
        return jsonify({'message': 'Asset approved and created', 'asset': new_asset.get_json()}), 200
    return jsonify({'message': 'Approval failed. Check if proposal is pending or asset tag is unique.'}), 400

@asset_auth_views.route('/api/authorizations/<int:auth_id>/reject', methods=['POST'])
@jwt_required()
def reject_proposal(auth_id):
    proposal = reject_asset(auth_id, current_user.user_id)
    if proposal:
        return jsonify({'message': 'Proposal rejected', 'proposal': proposal.get_json()}), 200
    return jsonify({'message': 'Rejection failed'}), 400
