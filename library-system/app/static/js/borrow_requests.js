function updateStatus(slipId, status) {
    fetch(`/staff/borrow-requests/${slipId}/update`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({status: status})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const row = document.getElementById(`row-${slipId}`);
            if (row) {
                const statusCell = row.querySelector(".status-badge");
                if (statusCell) {
                    if (status === "APPROVED") {
                        statusCell.innerHTML = `<span class="badge bg-success">Đã duyệt</span>`;
                    } else if (status === "REJECTED") {
                        statusCell.innerHTML = `<span class="badge bg-danger">Từ chối</span>`;
                    }
                }
            }
            alert(data.message);
        } else {
            alert("Lỗi: " + data.message);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Có lỗi xảy ra!");
    });
}
