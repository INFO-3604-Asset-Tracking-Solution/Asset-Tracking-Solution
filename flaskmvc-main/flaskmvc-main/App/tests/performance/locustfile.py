from locust import HttpUser, task, between, events, TaskSet
import random
import threading

# --- Global State for Seeding ---
SEED_LOCK = threading.Lock()
HAS_SEEDED_500 = False

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    print("--- Performance Test Initializing (With 500 Asset Seeder) ---")

def seed_database_with_500_assets(client):
    global HAS_SEEDED_500
    with SEED_LOCK:
        if HAS_SEEDED_500:
            return
        print("--- BEGINNING BULK SEED OF 500 ASSETS ---")
        
        # Auth as Manager to seed
        resp = client.post("/api/login", json={"email": "manager@gmail.com", "password": "managerpass"}, name="Setup: Login")
        if resp.status_code != 200:
            print("Failed to login for setup.")
            return
        token = resp.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # Fetch rooms
        resp = client.get("/api/rooms/all", headers=headers, name="Setup: Get Rooms")
        if resp.status_code != 200 or not resp.json():
            print("Failed to fetch rooms.")
            return
        rooms = [r['room_id'] for r in resp.json()]
        
        client.post("/api/start-audit", headers=headers, name="Setup: Start Initial Audit")
        
        for i in range(500):
            asset_sn = f"PERF-500-{random.randint(1000, 9999)}-{i}"
            
            # Seed Asset
            resp_asset = client.post("/api/asset/add", json={
                "description": f"Performance Asset {i}",
                "brand": "BulkLoad",
                "serial_number": asset_sn,
                "status_name": "Available"
            }, headers=headers, name="Setup: Seed Asset")
            
            # Assign Asset
            if resp_asset.status_code == 201:
                asset_id = resp_asset.json().get('asset', {}).get('asset_id')
                if asset_id:
                    room_id = rooms[i % len(rooms)]
                    client.post("/api/assignments", json={
                        "asset_id": asset_id,
                        "employee_id": 1,
                        "room_id": room_id,
                        "condition": "Good",
                        "assign_date": "2023-01-01"
                    }, headers=headers, name="Setup: Assign Asset")
        
        print("--- 500 ASSETS SEEDED SUCCESSFULLY ---")
        HAS_SEEDED_500 = True


class AuditorBehavior(TaskSet):
    """
    Auditor flow
    1. Pick Room -> 2. Scan many items -> 3. Mark missing -> Loop
    """
    def on_start(self):
        self.rooms = []
        self.current_room_id = None
        self.assets_in_room = []
        
        resp = self.client.post("/api/login", json={"email": "auditor@gmail.com", "password": "auditorpass"}, name="Auditor: Login")
        if resp.status_code == 200:
            self.client.headers.update({"Authorization": f"Bearer {resp.json().get('access_token')}"})

    @task(1)
    def handle_audit(self):
        # State 1: Pick a room
        if not self.current_room_id:
            if not self.rooms:
                resp = self.client.get("/api/rooms/all", name="Auditor: Get Rooms")
                if resp.status_code == 200:
                    self.rooms = [r['room_id'] for r in resp.json()]
            
            if self.rooms:
                self.current_room_id = random.choice(self.rooms)
                resp = self.client.get(f"/api/assets/{self.current_room_id}", name="Auditor: Get Room Assets")
                if resp.status_code == 200:
                    self.assets_in_room = [a['asset_id'] for a in resp.json()]
                    
                    self.items_to_scan = int(len(self.assets_in_room) * 0.8)
                else:
                    self.current_room_id = None
            return # Yield execution for this tick
        
        # State 2: Scan remaining assets
        if getattr(self, 'items_to_scan', 0) > 0 and self.assets_in_room:
            # Pick random index to pop
            idx = random.randrange(len(self.assets_in_room))
            asset_id = self.assets_in_room.pop(idx)
            
            self.client.post("/api/check-event", json={
                "asset_id": asset_id,
                "found_room_id": self.current_room_id,
                "condition": random.choice(["Good", "Needs Repair"])
            }, name="Auditor: Scan Asset")
            
            self.items_to_scan -= 1
            return # Yield execution
            
        # State 3: Room scanning is complete, mark the rest as missing (cap to prevent huge payload)
        if self.assets_in_room:
             missing_ids = self.assets_in_room[:10] # Just mark up to 10 missing
             self.client.post("/api/mark-assets-missing", json={"assetIds": missing_ids}, name="Auditor: Mark Missing")
        
        # Reset state for next room
        self.assets_in_room = []
        self.current_room_id = None
        self.items_to_scan = 0

    @task(1)
    def view_all_assets_irregular(self):
        if random.random() < 0.2:
            self.client.get("/api/assets", name="Auditor: Get All Assets")


class ManagerBehavior(TaskSet):
    """
    Manager oversees the discrepancies reported by Auditors.
    """
    def on_start(self):
        resp = self.client.post("/api/login", json={"email": "manager@gmail.com", "password": "managerpass"}, name="Manager: Login")
        if resp.status_code == 200:
            self.client.headers.update({"Authorization": f"Bearer {resp.json().get('access_token')}"})

    @task(3)
    def view_and_reconcile(self):
        resp = self.client.get("/api/discrepancies", name="Manager: View Discrepancies")
        if resp.status_code == 200:
            data = resp.json()
            relocations = [r for r in data if r.get('row_type') == 'relocation']
            if relocations:
                target = random.choice(relocations)
                self.client.post("/reconcile-discrepancy", json={
                    "asset_id": target['asset_id'],
                    "new_room_id": target['found_room_id'],
                    "new_condition": "Good"
                }, name="Manager: Reconcile")

    @task(1)
    def manage_audit_cycle(self):
        resp = self.client.get("/api/audit-list", name="Manager: Audit List")
        if resp.status_code == 200:
            audits = resp.json()
            active = [a for a in audits if a['status'] == 'in_progress']
            
            # Small chance to end current audit to keep pipeline flowing
            if active and random.random() < 0.05:
                self.client.get("/end-audit", name="Manager: End Audit")
            elif not active:
                self.client.post("/api/start-audit", name="Manager: Start Audit")

    @task(1)
    def export_report(self):
        self.client.get("/api/discrepancies/download", name="Manager: Export CSV")
        
    @task(1)
    def view_all_assets(self):
        # Irregular request to get all assets
        if random.random() < 0.3:
            self.client.get("/api/assets", name="Manager: Get All Assets")


class AssetTrackingSuite(HttpUser):
    wait_time = between(1, 4) # Fast pacing to execute the 500 asset audit efficiently
    
    def on_start(self):
        # Seed only once across all spawned users
        seed_database_with_500_assets(self.client)

    tasks = {
        AuditorBehavior: 4,  # 4 Auditors scanning 
        ManagerBehavior: 1   # 1 Manager resolving discrepancies
    }
