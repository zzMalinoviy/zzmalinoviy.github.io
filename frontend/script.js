// Данные для карусели с друзьями - теперь с локальными фото (ваши данные сохранены)
const friendsData = [
    { 
        id: 1, 
        name: "Андрей", 
        avatarUrl: "images/friend1.jpg" 
    },
    { 
        id: 2, 
        name: "Арина", 
        avatarUrl: "images/friend2.jpg" 
    },
    { 
        id: 3, 
        name: "Эльдар", 
        avatarUrl: "images/friend6.jpg" 
    },
    { 
        id: 4, 
        name: "Ярик", 
        avatarUrl: "images/friend5.jpg" 
    },
    { 
        id: 5, 
        name: "Макс", 
        avatarUrl: "images/friend3.jpg" 
    },
    { 
        id: 6, 
        name: "Лиза", 
        avatarUrl: "images/friend4.jpg" 
    },
];

// Данные для треков (новая секция)
const tracksData = [
    {
        id: 1,
        title: "LUMI",
        artist: "UdieNnx",
        cover: "music/covers/cover1.jpg",
        file: "music/track1.mp3",
        duration: "1:44"
    },
    {
        id: 2,
        title: "днями и ночами",
        artist: "BUSHIDO ZHO",
        cover: "music/covers/cover2.jpg",
        file: "music/track2.mp3",
        duration: "2:22"
    },
    {
        id: 3,
        title: "Силуети",
        artist: "shadowrhyme",
        cover: "music/covers/cover3.jpg",
        file: "music/track3.mp3",
        duration: "2:41"
    },
    {
        id: 4,
        title: "Банк",
        artist: "ICEGERGERT",
        cover: "music/covers/cover4.jpg",
        file: "music/track4.mp3",
        duration: "2:58"
    },
    {
        id: 5,
        title: "KM",
        artist: "Aarne, Toxi$",
        cover: "music/covers/cover5.jpg",
        file: "music/track5.mp3",
        duration: "1:52"
    }
];

// Функция для проверки доступности изображения (чтобы показать заглушку если фото нет)
function checkImage(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(url);
        img.onerror = () => resolve('https://api.dicebear.com/7.x/adventurer/svg?seed=Unknown');
        img.src = url;
    });
}

// Функция для проверки доступности аудио
function checkAudio(url) {
    return new Promise((resolve) => {
        const audio = new Audio();
        audio.oncanplaythrough = () => resolve(url);
        audio.onerror = () => resolve(null);
        audio.src = url;
    });
}

// Инициализация карусели
async function initCarousel() {
    const carouselTrack = document.querySelector('.carousel-track');
    const indicatorsContainer = document.querySelector('.carousel-indicators');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    
    // Создание карточек друзей
    for (const friend of friendsData) {
        // Проверяем доступность локального фото
        const finalAvatarUrl = await checkImage(friend.avatarUrl);
        
        // Карточка друга
        const friendCard = document.createElement('div');
        friendCard.className = 'friend-card';
        friendCard.innerHTML = `
            <div class="friend-card-inner">
                <img src="${finalAvatarUrl}" alt="${friend.name}" class="friend-avatar">
                <h3 class="friend-name">${friend.name}</h3>
            </div>
        `;
        carouselTrack.appendChild(friendCard);
    }
    
    // Создаем индикаторы после создания всех карточек
    friendsData.forEach((friend, index) => {
        const indicator = document.createElement('div');
        indicator.className = `indicator ${index === 0 ? 'active' : ''}`;
        indicator.dataset.index = index;
        indicatorsContainer.appendChild(indicator);
        
        // Обработчик клика на индикатор
        indicator.addEventListener('click', () => {
            goToSlide(index);
            updateIndicators(index);
            resetAutoSlide();
        });
    });
    
    let currentIndex = 0;
    const totalSlides = friendsData.length;
    
    // Функция перехода к конкретному слайду
    function goToSlide(index) {
        // Для мобильных устройств показываем 1 карточку
        const isMobile = window.innerWidth <= 768;
        const cardsToShow = isMobile ? 1 : (window.innerWidth <= 992 ? 2 : 3);
        
        // Рассчитываем смещение
        let offset;
        if (isMobile) {
            offset = -index * 100;
        } else if (window.innerWidth <= 992) {
            offset = -index * 50;
        } else {
            offset = -index * (100 / 3);
        }
        
        carouselTrack.style.transform = `translateX(${offset}%)`;
        currentIndex = index;
    }
    
    // Функция обновления индикаторов
    function updateIndicators(index) {
        document.querySelectorAll('.indicator').forEach((indicator, i) => {
            indicator.classList.toggle('active', i === index);
        });
    }
    
    // Функция перехода к следующему слайду
    function nextSlide() {
        currentIndex = (currentIndex + 1) % totalSlides;
        goToSlide(currentIndex);
        updateIndicators(currentIndex);
    }
    
    // Функция перехода к предыдущему слайду
    function prevSlide() {
        currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
        goToSlide(currentIndex);
        updateIndicators(currentIndex);
    }
    
    // Обработчики кнопок
    prevBtn.addEventListener('click', () => {
        prevSlide();
        resetAutoSlide();
    });
    
    nextBtn.addEventListener('click', () => {
        nextSlide();
        resetAutoSlide();
    });
    
    // Автопрокрутка карусели
    let autoSlideInterval = setInterval(nextSlide, 4000);
    
    // Сброс интервала автопрокрутки
    function resetAutoSlide() {
        clearInterval(autoSlideInterval);
        autoSlideInterval = setInterval(nextSlide, 4000);
    }
    
    // Адаптация карусели при изменении размера окна
    window.addEventListener('resize', () => {
        goToSlide(currentIndex);
    });
    
    // Инициализация первой позиции
    goToSlide(0);
}

// Инициализация музыкального плеера (новая функция)
async function initMusicPlayer() {
    const musicGrid = document.querySelector('.music-grid');
    
    if (!musicGrid) return; // Если секции нет, выходим
    
    for (const track of tracksData) {
        // Проверяем доступность обложки
        const finalCoverUrl = await checkImage(track.cover);
        
        // Создаем карточку трека
        const trackCard = document.createElement('div');
        trackCard.className = 'track-card';
        trackCard.innerHTML = `
            <img src="${finalCoverUrl}" alt="${track.title}" class="track-cover">
            <div class="track-info">
                <h3 class="track-title">${track.title}</h3>
                <p class="track-artist">${track.artist}</p>
            </div>
            <div class="track-controls">
                <button class="track-btn play-btn" data-track="${track.file}">
                    <i class="fas fa-play"></i>
                </button>
                <div class="track-progress">
                    <div class="progress-bar">
                        <div class="progress" style="width: 0%"></div>
                    </div>
                    <div class="time-display">
                        <span class="current-time">0:00</span>
                        <span class="duration">${track.duration}</span>
                    </div>
                </div>
            </div>
            <div class="volume-control">
                <i class="fas fa-volume-up volume-icon"></i>
                <div class="volume-slider">
                    <div class="progress" style="width: 70%"></div>
                </div>
            </div>
        `;
        musicGrid.appendChild(trackCard);
    }
    
    // Инициализация аудио плеера
    let currentAudio = null;
    let currentPlayBtn = null;
    
    // Обработчики для всех кнопок воспроизведения
    document.querySelectorAll('.play-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const trackFile = this.getAttribute('data-track');
            const trackCard = this.closest('.track-card');
            
            // Если этот трек уже играет - пауза
            if (currentAudio && currentAudio.src.includes(trackFile)) {
                if (!currentAudio.paused) {
                    currentAudio.pause();
                    this.innerHTML = '<i class="fas fa-play"></i>';
                } else {
                    currentAudio.play();
                    this.innerHTML = '<i class="fas fa-pause"></i>';
                }
                return;
            }
            
            // Останавливаем текущий трек
            if (currentAudio) {
                currentAudio.pause();
                currentAudio.currentTime = 0;
                if (currentPlayBtn) {
                    currentPlayBtn.innerHTML = '<i class="fas fa-play"></i>';
                }
            }
            
            // Проверяем доступность аудиофайла
            const audioUrl = await checkAudio(trackFile);
            
            if (!audioUrl) {
                console.error(`Аудиофайл не доступен: ${trackFile}`);
                return;
            }
            
            // Создаем новый аудио элемент
            currentAudio = new Audio(audioUrl);
            currentPlayBtn = this;
            
            // Начинаем воспроизведение
            currentAudio.volume = 0.7; // Устанавливаем громкость 70%
            currentAudio.play().then(() => {
                this.innerHTML = '<i class="fas fa-pause"></i>';
            }).catch(error => {
                console.error('Ошибка воспроизведения:', error);
            });
            
            // Обновление прогресса
            const progressBar = trackCard.querySelector('.progress');
            const currentTimeEl = trackCard.querySelector('.current-time');
            const progressBarContainer = trackCard.querySelector('.progress-bar');
            
            currentAudio.addEventListener('timeupdate', () => {
                if (currentAudio.duration) {
                    const progress = (currentAudio.currentTime / currentAudio.duration) * 100;
                    progressBar.style.width = `${progress}%`;
                    
                    // Форматируем время
                    const minutes = Math.floor(currentAudio.currentTime / 60);
                    const seconds = Math.floor(currentAudio.currentTime % 60);
                    currentTimeEl.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
                }
            });
            
            // Когда трек закончился
            currentAudio.addEventListener('ended', () => {
                this.innerHTML = '<i class="fas fa-play"></i>';
                progressBar.style.width = '0%';
                currentTimeEl.textContent = '0:00';
            });
            
            // Клик по прогресс-бару для перемотки
            progressBarContainer.addEventListener('click', (e) => {
                if (currentAudio.duration) {
                    const rect = progressBarContainer.getBoundingClientRect();
                    const pos = (e.clientX - rect.left) / rect.width;
                    currentAudio.currentTime = pos * currentAudio.duration;
                }
            });
            
            // Управление громкостью
            const volumeSlider = trackCard.querySelector('.volume-slider');
            const volumeProgress = trackCard.querySelector('.volume-slider .progress');
            
            volumeSlider.addEventListener('click', (e) => {
                const rect = volumeSlider.getBoundingClientRect();
                const pos = (e.clientX - rect.left) / rect.width;
                const volumeValue = Math.max(0, Math.min(1, pos));
                volumeProgress.style.width = `${volumeValue * 100}%`;
                currentAudio.volume = volumeValue;
            });
        });
    });
}

// Анимация появления элементов при скролле
function initScrollAnimations() {
    // Наблюдатель для секций
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const content = entry.target.querySelector('.section-content');
                if (content) {
                    content.classList.add('visible');
                }
                
                // Если это секция с командой, наблюдаем за карточками
                if (entry.target.id === 'team') {
                    observeFriendCards();
                }
                
                // Если это секция с музыкой, наблюдаем за карточками треков
                if (entry.target.id === 'music') {
                    observeTrackCards();
                }
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '50px'
    });
    
    // Наблюдатель для карточек друзей
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '50px'
    });
    
    // Наблюдатель для карточек треков (новый наблюдатель)
    const trackObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '50px'
    });
    
    // Начать наблюдение за секциями
    document.querySelectorAll('section').forEach(section => {
        sectionObserver.observe(section);
    });
    
    // Наблюдение за карточками друзей
    function observeFriendCards() {
        const friendCards = document.querySelectorAll('.friend-card');
        friendCards.forEach(card => {
            cardObserver.observe(card);
        });
    }
    
    // Наблюдение за карточками треков (новая функция)
    function observeTrackCards() {
        const trackCards = document.querySelectorAll('.track-card');
        trackCards.forEach(card => {
            trackObserver.observe(card);
        });
    }
}

// Проверка видимости элементов при загрузке
function checkVisibilityOnLoad() {
    const sections = document.querySelectorAll('section');
    
    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom >= 0;
        
        if (isVisible) {
            const content = section.querySelector('.section-content');
            if (content) {
                content.classList.add('visible');
            }
            
            // Если видима секция с командой, показываем карточки
            if (section.id === 'team') {
                const friendCards = document.querySelectorAll('.friend-card');
                friendCards.forEach(card => {
                    card.classList.add('visible');
                });
            }
            
            // Если видима секция с музыкой, показываем карточки треков
            if (section.id === 'music') {
                const trackCards = document.querySelectorAll('.track-card');
                trackCards.forEach(card => {
                    card.classList.add('visible');
                });
            }
        }
    });
}

// Инициализация всех элементов при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await initCarousel();
        await initMusicPlayer(); // Добавлен вызов инициализации музыкального плеера
        initScrollAnimations();
        
        // Проверить видимость при загрузке
        setTimeout(() => {
            checkVisibilityOnLoad();
        }, 300);
        
        // Обработчик для плавного скролла по якорным ссылкам
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            });
        });
    } catch (error) {
        console.error('Ошибка при инициализации:', error);
    }
});

// Также проверять видимость при скролле
window.addEventListener('scroll', () => {
    checkVisibilityOnLoad();
});