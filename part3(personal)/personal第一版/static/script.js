// 头像选择相关函数
function showPresetImages() {
    document.getElementById('preset-images-modal').style.display = 'block';
}

function closePresetImages() {
    document.getElementById('preset-images-modal').style.display = 'none';
}

function selectImage(img) {
    const avatar = document.getElementById('avatar');
    avatar.src = img.src;
    closePresetImages();
}

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
    const name = document.getElementById('name').value;
    const gender = document.getElementById('gender').value;
    const age = document.getElementById('age').value;
    const signature = document.getElementById('signature').value;
    const hometown = document.getElementById('hometown').value;
    const hobby = document.getElementById('hobby').value;
    const campus = document.getElementById('campus').value;
    const major = document.getElementById('major').value;
    const constellation = document.getElementById('constellation').value;
    const mbti = document.getElementById('mbti').value;
    const declaration = document.getElementById('declaration').value;
    const personality = document.getElementById('personality').value;
    const avatar = document.getElementById('avatar').src;
    const birthday = document.getElementById('birthday').value;

    // 构建要发送的数据对象
    const data = {
        name,
        gender,
        age,
        signature,
        hometown,
        hobby,
        campus,
        major,
        constellation,
        mbti,
        declaration,
        personality,
        avatar,
        user_id: 1, // 假设用户ID为1，实际应用中应从session或token中获取
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