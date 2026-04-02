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
            action: (cells[3]?.textContent || '').trim(),
            fullText: row.textContent.toLowerCase()
        };
    }

    function matchesFilter(data, filterValue) {
        if (filterValue === 'all') return true;
        if (filterValue === 'missing') return data.missing !== '-';
        if (filterValue === 'relocation') return data.relocated !== '-';
        if (filterValue === 'reconciliation') return data.reconciliation !== '';
        return true;
    }

    function applyFilters() {
        const searchTerm = searchInput.value.trim().toLowerCase();
        const filterValue = filterSelect.value;

        getRows().forEach(row => {
            const data = getRowData(row);
            const matchesSearch = !searchTerm || data.fullText.includes(searchTerm);
            const show = matchesSearch && matchesFilter(data, filterValue);
            row.style.display = show ? '' : 'none';
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', applyFilters);
    }

    if (viewMissingBtn) {
        viewMissingBtn.addEventListener('click', () => {
            filterSelect.value = 'missing';
            applyFilters();
        });
    }

    if (viewRelocationBtn) {
        viewRelocationBtn.addEventListener('click', () => {
            filterSelect.value = 'relocation';
            applyFilters();
        });
    }

    tableBody.addEventListener('click', async (event) => {
        const notifyBtn = event.target.closest('.notify-btn');
        if (!notifyBtn) return;

        const row = notifyBtn.closest('tr');
        const data = getRowData(row);

        let payload = {
            missing_asset: data.missing,
            relocated_asset: data.relocated,
            reconciliation: data.reconciliation
        };

        try {
            const response = await fetch('/notify-discrepancy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
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
            alert('Notification route is not ready yet.');
        }
    });

    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            const visibleRows = getRows().filter(row => row.style.display !== 'none');

            const csvRows = [
                ['Missing Assets', 'Relocated Assets', 'Reconciliation', 'Action']
            ];

            visibleRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                csvRows.push([
                    (cells[0]?.textContent || '').trim(),
                    (cells[1]?.textContent || '').trim(),
                    (cells[2]?.textContent || '').trim(),
                    (cells[3]?.textContent || '').trim()
                ]);
            });

            const csvContent = csvRows.map(row =>
                row.map(value => `"${String(value).replace(/"/g, '""')}"`).join(',')
            ).join('\n');

            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);

            const link = document.createElement('a');
            link.href = url;
            link.download = 'discrepancy_report.csv';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        });
    }

    applyFilters();
});