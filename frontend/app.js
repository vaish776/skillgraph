const API_BASE = "http://127.0.0.1:8000";


// --------------------------------------------------
// STATE
// --------------------------------------------------

let people = [];
let projects = [];
let currentPerson = null;


// --------------------------------------------------
// DOM HELPERS
// --------------------------------------------------

const loading = document.getElementById("loading");
const errorBox = document.getElementById("error");
const errorMessage = document.getElementById("error-message");
const content = document.getElementById("content");

const pageTitle = document.getElementById("page-title");


// --------------------------------------------------
// API
// --------------------------------------------------

async function apiFetch(endpoint) {

    const response = await fetch(`${API_BASE}${endpoint}`);

    if (!response.ok) {

        let message = `Request failed with status ${response.status}`;

        try {

            const data = await response.json();

            if (data.detail) {
                message = data.detail;
            }

        } catch {
            // Keep default error message.
        }

        throw new Error(message);
    }

    return response.json();
}


// --------------------------------------------------
// LOADING / ERROR
// --------------------------------------------------

function showLoading() {

    loading.classList.remove("hidden");
    errorBox.classList.add("hidden");

}


function hideLoading() {

    loading.classList.add("hidden");

}


function showError(message) {

    hideLoading();

    errorBox.classList.remove("hidden");

    errorMessage.textContent = message;

}


function hideError() {

    errorBox.classList.add("hidden");

}


// --------------------------------------------------
// PAGE NAVIGATION
// --------------------------------------------------

function showPage(pageName) {

    document.querySelectorAll(".page").forEach(page => {

        page.classList.add("hidden");

    });


    const page = document.getElementById(`${pageName}-page`);

    if (page) {

        page.classList.remove("hidden");

    }


    document.querySelectorAll(".nav-button").forEach(button => {

        button.classList.toggle(
            "active",
            button.dataset.page === pageName
        );

    });


    const titles = {

        dashboard: "Dashboard",

        people: "People",

        skills: "Skills",

        projects: "Projects",

        person: "Person",

        matches: "Project Matches"

    };


    pageTitle.textContent = titles[pageName] || "SkillGraph";

    hideError();


    if (pageName === "dashboard") {
        loadDashboard();
    }

    if (pageName === "people") {
        loadPeople();
    }

    if (pageName === "skills") {
        loadSkills();
    }

    if (pageName === "projects") {
        loadProjects();
    }

}


// --------------------------------------------------
// DASHBOARD
// --------------------------------------------------

async function loadDashboard() {

    showLoading();

    try {

        const [peopleData, projectsData] = await Promise.all([

            apiFetch("/api/people"),

            apiFetch("/api/projects")

        ]);


        people = peopleData;

        projects = projectsData;


        const skillSet = new Set();

        people.forEach(person => {

            (person.skills || []).forEach(skill => {

                skillSet.add(skill);

            });

        });


        const stats = document.getElementById("stats");

        stats.innerHTML = `

            <div class="stat">
                <div class="stat-number">
                    ${people.length}
                </div>

                <div class="stat-label">
                    People
                </div>
            </div>


            <div class="stat">
                <div class="stat-number">
                    ${skillSet.size}
                </div>

                <div class="stat-label">
                    Skills
                </div>
            </div>


            <div class="stat">
                <div class="stat-number">
                    ${projects.length}
                </div>

                <div class="stat-label">
                    Projects
                </div>
            </div>


            <div class="stat">
                <div class="stat-number">
                    Graph
                </div>

                <div class="stat-label">
                    Connected data
                </div>
            </div>

        `;


        hideLoading();

    } catch (error) {

        showError(
            `Unable to load dashboard: ${error.message}`
        );

    }

}


// --------------------------------------------------
// PEOPLE
// --------------------------------------------------

async function loadPeople() {

    showLoading();

    try {

        if (people.length === 0) {

            people = await apiFetch("/api/people");

        }


        renderPeople(people);

        hideLoading();

    } catch (error) {

        showError(
            `Unable to load people: ${error.message}`
        );

    }

}


function renderPeople(list) {

    const grid = document.getElementById("people-grid");


    if (!list.length) {

        grid.innerHTML = `

            <div class="empty">
                No people found.
            </div>

        `;

        return;
    }


    grid.innerHTML = list.map(person => {

        const initials = getInitials(person.name);

        const skills = person.skills || [];


        return `

            <article class="person-card">

                <div class="avatar">
                    ${escapeHtml(initials)}
                </div>


                <h3>
                    ${escapeHtml(person.name)}
                </h3>


                <p class="title">
                    ${escapeHtml(person.title || "Professional")}
                </p>


                <div class="tags">

                    ${skills.slice(0, 6).map(skill => `

                        <span class="tag">
                            ${escapeHtml(skill)}
                        </span>

                    `).join("")}

                </div>


                <button
                    class="link-button"
                    onclick="openPerson('${escapeAttribute(person.id)}')"
                >
                    View profile →
                </button>

            </article>

        `;

    }).join("");

}


// --------------------------------------------------
// PERSON DETAIL
// --------------------------------------------------

async function openPerson(personId) {

    showLoading();

    showPageWithoutLoading("person");

    try {

        const person = await apiFetch(
            `/api/people/${encodeURIComponent(personId)}`
        );


        currentPerson = person;


        const container =
            document.getElementById("person-detail");


        const projectsHtml = (person.projects || []).length

            ? person.projects.map(project => `

                <div class="project-mini">

                    <strong>
                        ${escapeHtml(project.name)}
                    </strong>

                    <span>
                        ${escapeHtml(project.description || "")}
                    </span>

                </div>

            `).join("")

            : `

                <div class="empty">
                    No projects connected to this person.
                </div>

            `;


        container.innerHTML = `

            <div class="detail-card">

                <div class="avatar">
                    ${escapeHtml(getInitials(person.name))}
                </div>


                <h3>
                    ${escapeHtml(person.name)}
                </h3>


                <p class="title">
                    ${escapeHtml(person.title || "Professional")}
                </p>


                <div class="detail-section">

                    <h4>
                        Skills
                    </h4>

                    <div class="tags">

                        ${(person.skills || []).map(skill => `

                            <span class="tag">
                                ${escapeHtml(skill)}
                            </span>

                        `).join("")}

                    </div>

                </div>


                <div class="detail-section">

                    <h4>
                        Company
                    </h4>

                    <p>
                        ${(person.companies || []).length
                            ? person.companies
                                .map(escapeHtml)
                                .join(", ")
                            : "No company listed"
                        }
                    </p>

                </div>


                <div class="detail-section">

                    <h4>
                        Connected Projects
                    </h4>

                    ${projectsHtml}

                </div>

            </div>

        `;


        hideLoading();

    } catch (error) {

        showError(
            `Unable to load profile: ${error.message}`
        );

    }

}


function showPageWithoutLoading(pageName) {

    document.querySelectorAll(".page").forEach(page => {

        page.classList.add("hidden");

    });


    const page = document.getElementById(`${pageName}-page`);

    if (page) {

        page.classList.remove("hidden");

    }


    document.querySelectorAll(".nav-button").forEach(button => {

        button.classList.remove("active");

    });


    pageTitle.textContent = "Person";

    hideError();

}


// --------------------------------------------------
// SKILLS
// --------------------------------------------------

async function loadSkills() {

    showLoading();

    try {

        if (people.length === 0) {

            people = await apiFetch("/api/people");

        }


        const skillMap = new Map();


        people.forEach(person => {

            (person.skills || []).forEach(skill => {

                if (!skillMap.has(skill)) {

                    skillMap.set(skill, new Set());

                }

                skillMap.get(skill).add(person.name);

            });

        });


        const skills = [...skillMap.entries()]
            .sort((a, b) => b[1].size - a[1].size);


        const grid = document.getElementById("skills-grid");


        if (!skills.length) {

            grid.innerHTML = `

                <div class="empty">
                    No skills found.
                </div>

            `;

        } else {

            grid.innerHTML = skills.map(([skill, peopleSet]) => `

                <article class="skill-card">

                    <h4>
                        ${escapeHtml(skill)}
                    </h4>

                    <p>
                        ${peopleSet.size}
                        ${peopleSet.size === 1 ? "person" : "people"}
                        connected
                    </p>

                </article>

            `).join("");

        }


        hideLoading();

    } catch (error) {

        showError(
            `Unable to load skills: ${error.message}`
        );

    }

}


// --------------------------------------------------
// PROJECTS
// --------------------------------------------------

async function loadProjects() {

    showLoading();

    try {

        projects = await apiFetch("/api/projects");


        const grid =
            document.getElementById("projects-grid");


        if (!projects.length) {

            grid.innerHTML = `

                <div class="empty">
                    No projects found.
                </div>

            `;

        } else {

            grid.innerHTML = projects.map(project => `

                <article class="project-card">

                    <p class="eyebrow">
                        PROJECT
                    </p>


                    <h3>
                        ${escapeHtml(project.name)}
                    </h3>


                    <p>
                        ${escapeHtml(project.description || "")}
                    </p>


                    <div class="tags">

                        ${(project.required_skills || [])
                            .map(skill => `

                                <span class="tag">
                                    ${escapeHtml(skill)}
                                </span>

                            `)
                            .join("")
                        }

                    </div>


                    <p style="margin-top: 14px;">
                        <strong>
                            ${project.people_count || 0}
                        </strong>
                        potential matches
                    </p>


                    <button
                        class="primary-button"
                        onclick="openProjectMatches('${escapeAttribute(project.id)}', '${escapeAttribute(project.name)}')"
                    >
                        Find matching people
                    </button>

                </article>

            `).join("");

        }


        hideLoading();

    } catch (error) {

        showError(
            `Unable to load projects: ${error.message}`
        );

    }

}


// --------------------------------------------------
// PROJECT MATCHES
// --------------------------------------------------

async function openProjectMatches(projectId, projectName) {

    showPageWithoutLoading("matches");

    showLoading();


    try {

        const matches = await apiFetch(
            `/api/projects/${encodeURIComponent(projectId)}/matches`
        );


        const container =
            document.getElementById("matches-content");


        container.innerHTML = `

            <div class="page-heading">

                <p class="eyebrow">
                    GRAPH MATCHING
                </p>

                <h3>
                    ${escapeHtml(projectName)}
                </h3>

                <p>
                    People ranked by connected skill matches.
                </p>

            </div>

        `;


        if (!matches.length) {

            container.innerHTML += `

                <div class="empty">

                    <h3>
                        No matching people
                    </h3>

                    <p style="margin-top: 8px;">
                        No one currently matches this project's
                        required skills.
                    </p>

                </div>

            `;

        } else {

            const list = document.createElement("div");

            list.className = "match-list";


            matches.forEach(match => {

                const card =
                    document.createElement("article");

                card.className = "match-card";


                const skills =
                    match.matched_skills || [];


                card.innerHTML = `

                    <div class="match-info">

                        <h4>
                            ${escapeHtml(match.name)}
                        </h4>

                        <p>
                            ${escapeHtml(match.title || "Professional")}
                        </p>


                        <div class="tags match-skills">

                            ${skills.map(skill => `

                                <span class="tag">
                                    ${escapeHtml(skill)}
                                </span>

                            `).join("")}

                        </div>

                    </div>


                    <div class="match-score">

                        ${match.match_count}
                        skill matches

                    </div>

                `;


                list.appendChild(card);

            });


            container.appendChild(list);

        }


        hideLoading();

    } catch (error) {

        showError(
            `Unable to find matches: ${error.message}`
        );

    }

}


// --------------------------------------------------
// SEARCH
// --------------------------------------------------

function setupSearch() {

    const search =
        document.getElementById("people-search");


    search.addEventListener("input", event => {

        const query =
            event.target.value.trim().toLowerCase();


        if (!query) {

            renderPeople(people);

            return;

        }


        const filtered = people.filter(person => {

            const name =
                (person.name || "").toLowerCase();

            const title =
                (person.title || "").toLowerCase();

            const skills =
                (person.skills || [])
                    .join(" ")
                    .toLowerCase();


            return (
                name.includes(query) ||
                title.includes(query) ||
                skills.includes(query)
            );

        });


        renderPeople(filtered);

    });

}


// --------------------------------------------------
// NAVIGATION EVENTS
// --------------------------------------------------

function setupNavigation() {

    document.querySelectorAll("[data-page]").forEach(button => {

        button.addEventListener("click", () => {

            showPage(button.dataset.page);

        });

    });


    document
        .getElementById("back-people")
        .addEventListener("click", () => {

            showPage("people");

        });


    document
        .getElementById("back-projects")
        .addEventListener("click", () => {

            showPage("projects");

        });

}


// --------------------------------------------------
// UTILITY
// --------------------------------------------------

function getInitials(name) {

    if (!name) {
        return "?";
    }


    return name
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map(word => word[0])
        .join("")
        .toUpperCase();

}


function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }


    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


function escapeAttribute(value) {

    return String(value || "")
        .replaceAll("\\", "\\\\")
        .replaceAll("'", "\\'");
}


// --------------------------------------------------
// START APPLICATION
// --------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    setupNavigation();

    setupSearch();

    loadDashboard();

});