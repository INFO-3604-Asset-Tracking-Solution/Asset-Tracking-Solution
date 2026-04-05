/**
 * Asset Inventory Management
 * Handles loading, filtering, sorting, and managing inventory assets
 */

/* FILTER STATE MANAGEMENT */
const filterState = {
    searchTerm: '',
    statusFilters: new Set(),
    columnFilter: null,
    columnNames: ['description', 'Asset Tag', 'brandModel', 'Serial Number', 'Cost', 'status', 'lastUpdate', 'Action'],

    applyFilters: function () {
        handleSearch();
    },

    addStatusFilter: function (status) {
        if (this.statusFilters.has(status)) {
            this.statusFilters.delete(status);
        } else {
            this.statusFilters.add(status);
        }
        this.applyFilters();
        this.updateFilterUI();
    },

    setColumnFilter: function (columnIndex) {
        this.columnFilter = this.columnFilter === columnIndex ? null : columnIndex;
        this.applyFilters();
        this.updateFilterUI();
    },

    resetFilters: function () {
        this.searchTerm = '';
        this.statusFilters.clear();
        this.columnFilter = null;

        const searchInput = document.getElementById('searchInput');
        if (searchInput) searchInput.value = '';

        this.applyFilters();
        this.updateFilterUI();
    },

    updateFilterUI: function () {
        document.querySelectorAll('.status-filter').forEach(btn => {
            const status = btn.getAttribute('data-status');
            btn.classList.toggle('active', this.statusFilters.has(status));
        });

        document.querySelectorAll('.column-filter').forEach(btn => {
            const column = parseInt(btn.getAttribute('data-column'));
            btn.classList.toggle('active', this.columnFilter === column);
        });

        this.updateFilterTags();
    },

    updateFilterTags: function () {
        const container = document.getElementById('activeFilters');
        if (!container) return;

        container.innerHTML = '';

        this.statusFilters.forEach(status => {
            const tag = document.createElement('div');
            tag.className = 'active-filter-tag';
            tag.innerHTML = `
                <span>Status: ${status}</span>
                <span class="remove-filter" data-filter-type="status" data-filter-value="${status}">×</span>
            `;
            container.appendChild(tag);
        });

        if (this.columnFilter !== null) {
            const names = ['Description', 'Asset Tag', 'Brand/Model', 'Location', 'Status', 'Assignee', 'Last Update'];

            const tag = document.createElement('div');
            tag.className = 'active-filter-tag';
            tag.innerHTML = `
                <span>Column: ${names[this.columnFilter]}</span>
                <span class="remove-filter" data-filter-type="column">×</span>
            `;
            container.appendChild(tag);
        }

        if (this.searchTerm) {
            const tag = document.createElement('div');
            tag.className = 'active-filter-tag';
            tag.innerHTML = `
                <span>Search: "${this.searchTerm}"</span>
                <span class="remove-filter" data-filter-type="search">×</span>
            `;
            container.appendChild(tag);
        }

        const filtersContainer = document.getElementById('filtersContainer');
        if (filtersContainer) {
            const hasFilters =
                this.statusFilters.size > 0 ||
                this.columnFilter !== null ||
                this.searchTerm;

            filtersContainer.classList.toggle('d-none', !hasFilters);
        }
    }
};


function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date)) return dateString;
    return date.toISOString().split('T')[0];
}

function showMessage(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    if (!container) return;

    const el = document.createElement('div');
    el.className = `alert alert-${type} alert-dismissible fade show`;
    el.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.appendChild(el);

    setTimeout(() => {
        new bootstrap.Alert(el).close();
    }, 5000);
}

function showLoading(show = true) {
    const el = document.getElementById('loadingIndicator');
    if (el) el.style.display = show ? 'block' : 'none';
}

/* ------------ASSETS------------ */

async function loadAssets() {
    try {
        showLoading(true);

        const res = await fetch('/api/assets', {
            credentials: 'same-origin'
        });
        const data = await res.json();

        console.log("ASSETS:", data);

        displayAssets(data);

    } catch (err) {
        console.error(err);
        showMessage('Failed to load assets', 'danger');
    } finally {
        showLoading(false);
    }
}

async function loadRoomsForModal() {
    const select = document.getElementById('addAssetRoomSelect');
    if (!select) return;

    try {
        const res = await fetch('/api/rooms/all');
        const rooms = await res.json();

        select.innerHTML = '<option disabled selected>Select Room</option>';

        rooms.forEach(r => {
            const opt = document.createElement('option');
            opt.value = r.room_code;
            opt.textContent = r.room_name;
            select.appendChild(opt);
        });

    } catch (err) {
        console.error(err);
    }
}

async function saveNewAsset() {
    const payload = {
        description: document.getElementById('addAssetDescription')?.value,
        brand: document.getElementById('addAssetBrand')?.value,
        model: document.getElementById('addAssetModel')?.value,
        serial_number: document.getElementById('addAssetSerialNumber')?.value,
        status_name: "Available",        
        cost: document.getElementById('addAssetCost')?.value,
        notes: document.getElementById('addAssetNotes')?.value
    };  

    if (!payload.description) {
        showMessage("Please fill required fields", "warning");
        return;
    }

    try {
        const res = await fetch('/api/asset/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload),
            credentials: 'same-origin'

        });

        const data = await res.json();

        if (res.ok && data.success) {
            showMessage('Asset created successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addAssetModal')).hide();
            loadAssets();
        } else {
            showMessage(data.message || 'Failed to create asset', 'danger');
        }

    } catch (err) {
        console.error(err);
        showMessage("Server error", "danger");
    }
}

function displayAssets(assets) {
    const body = document.getElementById('assetTableBody');
    if (!body) return;

    body.innerHTML = '';

    assets.forEach(a => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${a.description ?? ''}</td>
            <td>${a.asset_id ?? ''}</td>
            <td>${(a.brand ?? '') + ' ' + (a.model ?? '')}</td>
            <td>${a.serial_number ?? ''}</td>
            <td>${a.cost ?? ''}</td>
            <td>${a.status_name ?? a.status ?? ''}</td>
            <td>${formatDate(a.last_update)}</td>
            <td>
                <div class="dropdown">
                    <button class="btn btn-sm btn-light dropdown-toggle"
                            data-bs-toggle="dropdown">
                        <i class="bi bi-chevron-down"></i>
                    </button>

                    <ul class="dropdown-menu dropdown-menu-end">
                        <li>
                            <a class="dropdown-item text-primary"
                               href="/asset/${a.asset_id}">
                                Edit Asset
                            </a>
                        </li>

                        <li>
                            <button class="dropdown-item text-danger"
                                onclick="deleteAsset('${a.asset_id}')">
                                Delete Asset
                            </button>
                        </li>
                    </ul>
                </div>
            </td>
        `;

        body.appendChild(row);
    });
}


function handleSearch() {    
    const input = document.getElementById('searchInput');
    const term = input?.value.toLowerCase() || '';
    filterState.searchTerm = term;

    document.querySelectorAll('#assetTableBody tr').forEach(row => {        
        let matchesSearch = false;

        if (filterState.columnFilter !== null) {
            // Search ONLY selected column
            const cell = row.querySelector(`td:nth-child(${filterState.columnFilter + 1})`);
            const text = cell?.textContent.toLowerCase() || '';
            matchesSearch = text.includes(term);
        }else{
            // Search entire row
            const text = row.textContent.toLowerCase();
            matchesSearch = text.includes(term);
        }

        row.style.display = matchesSearch ? '' : 'none';
    });
}


async function updateAsset() {
    const assetId = document.getElementById("assetId").value;

    const payload = {
        description: document.getElementById("description").value,
        brand: document.getElementById("brand").value,
        model: document.getElementById("model").value,
        serial_number: document.getElementById("serial_number").value,
        notes: document.getElementById("notes").value
    };

    const res = await fetch(`/api/asset/${assetId}/update`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (data.success) {
        alert("Asset updated successfully");
        window.location.href = "/inventory";
    } else {
        alert(data.message || "Update failed");
    }
}

async function deleteAsset(assetId) {
    if (!confirm('Are you sure you want to delete this asset? This cannot be undone.')) return;

    fetch(`/api/asset/${assetId}/delete`, {
        method: 'POST',
        credentials: 'same-origin'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('Asset deleted');
            loadAssets();
        } else {
            alert(data.message || 'Failed to delete');
        }
    })

    .catch (err => {
        console.error(err);
        alert('Server error');
    });
}


/* ------------ASSETS ASSIGNMENTS------------ */

function openAssignmentModal() {
    const modal = new bootstrap.Modal(document.getElementById('assignmentModal'));
    modal.show();
}

async function submitAssignment() {
    const payload = {
        asset_id: document.getElementById('assignAssetId').value,
        employee_id: document.getElementById('assignEmployeeId').value,
        room_id: document.getElementById('assignRoomId').value,
        condition: document.getElementById('assignCondition').value,
        assign_date: document.getElementById('assignDate').value,
    };

    console.log("Sending assignment:", payload);

    try {
        const res = await fetch('/api/assignments', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload),
            credentials: 'same-origin'
        });

        const data = await res.json();
        /*console.log("Response:", data);*/

        if (res.ok && data.success) {
            showMessage('Assignment created', 'success');
            bootstrap.Modal.getInstance(document.getElementById('assignmentModal')).hide();
            loadAssets();
        } else {
            showMessage(data.message || 'Failed assignment', 'danger');
        }

    } catch (err) {
        console.error(err);
        showMessage("Server error", "danger");
    }
}


async function updateAssignment() {
    const assignmentId = document.getElementById('assignmentId').value;

    // Auditor is only allowed to update return_date
    const payload = {
        return_date: document.getElementById('returnDate').value || null
    };

    try {
        const res = await fetch(`/api/assignments/${assignmentId}/update`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok && data.success) {
            alert("Assignment updated successfully");
            history.back();
        } else {
            alert(data.message || "Update failed");
        }

    } catch (err) {
        console.error(err);
        alert("Server error");
    }
}

async function loadAssignments() {
    try {
        const res = await fetch('/api/assignments', {
            credentials: 'same-origin'
        });
        const assignments = await res.json();

        const body = document.getElementById('assignmentsTableBody');
        body.innerHTML = '';

        if (assignments.length === 0) {
            body.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No assignments found</td></tr>';
            return;
        }

        assignments.forEach(a => {
            const status = a.return_date ? 'Completed' : 'Active';

            let badgeClass = 'bg-secondary';

            if(status == 'Active') badgeClass = 'bg-success';
            else if (status === 'Completed') badgeClass = 'bg-primary';
           /* else badgeClass = 'bg-secondary'; */

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${a.assignment_id ?? ''}</td>
                <td>${a.asset_id ?? ''}</td>
                <td>${a.employee_id ?? ''}</td>
                <td>${a.room_id ?? ''}</td>
                <td>${a.condition ?? ''}</td>
                <td>${formatDate(a.assignment_date)}</td>
                <td>${a.return_date ? formatDate(a.return_date) : 'N/A'}</td>
                <td>
                    <span class="badge ${badgeClass}">
                        ${status}
                    </span>
                </td>
                <td>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-light dropdown-toggle" data-bs-toggle="dropdown">
                            Actions
                        </button>

                        <ul class="dropdown-menu">

                            <li>
                                <a class="dropdown-item"
                                    href="/assignment/${a.assignment_id}">
                                        Edit Assignment
                                </a>
                            </li>

                            <li>
                                <button class="dropdown-item text-danger"
                                    onclick="deleteAssignment('${a.assignment_id}')">
                                    Delete 
                                </button>
                            </li>

                        </ul>
                    </div>
                </td>                
            `;
            body.appendChild(row);
        });

    } catch (err) {
        console.error(err);
        alert('Failed to load assignments');
    }
}

async function viewAssignments() {
    try {
        const res = await fetch('/api/assignments', {
            credentials: 'same-origin'
        });
        const assignments = await res.json();

        const body = document.getElementById('assignmentsTableBody');
        body.innerHTML = '';

        if (assignments.length === 0) {
            body.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No assignments found</td></tr>';
        } else {
            assignments.forEach(a => {
                const status = a.return_date ? 'Completed' : 'Active';

                let badgeClass = 'bg-secondary';
                if(status == 'Active') badgeClass = 'bg-success';
                else if (status === 'Completed') badgeClass = 'bg-primary';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${a.assignment_id ?? ''}</td>
                    <td>${a.asset_id ?? ''}</td>
                    <td>${a.employee_id ?? ''}</td>
                    <td>${a.room_id ?? ''}</td>
                    <td>${a.condition ?? ''}</td>
                    <td>${formatDate(a.assignment_date)}</td>
                    <td>${a.return_date ? formatDate(a.return_date) : 'N/A'}</td>
                    <td>
                        <span class="badge ${badgeClass}">
                            ${status}
                        </span>
                    </td>

                    <td>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-light dropdown-toggle"
                                    data-bs-toggle="dropdown">
                                <i class="bi bi-chevron-down"></i>
                            </button>

                            <ul class="dropdown-menu">
                                <li>
                                    <a class="dropdown-item"
                                        href="/assignment/${a.assignment_id}">
                                        Edit Assignment
                                    </a>
                                </li>
                        
                                <li>
                                    <button class="dropdown-item text-danger"
                                        onclick="deleteAssignment('${a.assignment_id}')">
                                        Delete Assignment
                                    </button>
                                </li>
                            </ul>
                        </div>
                    </td>
                `;
                body.appendChild(row);
            });
        }

        const searchInput = document.getElementById('assignmentSearchInput');
        const filterSelect = document.getElementById('assignmentFilterColumn');

        if (searchInput) {
            searchInput.addEventListener('input', handleAssignmentSearch);
        }

        if (filterSelect) {
            filterSelect.addEventListener('change', handleAssignmentSearch);
        }

        const modal = new bootstrap.Modal(document.getElementById('viewAssignmentsModal'));
        modal.show();

    } catch (err) {
        console.error(err);
        showMessage('Failed to Load Assignments', 'danger');
    }
}

async function updateAssignmentStatus(assignmentId, status) {
    try {
        const res = await fetch(`/api/assignments/${assignmentId}/update`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ status }),
            credentials: 'same-origin'
        });

        const data = await res.json();

        if (data.success) {
            showMessage("Status updated", "success");
            loadAssignments();
        } else {
            showMessage(data.message || "Failed to update status", "danger");
        }

    } catch (err) {
        console.error(err);
        showMessage("Server error", "danger");
    }
}

async function cancelAssignment(assignmentId) {
    if (!confirm('Are you sure you want to end this assignment?')) return;

    try {
        const res = await fetch(`/api/assignments/${assignmentId}/end`, {
            method: 'POST',
            credentials: 'same-origin'
        });
        const data = await res.json();

        if (res.ok && data.success) {
            loadAssignments();
        } else {
            alert(data.message || 'Failed to End Assignment');
        }

    } catch (err) {
        console.error(err);
        alert('Server error');
    }
}

async function deleteAssignment(assignmentId) {
    if (!confirm('Are you sure you want to delete this assignment? This cannot be undone.')) return;

    try {
        const res = await fetch(`/api/assignments/${assignmentId}/delete`, {
            method: 'POST',
            credentials: 'same-origin'
        });

        const data = await res.json();

        if (res.ok && data.success) {
            showMessage('Assignment Deleted', 'success');
            loadAssignments();
        } else {
            showMessage(data.message || 'Failed to Delete', 'danger');
        }

    } catch (err) {
        console.error(err);
        showMessage('Server error', 'danger');
    }
}

function handleAssignmentSearch() {
    const input = document.getElementById('assignmentSearchInput');
    const filterColumn = document.getElementById('assignmentFilterColumn').value;

    const term = input?.value.toLowerCase() || '';

    document.querySelectorAll('#assignmentsTableBody tr').forEach(row => {
        let matches = false;

        if (filterColumn !== '') {
            const cell = row.querySelector(`td:nth-child(${parseInt(filterColumn) + 1})`);
            const text = cell?.textContent.toLowerCase() || '';
            matches = text.includes(term);
        } else {
            const text = row.textContent.toLowerCase();
            matches = text.includes(term);
        }

        row.style.display = matches ? '' : 'none';
    });
}

    /*HAMBUGER MENU*/

document.addEventListener('DOMContentLoaded', () => {
    setupEvents();
    loadAssets();

    const menuBtn = document.getElementById('menuBtn');
    const menu = document.getElementById('menu');

    if (!menuBtn || !menu) {
        console.error("Menu not found");
        return;
    }

    menuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('d-none');
    });

    menu.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    document.addEventListener('click', () => {
        menu.classList.add('d-none');
    });
});


function setupEvents() {
    document.querySelectorAll('.status-filter').forEach(btn => {
        btn.addEventListener('click', () =>
            filterState.addStatusFilter(btn.dataset.status)
        );
    });
    document.querySelectorAll('.column-filter').forEach(btn => {
        btn.addEventListener('click', () =>
            filterState.setColumnFilter(parseInt(btn.dataset.column))
        );
    });

    const search = document.getElementById('searchInput');
    if (search) search.addEventListener('input', handleSearch);
}