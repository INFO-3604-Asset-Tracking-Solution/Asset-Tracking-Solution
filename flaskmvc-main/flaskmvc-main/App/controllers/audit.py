from App.models import Audit, CheckEvent, MissingDevice, AssetAssignment, Asset, Room
from App.database import db
from datetime import datetime

def create_audit(initiator_id):

    # Check if there is already an active audit
    active_audit = Audit.query.filter(Audit.status.in_([ 'IN_PROGRESS', 'PENDING'])).first()
    if active_audit:
        return active_audit
        
    audit = Audit(
        initiator_id = initiator_id,
        start_date = datetime.utcnow(),
        end_date = None,
        status = "IN_PROGRESS"

    )
    db.session.add(audit)
    db.session.commit()

    return audit

def end_audit():
    
    # Get the currently active audit
    audit = Audit.query.filter(Audit.status.in_(['IN_PROGRESS', 'PENDING'])).first()

    if not audit:
        return None

    # Check for pending relocations
    pending_checks = CheckEvent.query.filter_by(audit_id=audit.audit_id, status='pending relocation').first()
    if pending_checks:
        return None # Can't close if pending relocation exists

    # Audit cannot finish without relocation table having all assets be relocated 
    
    audit.end_date = datetime.utcnow()
    audit.status = "COMPLETED"

    db.session.commit()

    return audit

def get_all_audits():
    return Audit.query.order_by(Audit.start_date.desc()).all()

def get_all_audits_json():
    audits = get_all_audits()
    if not audits:
        return[]
    audits = [audit.get_json() for audit in audits]
    return audits

def get_audit_by_id(audit_id):
    return Audit.query.filter_by(audit_id=audit_id).first()

def get_audit_by_initiator_id(initiator_id):
    return Audit.query.filter_by(initiator_id=initiator_id).all()

def get_audit_by_status(status):
    return Audit.query.filter_by(status=status).all()

def get_audit_by_date_range(start_date, end_date):
    return Audit.query.filter(Audit.start_date >= start_date, Audit.end_date <= end_date).all()

def get_audit_by_date(date):
    return Audit.query.filter(Audit.start_date <= date, Audit.end_date >= date).first()

def get_active_audit():
    return Audit.query.filter(Audit.status.in_(['IN_PROGRESS', 'PENDING'])).first()

def get_audit_status():
    audit = get_active_audit()
    if not audit:
        return 'NO_ACTIVE_AUDIT'
    return audit.get_json()['status']

def generate_audit_report(audit_id, end_date=None):
    audit = get_audit_by_id(audit_id)
    if not audit:
        return None
        
    # Get all check events for this audit up to the end_date if provided
    check_query = CheckEvent.query.filter_by(audit_id=audit_id)
    missing_query = MissingDevice.query.filter_by(audit_id=audit_id)

    if end_date:
        import datetime
        end_of_day = datetime.datetime.combine(end_date, datetime.time.max)
        check_query = check_query.filter(CheckEvent.timestamp <= end_of_day)
        missing_query = missing_query.filter(MissingDevice.timestamp <= end_of_day)

    check_events = check_query.all()
    missing_records = missing_query.all()
    
    # We define global scope as all currently active assignments. 
    # (If the audit is old, active assignments might have changed, but we assume
    # we want the assignments active at the time of the query or at the start. 
    # For simplicity, we just use the current active ones + anything already linked to the audit.)
    
    active_assignments = AssetAssignment.query.filter_by(return_date=None).all()
    
    report = {
        'audit_info': audit.get_json(),
        'expected_total': len(active_assignments),
        'found_correct': [],
        'relocated': [],
        'condition_discrepancy': [],
        'missing': [],
        'unscanned': [],
        'unexpected': [],
        'room_breakdown': []
    }
    
    rooms_data = {}
    def get_room_data(r_id):
        if r_id not in rooms_data:
            room = Room.query.get(r_id)
            rooms_data[r_id] = {
                'room_id': r_id,
                'room_name': room.room_name if room else f"Room {r_id}",
                'expected_count': 0,
                'found_correct_count': 0,
                'relocated_out_count': 0,
                'missing_count': 0,
                'unexpected_here_count': 0,
                'unscanned_count': 0
            }
        return rooms_data[r_id]
    
    # Map CheckEvents by asset_id
    checks_by_asset = {ce.asset_id: ce for ce in check_events}
    
    # Track which assignments have been processed as explicitly missing
    missing_assignment_ids = [m.assignment_id for m in missing_records if not m.found_relocation_id]
    
    # 1. Process active assignments to find discrepancies
    for assignment in active_assignments:
        asset_id = assignment.asset_id
        r_data = get_room_data(assignment.room_id)
        r_data['expected_count'] += 1
        
        # Pull asset details for rich JSON
        asset = Asset.query.get(asset_id)
        asset_desc = asset.description if asset else "Unknown"
        
        if asset_id in checks_by_asset:
            # Asset was checked/scanned!
            ce = checks_by_asset[asset_id]
        
            # Add asset details to event payload early so we reuse it
            enrich_event = ce.get_json()
            enrich_event['asset_description'] = asset_desc
            enrich_event['expected_room'] = assignment.room_id
            enrich_event['expected_condition'] = assignment.condition
            
            is_correct_room = (int(ce.found_room_id) == int(assignment.room_id))
            is_correct_condition = (ce.condition == assignment.condition)
            
            if is_correct_room and is_correct_condition:
                report['found_correct'].append(enrich_event)
                
            if not is_correct_room:
                report['relocated'].append(enrich_event)
                
            if not is_correct_condition:
                report['condition_discrepancy'].append(enrich_event)
                
            # Update room statistics
            if is_correct_room:
                r_data['found_correct_count'] += 1
            else:
                r_data['relocated_out_count'] += 1
                found_r_data = get_room_data(int(ce.found_room_id))
                found_r_data['unexpected_here_count'] += 1
                
            # Remove from map so we know what's left
            del checks_by_asset[asset_id]
        
        elif assignment.assignment_id not in missing_assignment_ids:
            # It's not scanned and not explicitly marked missing yet
            r_data['unscanned_count'] += 1
            report['unscanned'].append({
                'asset_id': assignment.asset_id,
                'asset_description': asset_desc,
                'expected_room': assignment.room_id,
                'status': 'Pending Verification'
            })
        
    # 2. Process MissingDevices explicitly marked
    missing_assignment_ids = [m.assignment_id for m in missing_records if not m.found_relocation_id]
    
    for missing_record in missing_records:
        if not missing_record.found_relocation_id:
            assignment = AssetAssignment.query.get(missing_record.assignment_id)
            if assignment:
                # Update room missing stat
                r_data = get_room_data(assignment.room_id)
                r_data['missing_count'] += 1
                
                asset = Asset.query.get(assignment.asset_id)
                report['missing'].append({
                    'asset_id': assignment.asset_id,
                    'asset_description': asset.description if asset else 'Unknown',
                    'expected_room': assignment.room_id,
                    'missing_since': missing_record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
            
    # 3. Process unexpected assets (scanned, but had no active assignment)
    for asset_id, ce in checks_by_asset.items():
        # Update room unexpected stat for unassigned assets
        found_rid = int(ce.found_room_id)
        found_r_data = get_room_data(found_rid)
        found_r_data['unexpected_here_count'] += 1
        
        asset = Asset.query.get(asset_id)
        enrich_event = ce.get_json()
        enrich_event['asset_description'] = asset.description if asset else "Unknown/Unassigned"
        enrich_event['expected_room'] = 'None'
        enrich_event['expected_condition'] = 'None'
        report['unexpected'].append(enrich_event)
        
    report['room_breakdown'] = list(rooms_data.values())
    return report

def generate_interim_report(audit_id):
    audit = get_audit_by_id(audit_id)
    if not audit or audit.status == "COMPLETED":
        return None
    return generate_audit_report(audit_id)

def generate_final_report(audit_id):
    return generate_audit_report(audit_id)

def get_audit_active_dates(audit_id):
    check_dates = db.session.query(db.func.date(CheckEvent.timestamp)).filter_by(audit_id=audit_id).distinct().all()
    missing_dates = db.session.query(db.func.date(MissingDevice.timestamp)).filter_by(audit_id=audit_id).distinct().all()
    
    import datetime
    def to_date(d):
        if not d: return None
        if isinstance(d, str):
            try:
                return datetime.datetime.strptime(d.split(' ')[0], '%Y-%m-%d').date()
            except ValueError:
                return None
        if isinstance(d, datetime.datetime):
            return d.date()
        return d

    dates = set()
    for item in check_dates:
        parsed = to_date(item[0])
        if parsed: dates.add(parsed)
        
    for item in missing_dates:
        parsed = to_date(item[0])
        if parsed: dates.add(parsed)
        
    # Also add the audit start date
    audit = get_audit_by_id(audit_id)
    if audit and audit.start_date:
        parsed = to_date(audit.start_date)
        if parsed: dates.add(parsed)
        
    return sorted(list(dates))

def generate_daily_interim_reports_for_audit(audit_id):
    dates = get_audit_active_dates(audit_id)
    reports_by_date = {}
    
    for d in dates:
        date_str = d.strftime('%Y-%m-%d')
        report = generate_audit_report(audit_id, end_date=d)
        if report:
            reports_by_date[date_str] = report
            
    return {
        "dates": [d.strftime('%Y-%m-%d') for d in dates],
        "reports": reports_by_date
    }