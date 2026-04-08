from locust import HttpUser, task, between, SequentialTaskSet
import random

class AuditorBehavior(SequentialTaskSet):
    """Simulates a full room-scan cycle for an Auditor on the ground."""
    
    def on_start(self):
        # Authenticate via API and save JWT token to bypass local Secure Cookie restrictions
        with self.client.post("/api/login", json={"email": "auditor@gmail.com", "password": "auditorpass"}, catch_response=True) as response:
            if response.status_code == 200:
                token = response.json().get('access_token')
                self.client.headers.update({"Authorization": f"Bearer {token}"})
                response.success()
            else:
                response.failure("Login failed")
        
        self.current_room_id = None
        self.room_assets = []

    @task
    def start_or_join_audit(self):
        # Simulate loading the scanning UI
        self.client.get("/audit")

    @task
    def load_random_room(self):
        # Dynamically fetch floors/rooms
        with self.client.get("/api/floors/1", catch_response=True) as response:
            if response.status_code == 200:
                # Assuming rooms 1 through 4 exist based on initialize.py
                self.current_room_id = str(random.randint(1, 4))
                
                # Fetch anticipated assets
                with self.client.get(f"/api/assets/{self.current_room_id}", catch_response=True) as room_resp:
                    if room_resp.status_code == 200:
                        self.room_assets = room_resp.json()
                        room_resp.success()

    @task
    def burst_scan(self):
        # Simulates scanning a chunk of items rapidly
        if not self.room_assets:
            return
            
        # Scan up to 5 items randomly from the expected list
        max_scan = min(5, len(self.room_assets))
        if max_scan == 0:
            return
            
        scan_count = random.randint(1, max_scan)
        assets_to_scan = random.sample(self.room_assets, scan_count)
        
        for asset in assets_to_scan:
            # 90% good, 10% issues
            condition = random.choices(["Good", "Needs Repair", "Beyond Repair"], weights=[90, 8, 2])[0]
            
            # Usually the Frontend formats JSON id key as 'id' or 'id:'
            asset_id = asset.get('id') or asset.get('id:') or asset.get('asset_id')
            
            if asset_id:
                self.client.post("/api/check-event", json={
                    "asset_id": asset_id,
                    "found_room_id": self.current_room_id,
                    "condition": condition
                })

class ManagerBehavior(SequentialTaskSet):
    """Simulates a Manager reviewing heavy global reports and inventory."""
    
    def on_start(self):
        # Authenticate as a manager
        with self.client.post("/api/login", json={"email": "manager@gmail.com", "password": "managerpass"}, catch_response=True) as response:
            if response.status_code == 200:
                token = response.json().get('access_token')
                self.client.headers.update({"Authorization": f"Bearer {token}"})
                response.success()
            else:
                response.failure("Login failed")

    @task
    def view_inventory_dashboard(self):
        # Load main page
        self.client.get("/inventory")
        
    @task
    def view_audit_history(self):
        # Load audits list
        self.client.get("/audit-list")
        
    @task
    def view_heavy_audit_report(self):
        # To test the heavy `generate_audit_report` function, we first fetch API lists
        # to find an active or recent audit dynamically.
        with self.client.get("/api/audit-list", catch_response=True) as response:
            if response.status_code == 200:
                audits = response.json()
                if audits:
                    # Pick a random audit to stress
                    audit_id = random.choice(audits).get('audit_id')
                    if audit_id:
                        # Load the Heavy HTML dashboard directly (Triggers complex Python logic)
                        self.client.get(f"/audit-list/{audit_id}")


class PerformanceSuite(HttpUser):
    # Think-time between tasks (simulates walking, reading the screen, etc)
    wait_time = between(2, 6)
    
    # User distribution. 
    # For every 5 simulated users, 4 will be Auditors scanning, 1 will be a Manager analyzing
    tasks = {AuditorBehavior: 4, ManagerBehavior: 1}