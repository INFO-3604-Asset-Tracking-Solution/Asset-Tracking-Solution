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
    const saveBtn = document.getElementById('saveAssetBtn');
    const userRole = saveBtn?.dataset.role || '';
    
    const isProposing = (userRole === 'Auditor');
    const endpoint = isProposing ? '/api/authorizations/propose' : '/api/asset/add';

    const payload = {
        description: document.getElementById('addAssetDescription')?.value,
        brand: document.getElementById('addAssetBrand')?.value,
        model: document.getElementById('addAssetModel')?.value,
        serial_number: document.getElementById('addAssetSerialNumber')?.value,
        status_name: document.getElementById('addAssetStatus')?.value,     
        cost: document.getElementById('addAssetCost')?.value,
        notes: document.getElementById('addAssetNotes')?.value
    };  

    if (!payload.description) {
        showMessage("Please fill required fields", "warning");
        return;
    }

    if (payload.cost && parseFloat(payload.cost) < 0) {
        showMessage("Cost cannot be negative", "warning");
        return;
    }

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload),
            credentials: 'same-origin'
        });

        const data = await res.json();

        if (res.ok && (data.success || isProposing)) {
            const successMsg = isProposing ? 'Asset proposal submitted for approval' : 'Asset created successfully';
            showMessage(successMsg, 'success');
            
            const modalEl = document.getElementById('addAssetModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();
            
            // Note: field clearing happens automatically via the 'hidden.bs.modal' listener
            
            if (!isProposing) {
                loadAssets();
            }
        } else {
            showMessage(data.message || 'Action failed', 'danger');
        }

    } catch (err) {
        console.error(err);
        showMessage("Server error", "danger");
    }
}

function clearAddAssetModal() {
    const fields = [
        'addAssetDescription', 
        'addAssetBrand', 
        'addAssetModel', 
        'addAssetSerialNumber', 
        'addAssetCost', 
        'addAssetNotes'
    ];
    
    fields.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    
    const statusSelect = document.getElementById('addAssetStatus');
    if (statusSelect) statusSelect.selectedIndex = 0;
}

/* Track which assets are selected for bulk QR export */
let selectedAssets = new Map(); // assetId -> asset data object

function displayAssets(assets) {
    const body = document.getElementById('assetTableBody');
    if (!body) return;

    body.innerHTML = '';

    assets.forEach(a => {
        const row = document.createElement('tr');
        // Store full asset data on the row for easy retrieval
        row.dataset.asset = JSON.stringify(a);

        row.innerHTML = `
            <td>
                <input type="checkbox"
                       class="form-check-input asset-select-checkbox"
                       data-asset-id="${a.asset_id ?? ''}"
                       ${selectedAssets.has(a.asset_id) ? 'checked' : ''}>
            </td>
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

        // Checkbox change handler
        const checkbox = row.querySelector('.asset-select-checkbox');
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                selectedAssets.set(a.asset_id, a);
            } else {
                selectedAssets.delete(a.asset_id);
                // Uncheck the select-all box if any box is deselected
                const selectAll = document.getElementById('selectAllCheckbox');
                if (selectAll) selectAll.checked = false;
            }
            updateSelectionBar();
        });

        body.appendChild(row);
    });

    // Wire up Select All checkbox
    const selectAll = document.getElementById('selectAllCheckbox');
    if (selectAll) {
        selectAll.checked = false;
        selectAll.onchange = function() {
            if (this.checked) {
                selectAllAssets(assets);
            } else {
                deselectAll();
            }
        };
    }

    updateSelectionBar();
}

/** Shows/hides the toolbar above the table based on current selection */
function updateSelectionBar() {
    const toolbar = document.getElementById('qrExportToolbar');
    const countEl = document.getElementById('selectedCount');
    if (!toolbar) return;

    const count = selectedAssets.size;
    if (countEl) countEl.textContent = count;

    if (count > 0) {
        toolbar.classList.remove('d-none');
    } else {
        toolbar.classList.add('d-none');
    }
}

function selectAllAssets(assets) {
    assets.forEach(a => selectedAssets.set(a.asset_id, a));
    // Tick every visible checkbox
    document.querySelectorAll('.asset-select-checkbox').forEach(cb => {
        cb.checked = true;
    });
    updateSelectionBar();
}

function deselectAll() {
    selectedAssets.clear();
    document.querySelectorAll('.asset-select-checkbox').forEach(cb => cb.checked = false);
    const selectAll = document.getElementById('selectAllCheckbox');
    if (selectAll) selectAll.checked = false;
    updateSelectionBar();
}

/** Build the QR data string for one asset */
function buildQRData(a) {
    return [
        a.asset_id ?? '',
        a.description ?? '',
        a.brand ?? '',
        a.model ?? '',
        a.serial_number ?? ''
    ].join('|');
}

/** Generate a QR code canvas for a given data string */
function generateQRCanvas(data, size = 150) {
    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        QRCode.toCanvas(canvas, data, { width: size, margin: 1 }, (err) => {
            if (err) reject(err);
            else resolve(canvas);
        });
    });
}

/** Opens the QR export preview modal */
async function openQRExportModal(format) {
    if (selectedAssets.size === 0) {
        showMessage('Please select at least one asset.', 'warning');
        return;
    }

    const grid = document.getElementById('qrExportGrid');
    const confirmBtn = document.getElementById('confirmExportBtn');
    if (!grid || !confirmBtn) return;

    grid.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div><p class="mt-2 text-muted">Generating QR codes…</p></div>';

    const modal = new bootstrap.Modal(document.getElementById('qrExportModal'));
    modal.show();

    grid.innerHTML = '';

    for (const [id, a] of selectedAssets) {
        const qrData = buildQRData(a);
        const canvas = await generateQRCanvas(qrData, 140);

        const card = document.createElement('div');
        card.className = 'qr-export-card';
        card.innerHTML = `
            <div class="qr-card-img"></div>
            <div class="qr-card-info">
                <div class="qr-card-title">${a.description ?? 'N/A'}</div>
                <div class="qr-card-sub">${a.asset_id ?? ''}</div>
                <div class="qr-card-room"><i class="bi bi-geo-alt"></i> ${a.room_name ?? 'N/A'}</div>
            </div>
        `;
        card.querySelector('.qr-card-img').appendChild(canvas);
        grid.appendChild(card);
    }

    // Wire up Download button
    confirmBtn.onclick = () => {
        modal.hide();
        if (format === 'pdf') {
            exportSelectedPDF();
        } else {
            exportSelectedPNG();
        }
    };
    confirmBtn.innerHTML = `<i class="bi bi-download me-1"></i>Download as ${format.toUpperCase()}`;
}

/** Export all selected QR codes merged into one tall PNG */
async function exportSelectedPNG() {
    const assets = [...selectedAssets.values()];
    const QR_SIZE = 200;
    const PADDING = 16;
    const LABEL_H = 40;
    const COLS = Math.min(4, assets.length);
    const ROWS = Math.ceil(assets.length / COLS);
    const W = COLS * (QR_SIZE + PADDING) + PADDING;
    const H = ROWS * (QR_SIZE + LABEL_H + PADDING) + PADDING;

    const masterCanvas = document.createElement('canvas');
    masterCanvas.width = W;
    masterCanvas.height = H;
    const ctx = masterCanvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, W, H);

    for (let i = 0; i < assets.length; i++) {
        const a = assets[i];
        const col = i % COLS;
        const row = Math.floor(i / COLS);
        const x = PADDING + col * (QR_SIZE + PADDING);
        const y = PADDING + row * (QR_SIZE + LABEL_H + PADDING);

        const canvas = await generateQRCanvas(buildQRData(a), QR_SIZE);
        ctx.drawImage(canvas, x, y);

        // Label below the QR
        ctx.fillStyle = '#1a1a2e';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        const label = (a.description ?? a.asset_id ?? 'Asset').substring(0, 28);
        ctx.fillText(label, x + QR_SIZE / 2, y + QR_SIZE + 16);
        ctx.font = '10px sans-serif';
        ctx.fillStyle = '#6c757d';
        ctx.fillText(a.asset_id ?? '', x + QR_SIZE / 2, y + QR_SIZE + 30);
    }

    const link = document.createElement('a');
    link.href = masterCanvas.toDataURL('image/png');
    link.download = `qr_codes_export_${new Date().toISOString().split('T')[0]}.png`;
    link.click();
}

/** Export selected assets as a PDF – one QR label per asset */
async function exportSelectedPDF() {
    const { jsPDF } = window.jspdf;
    if (!jsPDF) {
        showMessage('PDF library not loaded. Please refresh the page.', 'danger');
        return;
    }

    const assets = [...selectedAssets.values()];
    const doc = new jsPDF({ unit: 'mm', format: 'a4' });
    const PAGE_W = 210;
    const MARGIN = 15;
    const QR_MM = 40;  // QR size in mm
    const ROW_H = 55;  // height of each label row (mm)
    const COLS = 4;
    const COL_W = (PAGE_W - 2 * MARGIN) / COLS;

    let col = 0;
    let y = MARGIN;

    for (let i = 0; i < assets.length; i++) {
        const a = assets[i];
        const x = MARGIN + col * COL_W;

        const canvas = await generateQRCanvas(buildQRData(a), 300);
        const imgData = canvas.toDataURL('image/png');

        // Draw QR code
        doc.addImage(imgData, 'PNG', x + (COL_W - QR_MM) / 2, y, QR_MM, QR_MM);

        // Asset description below QR
        doc.setFontSize(7);
        doc.setTextColor(30, 30, 30);
        doc.setFont(undefined, 'bold');
        const name = (a.description ?? a.asset_id ?? 'Unknown').substring(0, 24);
        doc.text(name, x + COL_W / 2, y + QR_MM + 5, { align: 'center' });

        doc.setFont(undefined, 'normal');
        doc.setFontSize(6);
        doc.setTextColor(100, 100, 100);
        doc.text(`ID: ${a.asset_id ?? 'N/A'}`, x + COL_W / 2, y + QR_MM + 10, { align: 'center' });
        doc.text(`Room: ${a.room_name ?? 'N/A'}`, x + COL_W / 2, y + QR_MM + 15, { align: 'center' });

        col++;
        if (col >= COLS) {
            col = 0;
            y += ROW_H;
        }
        if (y + ROW_H > 297 - MARGIN && i < assets.length - 1) {
            doc.addPage();
            y = MARGIN;
            col = 0;
        }
    }

    doc.save(`qr_codes_export_${new Date().toISOString().split('T')[0]}.pdf`);
}

function handleSearch() {
    const input = document.getElementById('searchInput');
    const term = input?.value.toLowerCase() || '';

    const filterBy = document.querySelector('input[name="filterBy"]:checked')?.value;

    document.querySelectorAll('#assetTableBody tr').forEach(row => {

        let text = '';

        switch (filterBy) {
            case 'item':
                // column 0 = checkbox, column 1 = description
                text = row.children[1]?.textContent.toLowerCase();
                break;

            case 'assetTag':
                text = row.children[2]?.textContent.toLowerCase();
                break;

            case 'brandModel':
                text = row.children[3]?.textContent.toLowerCase();
                break;

            case 'serialNumber':
                text = row.children[4]?.textContent.toLowerCase();
                break;

            default:
                text = row.textContent.toLowerCase();
        }

        row.style.display = text.includes(term) ? '' : 'none';
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
    const assetId = document.getElementById('assignAssetId').value;
    const employeeId = document.getElementById('assignEmployeeId').value;
    const roomId = document.getElementById('assignRoomId').value;

    if (!assetId || !employeeId || !roomId) {
        showMessage('Please select an Asset, Employee, and Room from the search results.', 'warning');
        return;
    }

    const payload = {
        asset_id: assetId,
        employee_id: employeeId,
        room_id: roomId,
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

        if (res.ok && data.success) {
            showMessage('Assignment created', 'success');
            bootstrap.Modal.getInstance(document.getElementById('assignmentModal')).hide();
            loadAssignments();
        } else {
            showMessage(data.message || 'Failed assignment', 'danger');
        }

    } catch (err) {
        console.error(err);
        showMessage("Server error", "danger");
    }
}

async function updateAssignment() {
    const assignmentId = document.getElementById('assignmentId').value.trim();
    const returnDateValue = document.getElementById('returnDate').value;

    const payload = {
        return_date: returnDateValue || null,
        condition: document.getElementById('condition').value
    };

    try {
        const res = await fetch(`/api/assignments/${assignmentId}/update`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok && data.success) {
            showMessage("Assignment updated successfully", "success");

            // safer than stale back navigation
            window.location.href = "/inventory";
        } else {
            showMessage(data.message || "Update failed", "danger");
        }

    } catch (err) {
        console.error(err);
        showMessage("Server error", "danger");
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
                <td>${a.asset_description ?? ''}</td>
                <td>${a.employee_name ?? a.employee_id ?? ''}</td>
                <td>${a.room_name ?? a.room_id ?? ''}</td>
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
                    <td>${a.asset_description ?? ''}</td>
                    <td>${a.employee_name ?? a.employee_id ?? ''}</td>
                    <td>${a.room_name ?? a.room_id ?? ''}</td>
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
    loadAssets()

    let lastChecked = "item";
    document.getElementById('searchInput')
    ?.addEventListener('input', handleSearch);

    document.querySelectorAll('input[name="filterBy"]').forEach(radio => {
        radio.addEventListener('click', function () {
            if (this.value === lastChecked) {
                this.checked = false;
                lastChecked = null;
            } else {
                lastChecked = this.value;
            }

            handleSearch();
        });
    });

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

    // Close menu when clicking any button inside it
    menu.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            menu.classList.add('d-none');
        });
    });

    document.addEventListener('click', () => {
        menu.classList.add('d-none');
    });
});


function setupEvents() {

    const search = document.getElementById('searchInput');
    if (search) search.addEventListener('input', handleSearch);
}

/* ------------ AUTOCOMPLETE SEARCHABLE DROPDOWNS ------------ */

// Data Store
const AutocompleteData = {
    assets: [],
    employees: [],
    rooms: []
};

async function loadAutocompleteData() {
    try {
        console.log("Loading autocomplete data...");
        const [assetRes, empRes, roomRes] = await Promise.all([
            fetch('/api/assets'),
            fetch('/api/employees/all'),
            fetch('/api/rooms/all')
        ]);

        AutocompleteData.assets = await assetRes.json();
        AutocompleteData.employees = await empRes.json();
        AutocompleteData.rooms = await roomRes.json();

        // Setup Asset Autocomplete
        setupAutocomplete(
            'assignAssetSearch', 
            'assignAssetId', 
            'assetResults', 
            AutocompleteData.assets, 
            (item) => `${item.asset_id} - ${item.description}`, 
            (item) => item.asset_id,
            (item, term) => (item.asset_id + item.description).toLowerCase().includes(term)
        );

        // Setup Employee Autocomplete
        setupAutocomplete(
            'assignEmployeeSearch', 
            'assignEmployeeId', 
            'employeeResults', 
            AutocompleteData.employees, 
            (item) => item.full_name, 
            (item) => item.employee_id,
            (item, term) => (item.full_name + item.employee_id).toLowerCase().includes(term)
        );

        // Setup Room Autocomplete
        setupAutocomplete(
            'assignRoomSearch', 
            'assignRoomId', 
            'roomResults', 
            AutocompleteData.rooms, 
            (item) => item.room_name, 
            (item) => item.room_id,
            (item, term) => (item.room_name + item.room_id).toLowerCase().includes(term)
        );

    } catch (err) {
        console.error("Failed to load autocomplete data:", err);
    }
}

function setupAutocomplete(inputId, hiddenId, resultsId, data, formatText, formatId, filterFn) {
    const input = document.getElementById(inputId);
    const hidden = document.getElementById(hiddenId);
    const results = document.getElementById(resultsId);

    if (!input || !results) return;

    // Remove existing listeners to prevent duplicates if function called multiple times
    const newInput = input.cloneNode(true);
    input.parentNode.replaceChild(newInput, input);
    
    const showResults = (term = '') => {
        const filtered = term.length > 0 
            ? data.filter(item => filterFn(item, term)).slice(0, 10)
            : data.slice(0, 10);

        if (filtered.length > 0) {
            results.innerHTML = filtered.map(item => `
                <div class="autocomplete-item" 
                     data-id="${formatId(item)}" 
                     data-display="${formatText(item).replace(/"/g, '&quot;')}">
                    <span class="item-name">${formatText(item)}</span>
                    <span class="item-id">ID: ${formatId(item)}</span>
                </div>
            `).join('');
            results.classList.remove('d-none');
        } else {
            results.innerHTML = '<div class="p-3 text-muted small">No matches found</div>';
            results.classList.remove('d-none');
        }
    };

    newInput.addEventListener('input', () => {
        hidden.value = ''; // Reset ID when typing
        showResults(newInput.value.toLowerCase());
    });

    newInput.addEventListener('click', (e) => {
        e.stopPropagation();
        showResults(newInput.value.toLowerCase());
    });

    newInput.addEventListener('focus', () => {
        showResults(newInput.value.toLowerCase());
    });

    results.addEventListener('click', (e) => {
        const item = e.target.closest('.autocomplete-item');
        if (item && item.dataset.id) {
            newInput.value = item.dataset.display;
            hidden.value = item.dataset.id;
            results.classList.add('d-none');
            
            // Visual feedback that it's selected
            newInput.classList.add('border-success');
            setTimeout(() => newInput.classList.remove('border-success'), 1000);
        }
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!newInput.contains(e.target) && !results.contains(e.target)) {
            results.classList.add('d-none');
        }
    });
}

// Global Listener for Modal
document.addEventListener('DOMContentLoaded', () => {
    const assignModal = document.getElementById('assignmentModal');
    if (assignModal) {
        assignModal.addEventListener('show.bs.modal', loadAutocompleteData);
    }
    const addAssetModal = document.getElementById('addAssetModal');
    if (addAssetModal) {
        addAssetModal.addEventListener('hidden.bs.modal', clearAddAssetModal);
    }
});