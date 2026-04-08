document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const filterSelect = document.getElementById('filterSelect');
    const viewMissingBtn = document.getElementById('viewMissingBtn');
    const viewRelocationBtn = document.getElementById('viewRelocationBtn');
    const exportBtn = document.getElementById('exportBtn');
    const tableBody = document.getElementById('discrepancy-table-body');

    if (!tableBody) return;

    function getRows() {
        return Array.from(tableBody.querySelectorAll('tr'));
    }

    function getRowData(row) {
        const cells = row.querySelectorAll('td');
        return {
            missing: (cells[0]?.textContent || '').trim(),
            relocated: (cells[1]?.textContent || '').trim(),
            reconciliation: (cells[2]?.textContent || '').trim(),
            fullText: row.textContent.toLowerCase()
        };
    }

    function matchesFilter(data, filterValue) {
        if (filterValue === 'all') return true;
        if (filterValue === 'missing') return data.missing && data.missing !== '-';
        if (filterValue === 'relocation') return data.relocated && data.relocated !== '-';
        if (filterValue === 'reconciliation') return data.reconciliation !== '';
        return true;
    }

    function applyFilters() {
        const searchTerm = (searchInput?.value || '').trim().toLowerCase();
        const filterValue = filterSelect?.value || 'all';

        getRows().forEach(row => {
            const data = getRowData(row);
            const matchesSearch = !searchTerm || data.fullText.includes(searchTerm);
            const show = matchesSearch && matchesFilter(data, filterValue);
            row.style.display = show ? '' : 'none';
        });
    }

    function renderRows(rows) {
        if (!rows || rows.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted">No discrepancies found.</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = rows.map(row => {
            // Supports either shape:
            // 1) { missing_asset, relocated_asset, reconciliation }
            // 2) { missing, relocated, reconciliation }
            const missingAsset = row.missing_asset ?? row.missing ?? '-';
            const relocatedAsset = row.relocated_asset ?? row.relocated ?? '-';
            const reconciliation = row.reconciliation || 'Pending';
            const actionButtons = [];

            if (row.can_mark_lost && row.missing_id) {
                actionButtons.push(`
                    <button
                        class="btn btn-sm btn-outline-danger mark-lost-btn"
                        data-missing-id="${row.missing_id}"
                        type="button"
                    >
                        Mark Lost
                    </button>
                `);
            }

            if (row.can_mark_relocated && row.relocation_id) {
                actionButtons.push(`
                    <button
                        class="btn btn-sm btn-outline-success mark-relocated-btn"
                        data-relocation-id="${row.relocation_id}"
                        type="button"
                    >
                        Mark Relocated
                    </button>
                `);
            }

            actionButtons.push(`
                <button
                    class="btn btn-sm btn-outline-secondary notify-btn"
                    data-missing-id="${row.missing_id || ''}"
                    data-relocation-id="${row.relocation_id || ''}"
                    type="button"
                >
                    Notify
                </button>
            `);

            return `
                <tr data-asset-id="${row.asset_id || ''}">
                    <td>${missingAsset}</td>
                    <td>${relocatedAsset}</td>
                    <td>${reconciliation}</td>
                    <td class="d-flex flex-wrap gap-2">${actionButtons.join('')}</td>
                </tr>
            `;
        }).join('');
    }

    async function loadDiscrepancies() {
        try {
            const response = await fetch('/api/discrepancies', { method: 'GET' });
            if (!response.ok) {
                throw new Error(`Failed to fetch discrepancies (${response.status})`);
            }

            const rows = await response.json();
            renderRows(rows);
            applyFilters();
        } catch (error) {
            console.error('Error loading discrepancy rows:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-danger">Unable to load discrepancy data.</td>
                </tr>
            `;
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', applyFilters);
    }

    if (viewMissingBtn && filterSelect) {
        viewMissingBtn.addEventListener('click', () => {
            filterSelect.value = 'missing';
            applyFilters();
        });
    }

    if (viewRelocationBtn && filterSelect) {
        viewRelocationBtn.addEventListener('click', () => {
            filterSelect.value = 'relocation';
            applyFilters();
        });
    }

    tableBody.addEventListener('click', async (event) => {
        const notifyBtn = event.target.closest('.notify-btn');
        const markLostBtn = event.target.closest('.mark-lost-btn');
        const markRelocatedBtn = event.target.closest('.mark-relocated-btn');

        if (markLostBtn) {
            const missingId = markLostBtn.dataset.missingId;
            if (!missingId) return;
            if (!confirm('Mark this missing asset as lost?')) return;

            try {
                const response = await fetch('/mark-asset-lost', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ missing_id: missingId })
                });

                if (!response.ok) {
                    const result = await response.json().catch(() => ({}));
                    throw new Error(result.message || 'Failed to mark asset as lost.');
                }

                await loadDiscrepancies();
                alert('Asset marked as lost.');
            } catch (error) {
                console.error('Mark lost error:', error);
                alert(error.message || 'Failed to mark asset as lost.');
            }
            return;
        }

        if (markRelocatedBtn) {
            const relocationId = markRelocatedBtn.dataset.relocationId;
            const roomId = prompt('Enter relocated room ID:');
            if (!relocationId || !roomId) return;

            try {
                const response = await fetch('/mark-asset-relocated', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        relocation_id: relocationId,
                        item_relocated_room_id: roomId
                    })
                });

                if (!response.ok) {
                    const result = await response.json().catch(() => ({}));
                    throw new Error(result.message || 'Failed to mark asset as relocated.');
                }

                await loadDiscrepancies();
                alert('Asset marked as relocated.');
            } catch (error) {
                console.error('Mark relocated error:', error);
                alert(error.message || 'Failed to mark asset as relocated.');
            }
            return;
        }

        if (!notifyBtn) return;

        const row = notifyBtn.closest('tr');
        const data = getRowData(row);

        const payload = {
            asset_id: row.dataset.assetId || null,
            missing_id: notifyBtn.dataset.missingId || null,
            relocation_id: notifyBtn.dataset.relocationId || null,
            missing_asset: data.missing,
            relocated_asset: data.relocated,
            reconciliation: data.reconciliation
        };

        try {
            const response = await fetch('/notify-discrepancy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert('Notification sent successfully.');
            } else {
                const result = await response.json().catch(() => ({}));
                alert(result.message || 'Failed to send notification.');
            }
        } catch (error) {
            console.error('Notification error:', error);
            alert('Failed to send notification.');
        }
    });

    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            window.location.href = '/api/discrepancies/download';
        });
    }

    loadDiscrepancies();
});