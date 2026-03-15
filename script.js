const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
const links = document.querySelectorAll('.adaptive-menu a, .hero-btns a');
const overlay = document.getElementById('status-overlay');
const projectDetails = document.getElementById('project-details');

let width, height, clusters = [];
const mouse = { x: -2000, y: -2000 };

const projectsData = {
    site_bz: {
        title: "Основной сайт команды Bezonov Reels!",
        date: "15 Марта 2026",
        img: "site.JPG",
        desc: "Самая первая работа от команды\n\nСтруктура:\n- Главная, приветствие пользователя.\n- Раздел с командой.\n- Страница с проектами.\n- Страница с обновлениями.",
        link: "https://github.com/zzMalinoviy/TemplateSiteBzrs"
    }
};

const updatesData = [
    { project: "BZRS - Сайт", version: "v2.0.1", date: "15.03.2026", text: "Завершение работы над основными модулями.", tag: "feature", tagText: "Новое" },
    { project: "BZRS - Сайт", version: "v2.0.2", date: "15.03.2026", text: "Независимое обновление стилей.", tag: "fix", tagText: "Исправление" },
];

function openProject(id) {
    const data = projectsData[id];
    if(!data) return;
    document.getElementById('det-title').innerText = data.title;
    document.getElementById('det-date').innerText = data.date;
    document.getElementById('det-img').src = data.img;
    document.getElementById('det-text').innerText = data.desc;
    document.getElementById('det-download').href = data.link;
    projectDetails.style.display = 'block';
    setTimeout(() => projectDetails.classList.add('active'), 10);
}

function closeDetails() {
    projectDetails.classList.remove('active');
    setTimeout(() => projectDetails.style.display = 'none', 500);
}

function closeStatus() { overlay.classList.remove('active'); }

function navigate(e) {
    const href = this.getAttribute('href');
    if (href && !href.startsWith('#')) return;
    e.preventDefault();

    if (href && href.startsWith('#')) {
        closeDetails();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
            document.querySelectorAll('.adaptive-menu a').forEach(l => l.classList.remove('active'));
            const menuLink = document.querySelector(`.adaptive-menu a[href="${href}"]`);
            if (menuLink) menuLink.classList.add('active');
        }
    }
}

function renderUpdates(filter = '') {
    const list = document.getElementById('updates-list');
    if (!list) return;
    list.innerHTML = '';
    const filtered = updatesData.filter(u => u.project.toLowerCase().includes(filter.toLowerCase()));
    filtered.forEach(u => {
        const item = document.createElement('div');
        item.className = 'team-item';
        item.innerHTML = `
            <div class="user-info">
                <div class="user-text">
                    <h3 class="card-name">${u.project} <span class="card-tag">${u.version}</span></h3>
                    <span class="card-tag">${u.text}</span>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
                <span class="update-badge tag-${u.tag}">${u.tagText}</span>
                <span class="card-tag" style="font-size: 0.75rem;">${u.date}</span>
            </div>`;
        list.appendChild(item);
    });
}

links.forEach(l => l.addEventListener('click', navigate));
document.getElementById('updates-search').addEventListener('input', (e) => renderUpdates(e.target.value));

function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    init();
}

const updateMouse = (e) => {
    const pos = e.touches ? e.touches[0] : e;
    mouse.x = pos.clientX;
    mouse.y = pos.clientY;
};

window.addEventListener('resize', resize);
window.addEventListener('mousemove', updateMouse);
window.addEventListener('touchmove', updateMouse, { passive: false });
window.addEventListener('touchstart', (e) => { updateMouse(e); clusters.forEach(c => c.scare()); }, { passive: false });
window.addEventListener('mousedown', () => clusters.forEach(c => c.scare()));

class Cluster {
    constructor() { this.reset(); }
    reset() {
        this.x = Math.random() * width; this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 0.4; this.vy = (Math.random() - 0.5) * 0.4;
        this.points = Array.from({length:6}, () => ({ ox: Math.random()*40-20, oy: Math.random()*40-20, tx: Math.random()*40-20, ty: Math.random()*40-20 }));
    }
    scare() { this.points.forEach(p => { p.tx = (Math.random()-0.5)*80; p.ty = (Math.random()-0.5)*80; }); }
    update() {
        this.x += this.vx; this.y += this.vy;
        if(this.x<0 || this.x>width) this.vx *= -1;
        if(this.y<0 || this.y>height) this.vy *= -1;
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        if(dx*dx + dy*dy < 22500) this.scare(); 
        this.points.forEach(p => { p.ox += (p.tx-p.ox)*0.05; p.oy += (p.ty-p.oy)*0.05; });
    }
    draw() {
        ctx.strokeStyle = 'rgba(99, 102, 241, 0.25)'; ctx.beginPath();
        this.points.forEach(p => ctx.lineTo(this.x + p.ox, this.y + p.oy));
        ctx.closePath(); ctx.stroke();
    }
}

function init() { clusters = Array.from({length: window.innerWidth > 768 ? 80 : 30}, () => new Cluster()); }
function animate() { ctx.clearRect(0,0,width,height); clusters.forEach(c => { c.update(); c.draw(); }); requestAnimationFrame(animate); }

resize(); animate(); renderUpdates();

/* --- БЛОКИРОВКА ЗУМА ДЛЯ TELEGRAM И ПК --- */

// 1. Отключение pinch-to-zoom (пальцами)
document.addEventListener('touchmove', function (e) {
    if (e.scale !== 1) { e.preventDefault(); }
}, { passive: false });

// 2. Отключение двойного тапа для зума
let lastTouchEnd = 0;
document.addEventListener('touchend', function (e) {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) { e.preventDefault(); }
    lastTouchEnd = now;
}, false);

// 3. Отключение зума на ПК (Ctrl + колесо и Ctrl + клавиши)
window.addEventListener('wheel', (e) => {
    if (e.ctrlKey) { e.preventDefault(); }
}, { passive: false });

window.addEventListener('keydown', (e) => {
    if (e.ctrlKey && (e.key === '+' || e.key === '-' || e.key === '=' || e.key === '0')) {
        e.preventDefault();
    }
});
