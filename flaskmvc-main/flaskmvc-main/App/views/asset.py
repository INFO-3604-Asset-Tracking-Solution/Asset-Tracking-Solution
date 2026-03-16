
from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for

asset_views = Blueprint('asset_views', __name__, template_folder='../templates')

@asset_views.route('/assets', methods=['GET'])
def get_asset_page():
    return render_template('inventory.html')

@asset_views.route('/api/propose-asset', methods=['POST'])
@jwt_required()
def propose_asset_action():
    data = request.form
    flash(f"Asset proposed")
    return redirect(url_for('asset_views.get_asset_page'))

@asset_views.route('/approve-asset/<asset_id>', methods=['POST'])
@jwt_required()
def approve_asset_action(asset_id):
    data = request.form
    flash(f"Asset approved")
    return redirect(url_for('asset_views.get_asset_page'))

@asset_views.route('/reject-asset/<asset_id>', methods=['POST'])
@jwt_required()
def reject_asset_action(asset_id):
    data = request.form
    flash(f"Asset rejected")
    return redirect(url_for('asset_views.get_asset_page'))

