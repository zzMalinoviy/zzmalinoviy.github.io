// changelog.js
document.addEventListener('DOMContentLoaded', function() {
    // Поиск по обновлениям
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const updateEntries = document.querySelectorAll('.update-entry');
    
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        
        if (searchTerm === '') {
            // Показать все записи если поиск пустой
            updateEntries.forEach(entry => {
                entry.style.display = 'block';
                setTimeout(() => {
                    entry.style.opacity = '1';
                }, 50);
            });
            return;
        }
        
        updateEntries.forEach(entry => {
            const title = entry.querySelector('.update-title').textContent.toLowerCase();
            const content = entry.querySelector('.update-content').textContent.toLowerCase();
            const tags = Array.from(entry.querySelectorAll('.tag')).map(tag => tag.textContent.toLowerCase());
            
            const matchesSearch = title.includes(searchTerm) || 
                                 content.includes(searchTerm) ||
                                 tags.some(tag => tag.includes(searchTerm));
            
            if (matchesSearch) {
                entry.style.display = 'block';
                setTimeout(() => {
                    entry.style.opacity = '1';
                }, 50);
                
                // Подсветка найденного текста
                highlightText(entry, searchTerm);
            } else {
                entry.style.opacity = '0';
                setTimeout(() => {
                    entry.style.display = 'none';
                }, 300);
            }
        });
    }
    
    function highlightText(element, searchTerm) {
        // Удаляем предыдущие подсветки
        const highlights = element.querySelectorAll('.highlight');
        highlights.forEach(hl => {
            const parent = hl.parentNode;
            parent.replaceChild(document.createTextNode(hl.textContent), hl);
            parent.normalize();
        });
        
        // Подсвечиваем текст
        highlightNode(element, searchTerm);
    }
    
    function highlightNode(node, searchTerm) {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent;
            const regex = new RegExp(`(${searchTerm})`, 'gi');
            const newText = text.replace(regex, '<mark class="highlight">$1</mark>');
            
            if (newText !== text) {
                const span = document.createElement('span');
                span.innerHTML = newText;
                node.parentNode.replaceChild(span, node);
            }
        } else if (node.nodeType === Node.ELEMENT_NODE && 
                   node.tagName !== 'MARK' && 
                   node.tagName !== 'STYLE' && 
                   node.tagName !== 'SCRIPT') {
            Array.from(node.childNodes).forEach(child => {
                highlightNode(child, searchTerm);
            });
        }
    }
    
    // События для поиска
    searchBtn.addEventListener('click', performSearch);
    
    searchInput.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            performSearch();
        }
    });
    
    // Пагинация
    const pageButtons = document.querySelectorAll('.page-btn');
    const nextButton = document.querySelector('.next-btn');
    
    pageButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Убираем активный класс у всех кнопок
            pageButtons.forEach(btn => btn.classList.remove('active'));
            // Добавляем активный класс текущей кнопке
            this.classList.add('active');
            
            // Здесь можно добавить логику загрузки страницы
            // Например: loadPage(parseInt(this.textContent));
            
            // Пока просто прокручиваем наверх
            window.scrollTo({
                top: document.querySelector('.changelog-feed').offsetTop - 100,
                behavior: 'smooth'
            });
        });
    });
    
    nextButton.addEventListener('click', function() {
        const currentActive = document.querySelector('.page-btn.active');
        const currentPage = parseInt(currentActive.textContent);
        
        if (currentPage < 5) { // 5 - последняя страница
            // Переключаем активную страницу
            pageButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.page-btn')[currentPage].classList.add('active');
            
            // Прокручиваем наверх
            window.scrollTo({
                top: document.querySelector('.changelog-feed').offsetTop - 100,
                behavior: 'smooth'
            });
        }
    });
    
    // Анимация появления записей при загрузке
    updateEntries.forEach((entry, index) => {
        entry.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Добавляем стиль для подсветки
    const style = document.createElement('style');
    style.textContent = `
        .highlight {
            background-color: rgba(255, 235, 59, 0.3);
            padding: 2px 0;
            border-radius: 3px;
            color: #ffeb3b;
        }
    `;
    document.head.appendChild(style);
    
    // Автофокус на поле поиска
    searchInput.focus();
});
