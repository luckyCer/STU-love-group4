document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('filter-form');
    const cardsContainer = document.getElementById('cards-container');
    
    // 处理滤镜选项点击事件
filterForm.querySelectorAll('input[type="radio"]').forEach(input => {
input.addEventListener('click', function () {
    // 改变点击后的颜色
    this.style.backgroundColor = '#ccc';
    setTimeout(() => {
        this.style.backgroundColor = ''; // 一段时间后恢复原状
    }, 300);
});
});


    // 初始化时显示所有卡片
    loadAllCards();

    // 监听表单提交事件
    filterForm.addEventListener('submit', function (event) {
        event.preventDefault(); // 阻止默认的表单提交行为
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData).toString();
        filterCards(params);
    });

    async function loadAllCards() {
        try {
            const response = await fetch('/');
            if (response.ok) {
                const users = await response.json();
                console.log('Loaded all users:', users); // 输出数据

                // 清空现有的卡片
                cardsContainer.innerHTML = '';

                users.forEach(user => {
                    const card = createCard(user);
                    cardsContainer.appendChild(card);
                    console.log(`Generated card with data-category: ${card.getAttribute('data-category')}`); // 输出卡片数据
                });
            } else {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    async function filterCards(params) {
        try {
            const response = await fetch(`/filter_users?${params}`);
            if (response.ok) {
                const filteredUsers = await response.json();
                console.log('Filtered users:', filteredUsers); // 输出数据

                // 清空现有的卡片
                cardsContainer.innerHTML = '';

                filteredUsers.forEach(user => {
                    const card = createCard(user);
                    cardsContainer.appendChild(card);
                    console.log(`Generated card with data-category: ${card.getAttribute('data-category')}`); // 输出卡片数据
                });
            } else {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error filtering users:', error);
        }
    }

    function createCard(user) {
        const categoryString = `${user.campus} ${user.grade} ${user.gender} ${user.college}`;
        const cardElement = document.createElement('div');
        cardElement.classList.add('card');
        cardElement.setAttribute('data-category', categoryString);

        cardElement.innerHTML = `
            <div class="front">
                <div class="photo"><img src="${user.photo || ''}" alt="User Photo"></div>
                <h5>${user.username}</h5>
            </div>
            <div class="back">
                <h5>About ${user.username}</h5>
                <h6>${user.gender}</h6>
                <p>${user.love_declaration}</p>
                <a href="#">聊解</a>
            </div>
        `;

        return cardElement;
    }
});