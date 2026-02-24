// --- 1. 选项卡管理 ---
function switchMainTab(tabId, btn) {
    document.querySelectorAll('.tab-page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-link').forEach(l => l.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    if(btn) btn.classList.add('active');
}

function switchSubTab(tabId, btn) {
    const parent = btn.closest('.sub-pages');
    document.querySelectorAll('.sub-page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.sub-link').forEach(l => l.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    if(btn) btn.classList.add('active');
}

// --- 2. 状态栏与时钟 ---
function updateTime() {
    const now = new Date();
    const timeStr = now.getFullYear() + '-' +
        String(now.getMonth() + 1).padStart(2, '0') + '-' +
        String(now.getDate()).padStart(2, '0') + ' ' +
        String(now.getHours()).padStart(2, '0') + ':' +
        String(now.getMinutes()).padStart(2, '0') + ':' +
        String(now.getSeconds()).padStart(2, '0');
    document.getElementById('status-time').innerText = timeStr;
}

let statusProtected = false;
function updateStatus(msg, isCritical = false) {
    if (statusProtected && !isCritical) return;
    document.getElementById('status-msg').innerText = msg;
    if (isCritical) {
        statusProtected = true;
        setTimeout(() => { statusProtected = false; }, 5000);
    }
}

// --- 3. 业务功能 (复用并适配新 ID) ---
async function refreshExcelList() {
    const files = await eel.list_excel_files()();
    const select = document.getElementById('excel-list');
    select.innerHTML = '<option value="">请选择 Excel 文件...</option>';
    files.forEach(file => {
        const option = document.createElement('option');
        option.value = file;
        option.text = file.split('\\').pop();
        select.appendChild(option);
    });
}

// 通用规则 (PDF)
async function loadPDFRules() {
    const pdfs = await eel.get_pdf_rules()();
    const listDiv = document.getElementById('pdf-rules-container');
    listDiv.innerHTML = '';
    pdfs.forEach((pdf, i) => {
        const row = document.createElement('div');
        row.className = 'req-item';
        row.innerHTML = `
            <input type="checkbox" class="pdf-cb" value="${pdf}" id="pdf-${i}">
            <label for="pdf-${i}" style="color: blue; text-decoration: underline;">${pdf}</label>
        `;
        listDiv.appendChild(row);
    });
}

function selectAllPDF(val) {
    document.querySelectorAll('.pdf-cb').forEach(cb => cb.checked = val);
}

async function insertPDFRules() {
    const filePath = document.getElementById('excel-list').value;
    const selected = Array.from(document.querySelectorAll('.pdf-cb:checked')).map(cb => cb.value);
    if (!filePath || !selected.length) return alert('请选择文件和守则');
    const res = await eel.write_sop_block(filePath, 'special_requirement', selected.join('\n'))();
    updateStatus(res.message, true);
}

// 专项要求库
let allReqData = {};
async function initRequirements() {
    allReqData = await eel.get_special_requirements()();
    const pCombo = document.getElementById('product-combo');
    pCombo.innerHTML = '<option value="">选择产品...</option>';
    Object.keys(allReqData).forEach(k => {
        const opt = document.createElement('option');
        opt.value = k; opt.text = k;
        pCombo.appendChild(opt);
    });
}

function onProductChange() {
    const cat = document.getElementById('product-combo').value;
    const gList = document.getElementById('general-req-list');
    const projCombo = document.getElementById('project-combo');
    gList.innerHTML = '';
    projCombo.innerHTML = '<option value="">选择项目...</option>';

    if (!cat || !allReqData[cat]) return;

    (allReqData[cat]["通用要求"] || []).forEach((r, i) => {
        const div = document.createElement('div');
        div.className = 'req-item';
        div.innerHTML = `<input type="checkbox" class="g-req-cb" value="${r.content}" id="g-r-${i}">
                         <label for="g-r-${i}">[${r.type}] ${r.content.substring(0,30)}...</label>`;
        gList.appendChild(div);
    });

    (allReqData[cat]["项目要求"] || []).forEach(p => {
        const opt = document.createElement('option');
        opt.value = p["项目名称"]; opt.text = p["项目名称"];
        projCombo.appendChild(opt);
    });
}

function onProjectChange() {
    const cat = document.getElementById('product-combo').value;
    const projName = document.getElementById('project-combo').value;
    const pList = document.getElementById('project-req-list');
    pList.innerHTML = '';
    if (!cat || !projName) return;
    const proj = allReqData[cat]["项目要求"].find(x => x["项目名称"] === projName);
    if (proj) {
        (proj["具体要求"] || []).forEach((r, i) => {
            const div = document.createElement('div');
            div.className = 'req-item';
            div.innerHTML = `<input type="checkbox" class="p-req-cb" value="${r.content}" id="p-r-${i}">
                             <label for="p-r-${i}">[${r.type}] ${r.content.substring(0,30)}...</label>`;
            pList.appendChild(div);
        });
    }
}

async function insertRequirements(type) {
    const filePath = document.getElementById('excel-list').value;
    const selector = type === 'general' ? '.g-req-cb:checked' : '.p-req-cb:checked';
    const selected = Array.from(document.querySelectorAll(selector)).map(cb => cb.value);
    if (!filePath || !selected.length) return;
    const res = await eel.write_sop_block(filePath, 'special_requirement', selected.join('\n'))();
    alert(res.message);
}

// --- 4. AI 与其它工具 (适配新布局) ---
async function handleAIGenerate(blockType) {
    const inputId = blockType === 'operation_content' ? 'op-gen-out' : 'process-gen-out';
    const outEl = document.getElementById(inputId);
    outEl.innerText = '正在生成...';
    // 简单起见，从当前聚焦的某个 input 获取提示词，实际应完善
    const prompt = "请根据工序生成内容";
    window.currentOutputId = inputId;
    await eel.ai_generate_content(prompt, blockType)();
}

async function writeAIToExcel(blockType) {
    const inputId = blockType === 'operation_content' ? 'op-gen-out' : 'process-gen-out';
    const content = document.getElementById(inputId).innerText;
    const filePath = document.getElementById('excel-list').value;
    if (!filePath || !content) return;
    const res = await eel.write_sop_block(filePath, blockType, content, 'overwrite')();
    alert(res.message);
}

async function handleImageAudit() {
    const filePath = document.getElementById('excel-list').value;
    const out = document.getElementById('vision-output');
    out.innerText = '正在截图分析...';
    const res = await eel.audit_sop_image(filePath)();
    out.innerText = res.result || res.message;
}

// 知识库加载与填充
async function loadKnowledgeLists() {
    const kb = await eel.get_knowledge_base()();
    const processList = document.getElementById('process-kb-list');
    const opList = document.getElementById('op-kb-list');

    [processList, opList].forEach(list => {
        if (!list) return;
        list.innerHTML = '';
        kb.forEach(item => {
            const div = document.createElement('div');
            div.className = 'kb-item';
            div.innerText = item["工步名称"];
            div.onclick = (e) => fillAIInputFromKB(item, list.id, e);
            list.appendChild(div);
        });
    });
}

function fillAIInputFromKB(item, listId, event) {
    // 高亮选中项
    document.querySelectorAll(`#${listId} .kb-item`).forEach(el => el.classList.remove('selected'));
    event.target.classList.add('selected');

    if (listId === 'process-kb-list') {
        // 填充工艺要求与控制方法
        document.getElementById('process-gen-out').innerText =
            `【工艺要求】\n${item["工艺要求"]}\n\n【控制方法】\n${item["控制方法"]}`;
    } else {
        // 填充操作内容
        document.getElementById('op-gen-out').innerText = item["操作内容"];
    }
}

// --- 5. 初始化 ---
window.onload = () => {
    refreshExcelList();
    loadPDFRules();
    initRequirements();
    loadKnowledgeLists();
    setInterval(updateTime, 1000);
    updateTime();
};

// --- 10. 通用编辑器弹窗逻辑 ---
let currentEditingKey = null;

async function openDataEditor(key) {
    currentEditingKey = key;
    const titleMap = {
        'knowledge_base': '工步知识库编辑器',
        'prompts': 'AI 提示词设置',
        'special_requirements': '工艺要求库编辑器',
        'templates': 'Excel 模板坐标设置 (高级)'
    };

    document.getElementById('modal-title').innerText = titleMap[key] || '数据编辑器';
    updateStatus(`正在加载 ${key}...`);

    const data = await eel.get_config(key)();
    document.getElementById('json-editor-area').value = JSON.stringify(data, null, 4);
    document.getElementById('modal-editor').style.display = 'block';
}

function closeModal() {
    document.getElementById('modal-editor').style.display = 'none';
    currentEditingKey = null;
}

async function saveModalData() {
    const rawValue = document.getElementById('json-editor-area').value;
    try {
        const jsonData = JSON.parse(rawValue);
        updateStatus(`正在保存 ${currentEditingKey}...`);

        const success = await eel.save_config(currentEditingKey, jsonData)();
        if (success) {
            alert('保存成功！新配置已即时生效。');
            closeModal();
            // 如果修改了知识库或专项要求，尝试刷新界面列表
            if (currentEditingKey === 'knowledge_base') loadKnowledgeLists();
            if (currentEditingKey === 'special_requirements') initRequirements();
        } else {
            alert('保存失败，请检查文件访问权限。');
        }
    } catch (e) {
        alert('JSON 格式错误，请检查！\n' + e.message);
    }
}

eel.expose(on_ai_chunk);
function on_ai_chunk(chunk, full) {
    const id = window.currentOutputId;
    if (id && document.getElementById(id)) {
        document.getElementById(id).innerText = full;
    }
}
