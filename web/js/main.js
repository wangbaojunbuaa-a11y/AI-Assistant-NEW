// --- 1. Tab Management ---
function switchMainTab(tabId, btn) {
    document.querySelectorAll('.tab-page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(l => l.classList.remove('active'));

    const target = document.getElementById(tabId);
    if (target) {
        target.classList.add('active');
        if(btn) btn.classList.add('active');

        // Auto-refresh when entering General tab
        if (tabId === 'tab-general') refreshExcelList();
    }
}

function switchSubTab(tabId, btn) {
    const parent = btn.closest('.sub-viewport');
    document.querySelectorAll('.sub-page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.sub-tab-btn').forEach(l => l.classList.remove('active'));

    const target = document.getElementById(tabId);
    if (target) {
        target.classList.add('active');
        if(btn) btn.classList.add('active');
    }
}

// --- 2. Real-time Feedback & Clock ---
function updateTime() {
    const now = new Date();
    const timeStr = now.getFullYear() + '-' +
        String(now.getMonth() + 1).padStart(2, '0') + '-' +
        String(now.getDate()).padStart(2, '0') + ' ' +
        String(now.getHours()).padStart(2, '0') + ':' +
        String(now.getMinutes()).padStart(2, '0') + ':' +
        String(now.getSeconds()).padStart(2, '0');

    const clockEls = [document.getElementById('status-time'), document.getElementById('header-clock')];
    clockEls.forEach(el => { if(el) el.innerText = timeStr; });
}

let statusProtected = false;
function updateStatus(msg, isCritical = false) {
    if (statusProtected && !isCritical) return;
    const msgEl = document.getElementById('status-msg');
    if (msgEl) msgEl.innerText = msg;

    if (isCritical) {
        statusProtected = true;
        setTimeout(() => { statusProtected = false; }, 5000);
    }
}

// --- 3. Core Functionality (Excel & Knowledge Base) ---
async function refreshExcelList() {
    updateStatus('正在扫描活跃 Excel 实例...');
    try {
        const files = await eel.list_excel_files()();
        const select = document.getElementById('excel-list');
        if (!select) return;

        select.innerHTML = '<option value="">请选择 Excel 工作簿...</option>';
        files.forEach(file => {
            const option = document.createElement('option');
            option.value = file;
            option.text = file.split('\\').pop();
            select.appendChild(option);
        });
        updateStatus('工作簿列表已同步');
    } catch (e) {
        updateStatus('获取文件列表失败', true);
    }
}

async function loadKnowledgeLists() {
    try {
        const kb = await eel.get_knowledge_base()();
        const processList = document.getElementById('process-kb-list');
        const opList = document.getElementById('op-kb-list');

        [processList, opList].forEach(list => {
            if (!list) return;
            list.innerHTML = '';
            kb.forEach(item => {
                const div = document.createElement('div');
                div.className = 'kb-item-modern';
                div.innerHTML = `<span class="kb-dot"></span><span class="kb-name">${item["工步名称"]}</span>`;
                div.onclick = (e) => fillAIInputFromKB(item, list.id, div);
                list.appendChild(div);
            });
        });
    } catch(e) { console.error("KB Load failed", e); }
}

function fillAIInputFromKB(item, listId, element) {
    document.querySelectorAll(`#${listId} .kb-item-modern`).forEach(el => el.classList.remove('selected'));
    element.classList.add('selected');

    if (listId === 'process-kb-list') {
        document.getElementById('process-gen-out').innerText =
            `【工艺要求】\n${item["工艺要求"]}\n\n【控制方法】\n${item["控制方法"]}`;
    } else {
        document.getElementById('op-gen-out').innerText = item["操作内容"];
        // Also fill the input area if it exists
        const input = document.getElementById('ai-input-content');
        if(input) input.value = item["工步名称"];
    }
}

// --- 4. Special Requirements (Cascading Selection) ---
let allReqData = {};
async function initRequirements() {
    allReqData = await eel.get_special_requirements()();
    const pCombo = document.getElementById('product-combo');
    if(!pCombo) return;

    pCombo.innerHTML = '<option value="">选择产品类别...</option>';
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
    if(!gList || !projCombo) return;

    gList.innerHTML = '';
    projCombo.innerHTML = '<option value="">选择子项目...</option>';

    if (!cat || !allReqData[cat]) return;

    (allReqData[cat]["通用要求"] || []).forEach((r, i) => {
        const div = document.createElement('div');
        div.className = 'req-item';
        div.innerHTML = `<input type="checkbox" class="g-req-cb" value="${r.content}" id="g-r-${i}">
                         <label for="g-r-${i}"><strong>[${r.type}]</strong> ${r.content}</label>`;
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
    if(!pList) return;

    pList.innerHTML = '';
    if (!cat || !projName) return;
    const proj = allReqData[cat]["项目要求"].find(x => x["项目名称"] === projName);
    if (proj) {
        (proj["具体要求"] || []).forEach((r, i) => {
            const div = document.createElement('div');
            div.className = 'req-item';
            div.innerHTML = `<input type="checkbox" class="p-req-cb" value="${r.content}" id="p-r-${i}">
                             <label for="p-r-${i}"><strong>[${r.type}]</strong> ${r.content}</label>`;
            pList.appendChild(div);
        });
    }
}

async function insertRequirements(type) {
    const filePath = document.getElementById('excel-list').value;
    const selector = type === 'general' ? '.g-req-cb:checked' : '.proj-req-cb:checked';
    const selected = Array.from(document.querySelectorAll(selector)).map(cb => cb.value);
    if (!filePath) return alert('请先选择 Excel 文件');
    if (!selected.length) return alert('请先勾选需要插入的条目');

    updateStatus('正在写入 Excel...');
    const result = await eel.write_sop_block(filePath, 'special_requirement', selected.join('\n'))();
    updateStatus(result.message, true);
    alert(result.message);
}

// --- 5. AI & Vision Actions ---
async function handleAIGenerate(blockType, inputId) {
    // If inputId is not provided, use the context-aware default
    const actualInputId = inputId || (blockType === 'operation_content' ? 'ai-input-content' : null);
    const prompt = actualInputId ? document.getElementById(actualInputId).value : "请根据工序名称生成内容";

    const outputId = blockType === 'operation_content' ? 'op-gen-out' : 'process-gen-out';
    const outEl = document.getElementById(outputId);
    if(!outEl) return;

    outEl.innerText = 'AI 正在思考并生成中，请稍候...';
    window.currentOutputId = outputId;

    const result = await eel.ai_generate_content(prompt, blockType)();
    if (result.status === 'error') {
        outEl.innerText = '⚠️ 生成失败: ' + result.message;
    }
}

async function writeAIToExcel(blockType, customOutputId) {
    const outputId = customOutputId || (blockType === 'operation_content' ? 'op-gen-out' : 'process-gen-out');
    const content = document.getElementById(outputId).innerText;
    const filePath = document.getElementById('excel-list').value;

    if (!filePath || !content || content.includes('正在思考')) {
        alert('无效的内容或未选择文件');
        return;
    }

    updateStatus('正在写回 Excel...');
    const res = await eel.write_sop_block(filePath, blockType, content, 'overwrite')();
    updateStatus('应用成功', true);
    alert(res.message);
}

async function handleImageAudit() {
    const filePath = document.getElementById('excel-list').value;
    const out = document.getElementById('vision-output');
    if (!filePath) return alert('请选择文件');

    out.innerText = '>>> 正在截取 Excel 指定区域...\n>>> 正在上传至视觉分析引擎...\n>>> 正在进行合规性比对...';
    const res = await eel.audit_sop_image(filePath)();
    out.innerText = res.result || res.message;
}

// --- 6. List Sync & MBOM ---
async function toggleTableType() {
    const type = document.getElementById('table-type').value;
    const listDiv = document.getElementById('table-data-list');
    listDiv.innerHTML = '<div class="loading-spinner"></div>';

    if (type === 'tool') {
        const tools = await eel.get_tools()();
        listDiv.innerHTML = '';
        tools.forEach((t, i) => {
            const div = document.createElement('div');
            div.className = 'req-item';
            const name = t['名称'] || t['tool_name'];
            div.innerHTML = `<input type="checkbox" class="table-cb" data-json='${JSON.stringify(t)}' id="tool-${i}">
                             <label for="tool-${i}"><strong>${name}</strong> <span class="tag">${t['物料编号'] || '无编号'}</span></label>`;
            listDiv.appendChild(div);
        });
    } else {
        listDiv.innerHTML = '<div class="empty-state">物料数据需要先通过“导入 MBOM”按钮进行加载</div>';
    }
}

async function handleTableSync(mode) {
    const filePath = document.getElementById('excel-list').value;
    const tableId = document.getElementById('table-type').value;
    const selected = Array.from(document.querySelectorAll('.table-cb:checked'))
                          .map(cb => JSON.parse(cb.getAttribute('data-json')));

    if (!filePath || selected.length === 0) return alert('请选择文件和数据项');

    updateStatus('正在同步清单表格...');
    const result = await eel.sync_sop_table(filePath, tableId, selected, mode)();
    alert(result.message);
    updateStatus('就绪');
}

async function importMBOM() {
    updateStatus('正在启动导入流程...');
    const result = await eel.pick_and_process_mbom()();
    if (result.status === 'success') {
        alert(result.message);
        document.getElementById('table-type').value = 'material';
        displayMaterialPreview(result.preview);
    } else {
        updateStatus('导入被取消或失败');
    }
}

function displayMaterialPreview(preview) {
    const listDiv = document.getElementById('table-data-list');
    listDiv.innerHTML = '';
    preview.forEach((item, i) => {
        const div = document.createElement('div');
        div.className = 'req-item';
        div.innerHTML = `<input type="checkbox" class="table-cb" data-json='${JSON.stringify(item)}' id="mat-${i}">
                         <label for="mat-${i}"><strong>${item.name}</strong> [${item.code}] (x${item.qty})</label>`;
        listDiv.appendChild(div);
    });
}

// --- 7. Utility Metadata Tools ---
async function handlePageUpdate() {
    const filePath = document.getElementById('excel-list').value;
    if (!filePath) return alert('请选择文件');
    updateStatus('正在重算页码...');
    const res = await eel.update_sop_page_numbers(filePath)();
    alert(res.message);
    updateStatus('页码已刷新', true);
}

async function handleCatalogGenerate() {
    const filePath = document.getElementById('excel-list').value;
    if (!filePath) return alert('请选择文件');
    updateStatus('正在构建全书目录...');
    const res = await eel.generate_sop_catalog(filePath)();
    alert(res.message);
}

async function handleMetadataUpdate(type) {
    const val = document.getElementById(`new-${type.replace('_','-')}`).value;
    const filePath = document.getElementById('excel-list').value;
    if (!filePath || !val) return alert('输入不完整');

    updateStatus(`正在修改${type}...`);
    const res = await eel.update_sop_metadata(filePath, type, val)();
    alert(res.message);
}

// --- 8. PDF Rules ---
async function loadPDFRules() {
    const pdfs = await eel.get_pdf_rules()();
    const listDiv = document.getElementById('pdf-rules-container');
    if(!listDiv) return;
    listDiv.innerHTML = '';
    pdfs.forEach((pdf, i) => {
        const row = document.createElement('div');
        row.className = 'req-item';
        row.innerHTML = `
            <input type="checkbox" class="pdf-cb" value="${pdf}" id="pdf-${i}">
            <label for="pdf-${i}" class="pdf-link">📄 ${pdf}</label>
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

    updateStatus('写入 PDF 引用标题...');
    const res = await eel.write_sop_block(filePath, 'special_requirement', selected.join('\n'))();
    alert(res.message);
}

// --- 9. Modal Data Editor ---
let currentEditingKey = null;

async function openDataEditor(key) {
    currentEditingKey = key;
    const titleMap = {
        'knowledge_base': '工步知识库编辑器 (Step Knowledge Base)',
        'prompts': 'AI 提示词设置 (Prompt Engineering)',
        'special_requirements': '工艺要求库编辑器 (Process Standards)',
        'templates': 'Excel 坐标映射 (Advanced Templates)'
    };

    document.getElementById('modal-title').innerText = titleMap[key] || 'Data Editor';
    const data = await eel.get_config(key)();
    document.getElementById('json-editor-area').value = JSON.stringify(data, null, 4);
    document.getElementById('modal-editor').style.display = 'block';
}

function closeModal() {
    document.getElementById('modal-editor').style.display = 'none';
}

async function saveModalData() {
    const rawValue = document.getElementById('json-editor-area').value;
    try {
        const jsonData = JSON.parse(rawValue);
        updateStatus(`正在写回 ${currentEditingKey}...`);

        const success = await eel.save_config(currentEditingKey, jsonData)();
        if (success) {
            alert('保存成功！新参数已立即注入内存。');
            closeModal();
            if (currentEditingKey === 'knowledge_base') loadKnowledgeLists();
            if (currentEditingKey === 'special_requirements') initRequirements();
        }
    } catch (e) {
        alert('JSON 解析失败，请检查格式。');
    }
}

// --- 10. Initialization ---
window.onload = () => {
    refreshExcelList();
    loadPDFRules();
    initRequirements();
    loadKnowledgeLists();

    // Clock & Status logic
    setInterval(updateTime, 1000);
    updateTime();

    // Load settings from config for display
    (async () => {
        const config = await eel.get_config('settings')();
        if (config) {
            const ai = config.deepseek_config || {};
            if(document.getElementById('setting-ai-base')) {
                document.getElementById('setting-ai-base').value = ai.api_base || '';
                document.getElementById('setting-ai-key').value = ai.api_key || '';
                document.getElementById('setting-ai-model').value = ai.model || '';
                document.getElementById('setting-catalog-pos').value = config.catalog_insert_position || 2;
                document.getElementById('setting-guide-type').value = config.guide_type || 'default';
            }
        }
    })();
};

// Eel Expose for Streaming AI
eel.expose(on_ai_chunk);
function on_ai_chunk(chunk, full) {
    const id = window.currentOutputId;
    const el = document.getElementById(id);
    if (el) {
        el.innerText = full;
        el.scrollTop = el.scrollHeight; // Auto scroll
    }
}
