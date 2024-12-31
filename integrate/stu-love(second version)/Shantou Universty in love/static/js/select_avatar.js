// 头像选择相关函数
function showPresetImages() {
    document.getElementById('preset-images-modal').style.display = 'block';
}

function closePresetImages() {
    document.getElementById('preset-images-modal').style.display = 'none';
}

function selectImage(img) {
    const avatar = document.getElementById('avatar');
    const sidebarAvatar = document.getElementById('sidebar-avatar');
    const indexSidebarAvatar = document.getElementById('index-sidebar-avatar'); // 新增：话题页面的头像

    // 更新顶部头像
    if (avatar) {
        avatar.src = img.src;
    }

    // 更新侧边栏头像
    if (sidebarAvatar) {
        sidebarAvatar.src = img.src;
    }

    // 更新话题页面的头像（如果存在）
    if (indexSidebarAvatar) {
        indexSidebarAvatar.src = img.src;
    }

    // 将头像路径存储到 localStorage
    localStorage.setItem('selectedAvatar', img.src);
    closePresetImages();  // 如果有弹窗，关闭它
}

function loadAvatar() {
    const savedAvatar = localStorage.getItem('selectedAvatar');

    if (savedAvatar) {
        const avatarElement = document.getElementById('avatar');
        const sidebarAvatar = document.getElementById('sidebar-avatar');
        const indexSidebarAvatar = document.getElementById('index-sidebar-avatar'); // 新增：话题页面的头像

        // 恢复顶部头像
        if (avatarElement) {
            avatarElement.src = savedAvatar;
        }

        // 恢复侧边栏头像
        if (sidebarAvatar) {
            sidebarAvatar.src = savedAvatar;
        }

        // 恢复话题页面的头像（如果存在）
        if (indexSidebarAvatar) {
            indexSidebarAvatar.src = savedAvatar;
        }
    }
}

// 在页面加载时调用 loadAvatar 函数
document.addEventListener('DOMContentLoaded', function() {
    loadAvatar();
});

/*
function selectImage(img) {
    const avatar = document.getElementById('avatar');
    const sidebarAvatar = document.getElementById('sidebar-avatar');

    // 更新顶部头像
    avatar.src = img.src;

    // 同时更新侧边栏头像
    if (sidebarAvatar) {
        sidebarAvatar.src = img.src;
    }

    // 将头像路径存储到 localStorage
    localStorage.setItem('selectedAvatar', img.src);
    closePresetImages();
}

function loadAvatar() {
    const savedAvatar = localStorage.getItem('selectedAvatar');

    if (savedAvatar) {
        const avatarElement = document.getElementById('avatar');
        const sidebarAvatar = document.getElementById('sidebar-avatar');

        // 恢复顶部头像
        if (avatarElement) {
            avatarElement.src = savedAvatar;
        }

        // 恢复侧边栏头像
        if (sidebarAvatar) {
            sidebarAvatar.src = savedAvatar;
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadAvatar();
});
*/

// 编辑模式切换函数
var isEditMode = true; // 默认进入编辑模式

function toggleEditMode() {
    const inputs = document.querySelectorAll('.editable');
    const saveBtn = document.getElementById('saveBtn');
    const editBtn = document.getElementById('editBtn');

    isEditMode = !isEditMode;
    inputs.forEach(input => input.readOnly = !isEditMode);
    saveBtn.style.display = isEditMode ? 'block' : 'none';
    editBtn.style.display = isEditMode ? 'none' : 'block';

    // 不再在这里控制模态框的显示
    // const presetImages = document.getElementById('preset-images-modal');
    // presetImages.style.display = isEditMode ? 'block' : 'none';

}

// 保存信息函数
function saveInfo() {
    const username = document.getElementById('username').value;
    const gender = document.getElementById('gender').value;
    const grade = document.getElementById('grade').value;
    const campus = document.getElementById('campus').value;
    const college = document.getElementById('college').value;
    if (!username || !gender || !grade || !campus || !college ) {
        alert('请填写昵称、性别、年级、校区和学院这些必填项！');
        return
    }
    //const signature = document.getElementById('signature').value || null;
    //const hometown = document.getElementById('hometown').value || null;
    //const hobby = document.getElementById('hobby').value || null;
    //const major = document.getElementById('major').value || null;
    //const constellation = document.getElementById('constellation').value || null;
    //const mbti = document.getElementById('mbti').value || null;
    //const declaration = document.getElementById('declaration').value || null;
    //const personality = document.getElementById('personality').value || null;
    //const avatar = document.getElementById('avatar').src;
    //const birthday = document.getElementById('birthday').value || null;
    const signatureElement = document.getElementById('signature');
    const signature = signatureElement ? signatureElement.value || null : null;

    const hometownElement = document.getElementById('hometown');
    const hometown = hometownElement ? hometownElement.value || null : null;

    const hobbyElement = document.getElementById('hobby');
    const hobby = hobbyElement ? hobbyElement.value || null : null;

    const majorElement = document.getElementById('major');
    const major = majorElement ? majorElement.value || null : null;

    const constellationElement = document.getElementById('constellation');
    const constellation = constellationElement ? constellationElement.value || null : null;

    const mbtiElement = document.getElementById('mbti');
    const mbti = mbtiElement ? mbtiElement.value || null : null;

    const declarationElement = document.getElementById('declaration');
    const declaration = declarationElement ? declarationElement.value || null : null;

    const personalityElement = document.getElementById('personality');
    const personality = personalityElement ? personalityElement.value || null : null;

    const avatarElement = document.getElementById('avatar');
    const avatar = avatarElement ? avatarElement.src || null : null;

    const birthdayElement = document.getElementById('birthday');
    const birthday = birthdayElement ? birthdayElement.value || null : null;


    // 构建要发送的数据对象
    const data = {
        username,
        gender,
        grade,
        campus,
        college,
        signature,
        hometown,
        hobby,
        major,
        constellation,
        mbti,
        declaration,
        personality,
        avatar,
        //user_id: userId, // 假设用户ID为1，实际应用中应从session或token中获取
        birthday
        
    };

    // 发送数据到服务器（这里使用jQuery的ajax方法）
    $.ajax({
        url: '/update_info',
        method: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            alert('信息保存成功！');
            // 关闭编辑模式
            isEditMode = false;
            document.querySelectorAll('.editable').forEach(input => input.readOnly = true);
            document.getElementById('editBtn').style.display = 'block';
            document.getElementById('saveBtn').style.display = 'none';
            document.getElementById('preset-images-modal').style.display = 'none';
        },
        error: function(error) {
            alert('信息保存失败，请重试。');
        }
    });

}