const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
const contentContainer = document.querySelector('.content');
const links = document.querySelectorAll('.adaptive-menu a, .hero-btns a');
const overlay = document.getElementById('status-overlay');

let width, height, clusters = [];
const mouse = { x: -2000, y: -2000 };

// Логика заглушек
function openStatus(type) {
    const title = document.getElementById('status-title');
    const desc = document.getElementById('status-desc');
    
    if(type === 'no-tg') {
        title.innerText = "Уже чиним!";
        desc.innerText = "У этого пользователя временно отсутствует Telegram, но мы работаем над этим.";
    } else {
        title.innerText = "В разработке";
        desc.innerText = "Этот раздел находится на стадии проектирования. Загляните позже!";
    }
    overlay.classList.add('active');
}

function closeStatus() {
    overlay.classList.remove('active');
}

// Навигация
function navigate(e) {
    const href = this.getAttribute('href');
    
    // Если это ссылка в разработке (для меню)
    if (this.classList.contains('dev-link')) {
        e.preventDefault();
        openStatus('dev');
        return;
    }

    if (href && href.startsWith('#')) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            contentContainer.scrollTo({ top: target.offsetTop, behavior: 'smooth' });
            document.querySelectorAll('.adaptive-menu a').forEach(l => l.classList.remove('active'));
            const menuLink = document.querySelector(`.adaptive-menu a[href="${href}"]`);
            if (menuLink) menuLink.classList.add('active');
        }
    }
}

links.forEach(l => l.addEventListener('click', navigate));

// Слушатель для кнопок друзей без ТГ
document.querySelectorAll('.no-tg').forEach(b => {
    b.addEventListener('click', (e) => {
        e.preventDefault();
        openStatus('no-tg');
    });
});

// Интерактивный фон (с поддержкой Touch)
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
window.addEventListener('touchmove', (e) => { updateMouse(e); }, { passive: false });
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
        if(Math.hypot(mouse.x-this.x, mouse.y-this.y) < 150) this.scare();
        this.points.forEach(p => { p.ox += (p.tx-p.ox)*0.05; p.oy += (p.ty-p.oy)*0.05; });
    }
    draw() {
        ctx.strokeStyle = 'rgba(99, 102, 241, 0.25)'; ctx.beginPath();
        this.points.forEach(p => ctx.lineTo(this.x + p.ox, this.y + p.oy));
        ctx.closePath(); ctx.stroke();
    }
}

function init() { clusters = Array.from({length: window.innerWidth > 768 ? 90 : 35}, () => new Cluster()); }
function animate() { ctx.clearRect(0,0,width,height); clusters.forEach(c => { c.update(); c.draw(); }); requestAnimationFrame(animate); }

resize(); animate();
