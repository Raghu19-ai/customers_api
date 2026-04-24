const BASE_URL = "/api";
console.log("app.js loaded");


let currentPage = 1;
let currentLimit = 5;


// UI NAVIGATION
function showLogin() {
    document.getElementById("loginSection").style.display = "block";
    document.getElementById("registerSection").style.display = "none";
    document.getElementById("dashboardSection").style.display = "none";
    document.getElementById("navbar").style.display = "none";
}

function showRegister() {
    document.getElementById("loginSection").style.display = "none";
    document.getElementById("registerSection").style.display = "block";
}

function showDashboard() {
    document.getElementById("loginSection").style.display = "none";
    document.getElementById("registerSection").style.display = "none";
    document.getElementById("dashboardSection").style.display = "block";
    document.getElementById("navbar").style.display = "flex";

    const role = localStorage.getItem("role");
    if (role === "admin" || role === "superadmin") {
        document.getElementById("admin-actions").style.display = "block";
    } else {
        document.getElementById("admin-actions").style.display = "none";
    }

    if (role === "superadmin") {
        document.getElementById("userManagementSection").style.display = "block";
        loadUsers();
    } else {
        document.getElementById("userManagementSection").style.display = "none";
    }

    loadCustomers();
    fetchStats();
}

async function fetchStats() {
    const token = localStorage.getItem("token");
    try {
        const userRes = await fetch(`${BASE_URL}/auth/users/count`, {
            headers: { "Authorization": "Bearer " + token }
        });
        if (userRes.ok) {
            const userData = await userRes.json();
            document.getElementById("total-users").innerText = userData.count;
        }
    } catch (err) {
        console.error("Stats fetch error:", err);
    }
}


// LOGIN
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // extract username
    const username = email.split("@")[0];
    console.log("Username:", username);

    const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
        alert("Login failed");
        return;
    }

    // store username (NOT email)
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", data.role);
    localStorage.setItem("user_identifier", username);

    // update UI
    document.getElementById("user-name").innerText = username;
    document.getElementById("user-avatar").innerText = username.charAt(0).toUpperCase();

    showDashboard();
}


// REGISTER
async function register() {
    const email = document.getElementById("reg_email").value;
    const username = document.getElementById("reg_username").value;
    const password = document.getElementById("reg_password").value;
    const role = document.getElementById("role").value;

    try {
        const res = await fetch(`${BASE_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, username, password, role })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Registration failed");
            return;
        }

        alert("Registered successfully");
        showLogin();
    } catch (err) {
        console.error(err);
    }
}


// LOAD CUSTOMERS (PAGINATED)
async function loadCustomers() {
    const token = localStorage.getItem("token");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");

    try {
        // Show loading state
        document.getElementById("customerTable").innerHTML = '<tr><td colspan="4" style="text-align:center; padding: 2rem;"><div class="spinner"></div> Loading customers...</td></tr>';

        const res = await fetch(`${BASE_URL}/customers/?page=${currentPage}&limit=${currentLimit}`, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await res.json();

        if (!res.ok) {
            console.error("Fetch failed", data);
            document.getElementById("customerTable").innerHTML = '<tr><td colspan="4" style="color: red; text-align:center; padding: 1rem;">Failed to load customers.</td></tr>';
            return;
        }

        if (data.length === 0) {
            document.getElementById("customerTable").innerHTML = '<tr><td colspan="4" style="text-align:center; padding: 2rem; color: var(--text-muted);">No customers found.</td></tr>';
            if (nextBtn) nextBtn.disabled = true;
            if (prevBtn) prevBtn.disabled = (currentPage === 1);
            return;
        }

        let html = "";
        data.forEach(c => {
            const addrHtml = c.addresses && c.addresses.length > 0
                ? c.addresses.map(a => `<div style="font-size:0.75rem;">${a.city}, ${a.state}</div>`).join('')
                : '<span style="color:var(--text-muted); font-size:0.75rem;">No address</span>';

            html += `
            <tr>
                <td>
                    <div style="font-weight:600;">${c.name}</div>
                    <div style="font-size:0.7rem; color:var(--text-muted);">${c.customer_type || 'General'} | ${c.status || 'Active'}</div>
                </td>
                <td>
                    <div style="font-size:0.8rem;">${c.email}</div>
                    <div style="font-size:0.8rem; color:var(--text-muted);">${c.phone || "N/A"}</div>
                </td>
                <td>
                    <div style="max-height: 50px; overflow-y: auto;">
                        ${addrHtml}
                    </div>
                    <button class="btn btn-outline btn-sm" style="margin-top:0.25rem; padding:1px 5px; font-size: 0.65rem;" onclick="openAddressModal(${c.id})">
                        + Add Address
                    </button>
                </td>
                <td>
                    <div style="display:flex; gap:0.5rem;">
                         ${localStorage.getItem("role") === "superadmin" ?
                    `<button class="btn btn-danger btn-sm" style="padding: 4px 8px;" onclick="deleteCustomer(${c.id})"><i data-lucide="trash-2" style="width:14px; height:14px;"></i></button>` :
                    `<span style="color:var(--text-muted); font-size:0.75rem;">-</span>`}
                    </div>
                </td>
            </tr>
            `;
        });

        document.getElementById("customerTable").innerHTML = html;
        document.getElementById("currentPage").innerText = currentPage;

        // Update button states
        if (prevBtn) prevBtn.disabled = (currentPage === 1);
        if (nextBtn) nextBtn.disabled = (data.length < currentLimit);

        lucide.createIcons();
    } catch (err) {
        console.error(err);
        document.getElementById("customerTable").innerHTML = '<tr><td colspan="4" style="color: red; text-align:center;">Connection Error.</td></tr>';
    }
}


// ADD CUSTOMER
async function addCustomer() {
    const token = localStorage.getItem("token");
    const payload = {
        name: document.getElementById("cust_name").value,
        age: parseInt(document.getElementById("cust_age").value),
        gender: document.getElementById("cust_gender").value,
        date_of_birth: document.getElementById("cust_dob").value,
        email: document.getElementById("cust_email").value,
        phone: document.getElementById("cust_phone").value,
        alternate_phone: document.getElementById("cust_alt_phone").value,
        company: document.getElementById("cust_company").value,
        job_title: document.getElementById("cust_job").value,
        experience_years: parseInt(document.getElementById("cust_exp").value),
        customer_type: document.getElementById("cust_type").value,
        status: document.getElementById("cust_status").value,
        notes: document.getElementById("cust_notes").value,
        source: document.getElementById("cust_source").value
    };

    try {
        const res = await fetch(`${BASE_URL}/customers/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            closeModal('customerModal');
            loadCustomers();
        } else {
            const data = await res.json();
            alert(data.error || "Failed");
        }
    } catch (err) {
        console.error(err);
    }
}


// ADD ADDRESS
async function addAddress() {
    const token = localStorage.getItem("token");
    const payload = {
        customer_id: parseInt(document.getElementById("addr_customer_id").value),
        city: document.getElementById("city").value,
        state: document.getElementById("state").value,
        pincode: document.getElementById("pincode").value
    };

    try {
        const res = await fetch(`${BASE_URL}/addresses/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            closeModal('addressModal');
            loadCustomers();
        } else {
            const data = await res.json();
            alert(data.error || "Failed");
        }
    } catch (err) {
        console.error(err);
    }
}


// PAGINATION
function nextPage() {
    currentPage++;
    loadCustomers();
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        loadCustomers();
    }
}

function changeLimit() {
    currentLimit = parseInt(document.getElementById("limitSelector").value);
    currentPage = 1; // Reset to page 1 when limit changes
    loadCustomers();
}


// CSV UPLOAD
async function uploadCSV() {
    console.log("uploadCSV called");
    const token = localStorage.getItem("token");
    const fileInput = document.getElementById("csv-input");
    if (!fileInput || !fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const res = await fetch(`${BASE_URL}/customers/upload`, {
            method: "POST",
            headers: { "Authorization": "Bearer " + token },
            body: formData
        });

        const data = await res.json();

        if (res.ok) {
            alert(`Success! Imported ${data.created || 0} customers.`);
            loadCustomers();
            fetchStats();
        } else {
            alert(data.error || "Upload failed");
        }
    } catch (err) {
        console.error(err);
        alert("Server error during upload");
    } finally {
        fileInput.value = "";
    }
}

async function uploadAddressCSV() {
    console.log("uploadAddressCSV called");
    const token = localStorage.getItem("token");
    const fileInput = document.getElementById("addr-csv-input");
    if (!fileInput || !fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const res = await fetch(`${BASE_URL}/addresses/upload`, {
            method: "POST",
            headers: { "Authorization": "Bearer " + token },
            body: formData
        });

        const data = await res.json();

        if (res.ok) {
            alert(`Success! Imported ${data.created || 0} addresses.`);
            loadCustomers();
        } else {
            alert(data.error || "Upload failed");
        }
    } catch (err) {
        console.error(err);
        alert("Server error during upload");
    } finally {
        fileInput.value = "";
    }
}

async function loadUsers() {
    const token = localStorage.getItem("token");
    try {
        const res = await fetch(`${BASE_URL}/auth/users`, {
            headers: { "Authorization": "Bearer " + token }
        });
        if (!res.ok) return;

        const users = await res.json();
        let html = "";

        users.forEach(u => {
            html += `
            <tr>
                <td style="font-weight:600;">${u.username}</td>
                <td><span class="badge">${u.role}</span></td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteUserAccount(${u.id})">
                        Delete
                    </button>
                </td>
            </tr>`;
        });
        document.getElementById("userTable").innerHTML = html;
        lucide.createIcons();
    } catch (err) {
        console.error(err);
    }
}


async function deleteUserAccount(id) {
    const token = localStorage.getItem("token");
    if (!confirm("Are you sure you want to delete this account?")) return;

    try {
        const res = await fetch(`${BASE_URL}/auth/users/${id}`, {
            method: "DELETE",
            headers: { "Authorization": "Bearer " + token }
        });
        if (res.ok) {
            loadUsers();
            fetchStats();
        }
    } catch (err) {
        console.error(err);
    }
}

// DELETE CUSTOMER
async function deleteCustomer(id) {
    const token = localStorage.getItem("token");
    if (!confirm("Really delete?")) return;

    const res = await fetch(`${BASE_URL}/customers/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    if (res.ok) {
        alert("Deleted");
        loadCustomers();
    }
}


// LOGOUT
function logout() {
    localStorage.clear();
    showLogin();
}


// MODAL HANDLING
function openModal(id) {
    document.getElementById(id).style.display = "flex";
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
}

function openAddressModal(customerId) {
    document.getElementById("addr_customer_id").value = customerId;
    openModal("addressModal");
}


// AUTO LOGIN
window.onload = function () {
    const token = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user_identifier");
    if (token) {
        if (savedUser) {
            document.getElementById("user-name").innerText = savedUser;
            document.getElementById("user-avatar").innerText = savedUser.charAt(0).toUpperCase();
        }
        showDashboard();
    } else {
        showLogin();
    }
};

// EXPOSE TO GLOBAL SCOPE
window.uploadCSV = uploadCSV;
window.uploadAddressCSV = uploadAddressCSV;
window.login = login;
window.register = register;
window.logout = logout;
window.addCustomer = addCustomer;
window.addAddress = addAddress;
window.nextPage = nextPage;
window.prevPage = prevPage;
window.changeLimit = changeLimit;
window.openModal = openModal;
window.closeModal = closeModal;
window.openAddressModal = openAddressModal;
window.deleteCustomer = deleteCustomer;
window.deleteUserAccount = deleteUserAccount;
console.log("app.js fully loaded and functions exposed");