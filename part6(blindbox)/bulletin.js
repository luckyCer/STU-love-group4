/*
// 获取弹幕容器
const bulletinContent = document.querySelector('.bulletin-content');

// 定义一个包含多个用户名的数组
const usernames = [
  "小明", "小红", "小刚", "小丽", "小强", "小美", "小斌", "小芳", "小杰", "小燕",
  // 可以根据需要添加更多用户名
];

// 定义最大弹幕数量
const maxBulletins = 5;

// 存储当前显示的弹幕元素
let bulletins = [];

// 随机选择一个用户名
function getRandomUsername() {
  const randomIndex = Math.floor(Math.random() * usernames.length);
  return usernames[randomIndex];
}

// 生成随机的 RGB 颜色
function getRandomColor() {
  const r = Math.floor(Math.random() * 256); // 红色分量
  const g = Math.floor(Math.random() * 256); // 绿色分量
  const b = Math.floor(Math.random() * 256); // 蓝色分量
  return `rgb(${r}, ${g}, ${b})`;
}

// 动态创建弹幕
function createBulletin() {
  // 随机选择一个用户名
  const username = getRandomUsername();
  // 生成弹幕文本
  const text = `${username}购买了一元盲盒......`;

  // 创建弹幕元素
  const p = document.createElement('p');
  p.className = 'bulletin-item'; // 添加类名以便应用CSS样式
  p.textContent = text;

  // 设置其他样式
  p.style.fontSize = `${Math.random() * 6 + 18}px`; // 字体大小在18px到22px之间随机
  p.style.color = getRandomColor(); // 随机颜色
  p.style.background = 'rgba(255, 255, 255, 0.8)'; // 白色背景，透明度为80%

  // 将弹幕添加到容器中
  bulletinContent.appendChild(p);

  // 将新弹幕添加到数组中
  bulletins.push(p);

  // 如果超过最大数量，则移除最早的弹幕
  if (bulletins.length > maxBulletins) {
    const oldestBulletin = bulletins.shift();
    bulletinContent.removeChild(oldestBulletin);
  }

  // 在动画结束后移除弹幕
  p.addEventListener('animationend', () => {
    bulletinContent.removeChild(p);
    // 从数组中移除该弹幕
    const index = bulletins.indexOf(p);
    if (index > -1) {
      bulletins.splice(index, 1);
    }
  });
}

// 定时器：每隔几秒钟生成一条新的弹幕
setInterval(createBulletin, 3000); // 每3秒生成一条新弹幕
 */

// 获取弹幕容器
const bulletinContent = document.querySelector('.bulletin-content');

// 定义最大弹幕数量
const maxBulletins = 6;

// 存储当前显示的弹幕元素
let bulletins = [];

// 生成随机的 RGB 颜色
function getRandomColor() {
  const r = Math.floor(Math.random() * 256); // 红色分量
  const g = Math.floor(Math.random() * 256); // 绿色分量
  const b = Math.floor(Math.random() * 256); // 蓝色分量
  return `rgb(${r}, ${g}, ${b})`;
}

// 获取当前用户的用户名
function getUsername() {
  return fetch('/get_usernames')
    .then(response => {
      // 检查响应是否为 200（成功）
      if (!response.ok) {
        throw new Error('Failed to fetch username, response not OK');
      }
      return response.json();
    })
    .then(data => {
      if (data.username) {
        return data.username;
      } else {
        console.error("Error fetching username: ", data.error);
        return "未知用户"; // 返回默认值
      }
    })
    .catch(error => {
      console.error("Error in getUsername:", error);
      return "错误用户"; // 在出错时返回错误用户名
    });
}


// 动态创建弹幕
function createBulletin() {
  // 获取用户名
  getUsername().then(username => {
    // 生成弹幕文本
    const text = `${username}购买了一元盲盒......`;

    // 创建弹幕元素
    const p = document.createElement('p');
    p.className = 'bulletin-item'; // 添加类名以便应用CSS样式
    p.textContent = text;

    // 设置其他样式
    p.style.fontSize = `${Math.random() * 6 + 18}px`; // 字体大小在18px到22px之间随机
    p.style.color = getRandomColor(); // 随机颜色
    p.style.background = 'rgba(255, 255, 255, 0.8)'; // 白色背景，透明度为80%

    // 将弹幕添加到容器中
    bulletinContent.appendChild(p);

    // 将新弹幕添加到数组中
    bulletins.push(p);

    // 如果超过最大数量，则移除最早的弹幕
    if (bulletins.length > maxBulletins) {
      const oldestBulletin = bulletins.shift();
      bulletinContent.removeChild(oldestBulletin);
    }

    // 在动画结束后移除弹幕
    p.addEventListener('animationend', () => {
      bulletinContent.removeChild(p);
      // 从数组中移除该弹幕
      const index = bulletins.indexOf(p);
      if (index > -1) {
        bulletins.splice(index, 1);
      }
    });
  });
}

// 定时器：每隔几秒钟生成一条新的弹幕
setInterval(createBulletin, 3000); // 每3秒生成一条新弹幕