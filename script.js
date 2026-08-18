// --- ДАННЫЕ КВЕСТА И ЗАСТАВКИ ---
const ALLOWED_PASSWORDS = [
    "АХАЕШЕЧКИ",
    "ОХАОШЕЧКИ",
    "АХАОШЕЧКИ",
    "ОХАЕШЕЧКИ"
];

const introPhotos = [
    "assets/photo1.jpg",
    "assets/photo2.jpg",
    "assets/photo3.jpg",
    "assets/photo4.jpg",
    "assets/photo5.jpg",
    "assets/photo6.jpg"
];

const subtexts = [
    "Мы готовимся, ещё немного... 🍌",
    "Настраиваем бананомеры... 🍌",
    "Миньоны наводят красоту... ✨",
    "Собираем самые лучшие воспоминания... ❤️",
    "Почти всё готово! 🎉"
];

const questQuestions = [
    {
        title: "Вопрос 1 из 4",
        text: "Дата твоего рождения?",
        answers: ["19 августа", "12 августа", "19 сентября", "15 августа"],
        correct: 0,
        gif: "assets/q1.gif"
    },
    {
        title: "Вопрос 2 из 4",
        text: "Твое любимое место в доме?",
        answers: ["Диван на кухне", "Кровать", "Рабочий стол", "У окна"],
        correct: 1,
        gif: "assets/q2.gif"
    },
    {
        title: "Вопрос 3 из 4",
        text: "Первая буква имен твоих животных? (в порядке кто появился раньше)",
        answers: ["СМА", "МСА", "АМС", "АСМ"],
        correct: 2,
        gif: "assets/q3.gif"
    },
    {
        title: "Вопрос 4 из 4",
        text: "Как сначала звали симку?",
        answers: ["Фиалка", "Розочка", "Лилия", "Ромашка"],
        correct: 1,
        gif: "assets/q4.gif"
    }
];

let currentQuestion = 0;

function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

// Предзагрузка аудиофайлов
function loadAndPlayAudio() {
    const audio1 = document.getElementById('bg-audio');
    const audio2 = document.getElementById('bg-audio-2');
    const status = document.getElementById('audio-status');
    const btnLoad = document.getElementById('btn-load-audio');
    const btnStart = document.getElementById('btn-start-intro');

    status.innerText = "Загружаем треки...";

    audio1.load();
    audio2.load();

    setTimeout(() => {
        status.innerText = "Музыка готова! Жми НАЧАТЬ!";
        btnLoad.style.display = 'none';
        btnStart.style.display = 'inline-block';
    }, 800);
}

// Запуск заставки (19 сек)
function startPhotoShow() {
    const audio1 = document.getElementById('bg-audio');
    
    audio1.play().catch(err => console.log(err));

    showScreen('screen-intro-show');
    const stage = document.getElementById('photo-stage');
    const subtextEl = document.getElementById('intro-subtext');
    const progressBar = document.getElementById('intro-progress-bar');
    
    const TOTAL_TIME = 19000;
    const photoIntervalTime = 2500;
    
    progressBar.style.transition = `width ${TOTAL_TIME}ms linear`;
    setTimeout(() => { progressBar.style.width = '100%'; }, 50);

    let photoIndex = 0;
    let subtextIndex = 0;

    addFramedPhoto(stage, photoIndex);

    const interval = setInterval(() => {
        photoIndex = (photoIndex + 1) % introPhotos.length;
        subtextIndex = (subtextIndex + 1) % subtexts.length;
        
        subtextEl.innerText = subtexts[subtextIndex];
        addFramedPhoto(stage, photoIndex);
    }, photoIntervalTime);

    // ПО ИСТЕЧЕНИИ 19 СЕКУНД:
    setTimeout(() => {
        clearInterval(interval);
        
        // 1. Останавливаем 1-й трек
        audio1.pause();
        audio1.currentTime = 0;

        // 2. Переходим к экрану пароля
        showScreen('screen-password');

        // 3. Запускаем второй трек
        startMainMusic();
    }, TOTAL_TIME);
}

// Запуск фоновой музыки и вызов виджета
function startMainMusic() {
    const audio2 = document.getElementById('bg-audio-2');
    const widget = document.getElementById('music-widget');

    audio2.play().then(() => {
        setVinylSpinning(true);
    }).catch(err => console.log(err));

    // Делаем плавающий плеер видимым
    widget.classList.add('visible');

    // Обновление прогресс-бара трека
    audio2.addEventListener('timeupdate', updateMainMusicProgress);
}

// Управление выдвижной кнопкой плеера
function toggleMusicWidget() {
    const widget = document.getElementById('music-widget');
    widget.classList.toggle('expanded');
}

// Старт / Пауза для основного трека
function togglePlayMainMusic() {
    const audio2 = document.getElementById('bg-audio-2');
    const playBtn = document.getElementById('widget-play-btn');

    if (audio2.paused) {
        audio2.play();
        playBtn.innerText = '⏸️';
        setVinylSpinning(true);
    } else {
        audio2.pause();
        playBtn.innerText = '▶️';
        setVinylSpinning(false);
    }
}

function setVinylSpinning(isSpinning) {
    const vinyl = document.getElementById('vinyl-record');
    if (isSpinning) {
        vinyl.classList.add('spinning');
    } else {
        vinyl.classList.remove('spinning');
    }
}

// Обновление прогресс-бара в виджете
function updateMainMusicProgress() {
    const audio2 = document.getElementById('bg-audio-2');
    const progressBar = document.getElementById('widget-progress-bar');
    if (audio2.duration) {
        const pct = (audio2.currentTime / audio2.duration) * 100;
        progressBar.style.width = pct + '%';
    }
}

// Перемотка трека по клику на полосу
function seekMainMusic(e) {
    const audio2 = document.getElementById('bg-audio-2');
    const container = e.currentTarget;
    const clickX = e.offsetX;
    const width = container.clientWidth;
    if (audio2.duration) {
        audio2.currentTime = (clickX / width) * audio2.duration;
    }
}

function addFramedPhoto(container, index) {
    const photoUrl = introPhotos[index];
    const isTwoEyes = Math.random() > 0.5;
    const angle = Math.floor(Math.random() * 30) - 15;
    const zIndex = container.children.length + 1;

    const photoCard = document.createElement('div');
    photoCard.className = 'minion-framed-photo';
    photoCard.style.transform = `rotate(${angle}deg)`;
    photoCard.style.zIndex = zIndex;

    const eyesHtml = isTwoEyes 
        ? `<div class="photo-eye"><div class="photo-pupil"></div></div><div class="photo-eye"><div class="photo-pupil"></div></div>`
        : `<div class="photo-eye"><div class="photo-pupil"></div></div>`;

    photoCard.innerHTML = `
        <img src="${photoUrl}" alt="Photo">
        <div class="photo-goggles">
            ${eyesHtml}
        </div>
    `;

    container.appendChild(photoCard);
}

function checkPassword() {
    const input = document.getElementById('password-input').value.trim().toUpperCase();
    const error = document.getElementById('password-error');
    
    if (ALLOWED_PASSWORDS.includes(input)) {
        error.style.display = 'none';
        startQuest();
    } else {
        error.style.display = 'block';
    }
}

document.getElementById('password-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        checkPassword();
    }
});

function startQuest() {
    currentQuestion = 0;
    showScreen('screen-quest');
    renderQuestion();
}

function renderQuestion() {
    const q = questQuestions[currentQuestion];
    document.getElementById('question-title').innerText = q.title;
    document.getElementById('question-text').innerText = q.text;
    document.getElementById('quest-error').style.display = 'none';

    const imgEl = document.getElementById('quest-img');
    if (q.gif) {
        imgEl.src = q.gif;
        imgEl.style.display = 'block';
    }

    const progress = ((currentQuestion) / questQuestions.length) * 100;
    document.getElementById('progress-bar').style.width = progress + '%';

    const container = document.getElementById('answers-container');
    container.innerHTML = '';
    
    q.answers.forEach((ans, index) => {
        const btn = document.createElement('button');
        btn.className = 'btn-option';
        btn.innerText = ans;
        btn.onclick = () => selectAnswer(index);
        container.appendChild(btn);
    });
}

function selectAnswer(index) {
    const q = questQuestions[currentQuestion];
    const error = document.getElementById('quest-error');

    if (index === q.correct) {
        error.style.display = 'none';
        currentQuestion++;
        if (currentQuestion < questQuestions.length) {
            renderQuestion();
        } else {
            finishQuest();
        }
    } else {
        error.style.display = 'block';
    }
}

function finishQuest() {
    showScreen('screen-final');
    document.getElementById('progress-bar').style.width = '100%';
    launchConfetti();
}

function launchConfetti() {
    var duration = 4 * 1000;
    var animationEnd = Date.now() + duration;
    var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 1000 };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    var interval = setInterval(function() {
        var timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        var particleCount = 50 * (timeLeft / duration);
        confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } }));
        confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } }));
    }, 250);
}