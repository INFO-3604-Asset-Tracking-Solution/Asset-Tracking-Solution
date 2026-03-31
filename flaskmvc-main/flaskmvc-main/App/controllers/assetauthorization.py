from App.models import AssetAuthorization, Asset, AssetStatus, db
from App.controllers.asset import add_asset
from datetime import datetime

def propose_asset(description, proposing_user_id, brand=None, model=None, serial_number=None, cost=None, notes=None, status_id=None):
    """
    Creates an asset authorization request. The asset is NOT added to the Asset table yet.
    """
    new_proposal = AssetAuthorization(
        description=description,
        proposing_user_id=proposing_user_id,
        brand=brand,
        model=model,
        serial_number=serial_number,
        cost=cost,
        notes=notes
    )
    
    try:
        db.session.add(new_proposal)
        db.session.commit()
        return new_proposal
    except Exception as e:
        db.session.rollback()
        print(f"Error proposing asset: {e}")
        return None

def approve_asset(authorization_id, authorized_by_user_id):
    """
    Approves an asset proposal and formally adds it to the Asset table.
    """
    proposal = AssetAuthorization.query.get(authorization_id)
    if not proposal or proposal.authorization_status != 'Pending':
        return None
    
    # Default to 'Available'
    status_name = "Available"

    # Formally add the asset to the database
    new_asset = add_asset(
        description=proposal.description,
        brand=proposal.brand,
        model=proposal.model,
        serial_number=proposal.serial_number,
        cost=proposal.cost,
        notes=proposal.notes,
        status_name=status_name
    )

    if new_asset:
        proposal.authorization_status = 'Approved'
        proposal.authorized_by = authorized_by_user_id
        proposal.authorization_date = datetime.utcnow()
        db.session.commit()
        return new_asset
    
    return None

def reject_asset(authorization_id, authorized_by_user_id):
    """
    Rejects an asset proposal.
    """
    proposal = AssetAuthorization.query.get(authorization_id)
    if not proposal or proposal.authorization_status != 'Pending':
        return None
    
    proposal.authorization_status = 'Rejected'
    proposal.authorized_by = authorized_by_user_id
    proposal.authorization_date = datetime.utcnow()
    
    try:
        db.session.commit()
        return proposal
    except Exception as e:
        db.session.rollback()
        print(f"Error rejecting asset: {e}")
        return None

def get_pending_authorizations():
    return AssetAuthorization.query.filter_by(authorization_status='Pending').all()

def get_all_authorizations():
    return AssetAuthorization.query.all()

def update_proposal(authorization_id, **kwargs):
    """
    Updates a pending asset proposal with new information.
    """
    proposal = AssetAuthorization.query.get(authorization_id)
    if not proposal or proposal.authorization_status != 'Pending':
        return None
    
    # Update only allowed fields
    allowed_fields = ['description', 'brand', 'model', 'serial_number', 'cost', 'notes', 'status_id']
    for key, value in kwargs.items():
        if key in allowed_fields:
            setattr(proposal, key, value)
            
    try:
        db.session.commit()
        return proposal
    except Exception as e:
        db.session.rollback()
        print(f"Error updating proposal: {e}")
        return None

def delete_proposal(authorization_id):
    """
    Deletes an asset proposal. It is generally safer to allow deletion of 
    Pending or Rejected proposals, while keeping Approved ones for audit trails.
    """
    proposal = AssetAuthorization.query.get(authorization_id)
    if not proposal:
        return False
    
    if proposal.authorization_status == 'Approved':
        return False # Protect approved audit history
    
    try:
        db.session.delete(proposal)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting proposal: {e}")
        return False
