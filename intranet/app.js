let myRole='';let myUser='';let myTeam='';let myCargo='';let myRhAccess=false;let currentView='dashboard';let allFolders=[];let permList=[];

// SISTEMA DE NOTIFICAÇÕES (TOASTS)
function showToast(msg, type='success') {
    const color = type === 'success' ? '#66cc00' : '#ff4444';
    const toast = document.createElement('div');
    toast.style.cssText = `position:fixed;bottom:28px;right:28px;background:rgba(8,13,9,0.97);color:#d0dcd2;border:1px solid rgba(255,255,255,0.08);border-left:3px solid ${color};padding:14px 20px;border-radius:12px;z-index:999999;font-weight:500;box-shadow:0 16px 40px rgba(0,0,0,0.8),0 0 0 1px rgba(0,0,0,0.5);font-size:13px;display:flex;align-items:center;gap:10px;transition:0.3s;opacity:0;transform:translateY(8px);backdrop-filter:blur(20px);`;
    toast.innerHTML = `<span style="background:${color};color:#000;width:24px;height:24px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-size:14px;">${type==='success'?'✔':'✖'}</span> ${msg}`;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '1'; toast.style.transform = 'translateY(0)'; }, 50);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateY(20px)'; setTimeout(()=>toast.remove(), 500); }, 3500);
}

function logAction(action,detail){try{navigator.sendBeacon("/api/logs",new Blob([JSON.stringify({action,detail})],{type:"application/json"}));}catch(e){try{fetch("/api/logs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action,detail}),keepalive:true});}catch(e2){}}}
async function init(){
    injectModals(); fixLinks();
    try{
        const me=await(await fetch('/api/me')).json();myRole=me.role;myUser=me.user;myTeam=me.profile?.team||'';myCargo=me.profile?.cargo||'';myRhAccess=me.profile?.rhAccess===true;
        document.getElementById('user-info').textContent='Olá, '+(me.user==='petterson'?'Petterson':me.user);

        const pModal = document.getElementById('profile-modal');
        if(pModal) {
            pModal.innerHTML = `
            <div class="modal-content">
                <img src="${me.profile?.photo || 'https://ui-avatars.com/api/?name='+me.user+'&background=0D8ABC&color=fff'}" style="width:100px;height:100px;border-radius:50%;object-fit:cover;border:2px solid #66cc00;margin:0 auto 20px auto;display:block;" id="profile-preview">
                <h3 style="text-align:center;color:#fff;margin-bottom:25px;font-size:18px;">Meu Perfil</h3>
                <label style="color:#aaa;font-size:12px;display:block;margin-bottom:5px;">Trocar Foto de Perfil</label>
                <input type="file" id="profile-photo-input" accept="image/*">
                <label style="color:#aaa;font-size:12px;display:block;margin-top:10px;margin-bottom:5px;">Data de Aniversário</label>
                <input type="date" id="profile-bday" value="${me.profile?.birthday || ''}">
                <label style="color:#aaa;font-size:12px;display:block;margin-top:10px;margin-bottom:5px;">Meu Time</label>
                <input type="text" value="${me.profile?.team || 'N/A'}" disabled>
                <div style="margin-top:25px;">
                    <button onclick="document.getElementById('profile-modal').classList.remove('active')">Cancelar</button>
                    <button onclick="saveProfileData(event)">Salvar Perfil</button>
                </div>
            </div>`;
        }
        const headerPhoto = document.getElementById('header-photo'); headerPhoto.src = me.profile?.photo || 'https://ui-avatars.com/api/?name='+me.user+'&background=1a5c35&color=66cc00&bold=true'; headerPhoto.style.display='block';

        const menuLinks = document.querySelectorAll('header > div:last-child a');
        if(menuLinks.length >= 2) {
            menuLinks[0].onclick = (e) => { e.preventDefault(); document.getElementById('profile-modal').classList.add('active'); };
            menuLinks[1].onclick = (e) => { e.preventDefault(); window.location.href = 'https://auth.segredosdaaudiencia.com.br/logout'; };
        }

        allFolders=await(await fetch('/api/folders')).json();
        permList=[];
        allFolders.forEach(f=>{
            permList.push({val:f.name,label:f.name,isSub:false});
            f.categories.forEach(c=>{ permList.push({val:`${f.name}/${c.name}`,label:`↳ ${c.name}`,isSub:true}); });
        });
        renderFolders(allFolders);

        if(['master','admin','anjo-caido'].includes(myRole)){
            const navAdm=document.getElementById('nav-admin');
            if(navAdm)navAdm.style.display='flex';
        }
        if(['master','anjo-caido'].includes(myRole)){const navLogs=document.getElementById('nav-logs');if(navLogs)navLogs.style.display='flex';}
        if(['master','anjo-caido','admin'].includes(myRole)||(myCargo==='Lider Recursos Humanos'||myRhAccess)||myRhAccess){const navRh=document.getElementById('nav-rh');if(navRh)navRh.style.display='flex';}
        {const isLiderCargo=myCargo&&(myCargo.startsWith('Lider')||myCargo==='Diretoria');if(['master','anjo-caido','admin'].includes(myRole)||myRhAccess||isLiderCargo){const navLid=document.getElementById('nav-lideres');if(navLid)navLid.style.display='flex';}}
        loadNotices(); loadFiles(); loadFerias(); loadAllAprovadas();
    }catch(e){console.error(e);}
}

function injectModals() {
    if(!document.getElementById('custom-notice-modal')) {
        document.body.insertAdjacentHTML('beforeend', `
        <div id="custom-notice-modal" class="modal">
            <div class="modal-content" style="width:400px;text-align:left;">
                <h3 style="color:#fff;margin-bottom:15px;font-size:16px;">Novo Aviso no Mural</h3>
                <textarea id="custom-notice-text" placeholder="Digite o aviso para a equipe..." style="width:100%;height:100px;background:#050505;border:1px solid #333;color:#fff;padding:12px;border-radius:8px;font-family:inherit;font-size:13px;outline:none;resize:none;margin-bottom:15px;"></textarea>
                <div style="text-align:right;">
                    <button onclick="document.getElementById('custom-notice-modal').classList.remove('active')" style="background:transparent;color:#aaa;border:1px solid #444;padding:10px 15px;border-radius:6px;cursor:pointer;margin-right:10px;">Cancelar</button>
                    <button onclick="confirmAddNotice()" style="background:linear-gradient(135deg, #66cc00, #4d9900);color:#000;border:none;padding:10px 20px;border-radius:6px;font-weight:bold;cursor:pointer;">Publicar</button>
                </div>
            </div>
        </div>`);
    }
    const profileModal = document.querySelector('.modal:not(#custom-notice-modal)');
    if(profileModal) profileModal.id = 'profile-modal';
    else document.body.insertAdjacentHTML('beforeend', `<div id="profile-modal" class="modal"></div>`);
    window.onclick = function(event) { if (event.target.classList.contains('modal')) event.target.classList.remove('active'); }
}

function fixLinks() {
    const linksGrid = document.querySelector('.links-grid');
    if(linksGrid) {
        linksGrid.innerHTML = `
        <a href="https://app.iuli.com.br" target="_blank" class="link-card">
            <div style="width:50px;text-align:center"><img src="/Imagens/logo-iuli-branco.png" style="width:40px;height:40px;object-fit:contain;border-radius:8px"></div>
            <div><strong style="display:block;color:#fff;font-size:14px">IULI</strong><span style="color:#aaa;font-size:11px">Sistema financeiro e notas</span></div>
        </a>
        <a href="https://sda-club.ticto.club/signin" target="_blank" class="link-card">
            <div style="font-size:28px;width:50px;text-align:center">🎓</div>
            <div><strong style="display:block;color:#fff;font-size:14px">SDA CLUB</strong><span style="color:#aaa;font-size:11px">Portal de treinamentos</span></div>
        </a>
        <a href="https://instagram.com/segredosdaaudiencia" target="_blank" class="link-card">
            <div style="width:50px;text-align:center"><img src="/Imagens/icone-instagram.png" style="width:40px;height:40px;object-fit:contain;border-radius:8px"></div>
            <div><strong style="display:block;color:#fff;font-size:14px">Instagram</strong><span style="color:#aaa;font-size:11px">@segredosdaaudiencia</span></div>
        </a>
        <a href="https://linkedin.com/company/segredosdaaudiencia" target="_blank" class="link-card">
            <div style="width:50px;text-align:center"><img src="/Imagens/icone-likedin.png" style="width:40px;height:40px;object-fit:contain;border-radius:8px"></div>
            <div><strong style="display:block;color:#fff;font-size:14px">LinkedIn</strong><span style="color:#aaa;font-size:11px">Página da Empresa</span></div>
        </a>
        <a href="https://facebook.com/segredosdaaudiencia" target="_blank" class="link-card">
            <div style="width:50px;text-align:center"><img src="/Imagens/icone-facebook.png" style="width:40px;height:40px;object-fit:contain;border-radius:8px"></div>
            <div><strong style="display:block;color:#fff;font-size:14px">Facebook</strong><span style="color:#aaa;font-size:11px">Página Oficial</span></div>
        </a>
        <a href="https://youtube.com/segredosdaaudiencia" target="_blank" class="link-card">
            <div style="width:50px;text-align:center"><img src="/Imagens/icone-youtube.png" style="width:40px;height:40px;object-fit:contain;border-radius:8px"></div>
            <div><strong style="display:block;color:#fff;font-size:14px">YouTube</strong><span style="color:#aaa;font-size:11px">Canal Oficial</span></div>
        </a>
        <a href="https://bernardocoelho.pixieset.com/" target="_blank" class="link-card">
            <div style="font-size:28px;width:50px;text-align:center">📸</div>
            <div><strong style="display:block;color:#fff;font-size:14px">Fotos SDA e Samuel</strong><span style="color:#aaa;font-size:11px">Site Bernardo Coelho com fotos de eventos</span></div>
        </a>`;
    }
}

window.openNoticeModal = function() {
    document.getElementById('custom-notice-text').value = '';
    document.getElementById('custom-notice-modal').classList.add('active');
};
window.confirmAddNotice = async function() {
    const text = document.getElementById('custom-notice-text').value;
    if(!text.trim()) return showToast('O aviso não pode estar vazio!', 'error');
    try {
        const res = await fetch('/api/notices',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
        if(res.ok) { showToast('Aviso publicado com sucesso!', 'success'); logAction('Aviso publicado',text.substring(0,80)); document.getElementById('custom-notice-modal').classList.remove('active'); loadNotices(); }
        else throw new Error();
    } catch(e) { showToast('Erro ao publicar o aviso.', 'error'); }
};

// BYPASS DE DELETE NO NGINX (USANDO POST PARA APAGAR)
window.delNotice = async function(id) {
    if(!confirm('Deseja realmente apagar este aviso?')) return;
    try {
        const res = await fetch(`/api/notices/delete/${id}`,{method:'POST'});
        if(res.ok) { showToast('Aviso removido do mural!', 'success'); loadNotices(); }
        else throw new Error();
    } catch(e) { showToast('Falha ao remover o aviso.', 'error'); }
};

let allNotices=[];
async function loadNotices(){
    const n=await(await fetch('/api/notices')).json();
    allNotices=n;
    const canNotice=['master','anjo-caido'].includes(myRole)||myTeam==='Recursos Humanos'||myTeam==='Diretoria';
    const btnAdd=canNotice?`<button onclick="openNoticeModal()" style="width:100%;margin-bottom:15px;background:rgba(102,204,0,0.05);border:1px dashed #66cc00;color:#66cc00;padding:12px;border-radius:10px;font-weight:600;cursor:pointer;">+ Adicionar Novo Aviso</button>`:'';
    document.getElementById('notices-list').innerHTML=btnAdd+n.map(x=>`<div class="notice-card" style="position:relative;background:rgba(255,255,255,0.03);padding:15px;border-radius:10px;border-left:4px solid #66cc00;margin-bottom:12px;">${x.text} <br><small style="color:#777;font-size:11px;margin-top:5px;display:block">${x.author} - ${x.date}</small> ${canNotice?`<button onclick="delNotice(${x.id})" style="position:absolute;top:10px;right:10px;background:none;border:none;color:#ff4444;cursor:pointer;font-weight:bold;font-size:14px">X</button>`:''}</div>`).join('');
}

// COMPRESSOR DE IMAGEM NO NAVEGADOR (BYPASS NGINX PAYLOAD SIZE)
window.saveProfileData = async function(event) {
    const bday = document.getElementById('profile-bday').value;
    const fileInput = document.getElementById('profile-photo-input');
    const btn = event.target; const oldText = btn.innerText;
    btn.innerText = 'Salvando...'; btn.disabled = true;

    const doSave = async (data) => {
        try {
            const res = await fetch('/api/profile', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            if(res.ok) { showToast('Perfil salvo com sucesso!', 'success'); setTimeout(() => window.location.reload(), 1500); } 
            else throw new Error();
        } catch(e) { showToast('Falha ao salvar o perfil.', 'error'); btn.innerText = oldText; btn.disabled = false; }
    };

    if(fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                const canvas = document.createElement('canvas');
                let w = img.width; let h = img.height; const max = 400; // REDUZ A IMAGEM PARA 400px (FICA LEVE E RAPIDA)
                if(w > h) { if(w > max) { h *= max / w; w = max; } } else { if(h > max) { w *= max / h; h = max; } }
                canvas.width = w; canvas.height = h;
                const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0, w, h);
                doSave({ birthday: bday, photo: canvas.toDataURL('image/jpeg', 0.8) }); // CONVERTE PRA JPEG LEVE
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(fileInput.files[0]);
    } else { doSave({ birthday: bday }); }
};

function setupAdminForm(){
    const adminSec=document.querySelector('.admin-section');
    if(adminSec && !adminSec.dataset.init){
        adminSec.dataset.init='1';
        adminSec.innerHTML=`<div class="sec-label" style="margin-top:4px;">Novo Usuário</div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:15px;background:rgba(255,255,255,0.02);padding:24px;border-radius:12px;border:1px solid rgba(255,255,255,0.07);margin-bottom:36px">
            <div style="display:flex;flex-direction:column"><label style="color:#aaa;font-size:12px;margin-bottom:5px">Usuário</label><input type="text" id="new-user" style="padding:11px 12px;border-radius:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;outline:none;transition:border-color .15s;"></div>
            <div style="display:flex;flex-direction:column"><label style="color:#aaa;font-size:12px;margin-bottom:5px">Email</label><input type="email" id="new-email" style="padding:11px 12px;border-radius:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;outline:none;transition:border-color .15s;"></div>
            <div style="display:flex;flex-direction:column"><label style="color:#aaa;font-size:12px;margin-bottom:5px">Senha</label><input type="password" id="new-pass" placeholder="Em branco p/ gerar auto" style="padding:11px 12px;border-radius:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;outline:none;transition:border-color .15s;"></div>
            <div style="display:flex;flex-direction:column"><label style="color:#aaa;font-size:12px;margin-bottom:5px">Time</label><select id="new-team" style="padding:11px 12px;border-radius:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;outline:none;transition:border-color .15s;"><option value="Atenção">Atenção</option><option value="Comercial">Comercial</option><option value="Recursos Humanos">Recursos Humanos</option><option value="Administrativo">Administrativo</option><option value="Concierge">Concierge</option><option value="Suporte">Suporte</option><option value="Eventos">Eventos</option><option value="Diretoria">Diretoria</option></select></div>
            <div style="display:flex;flex-direction:column"><label style="color:#aaa;font-size:12px;margin-bottom:5px">Nível</label><select id="new-role" style="padding:11px 12px;border-radius:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;outline:none;transition:border-color .15s;"><option value="ouvinte">Ouvinte</option><option value="admin">Admin</option><option value="master">Master</option></select></div>
            <div style="display:flex;flex-direction:column"><label style="color:#aaa;font-size:12px;margin-bottom:5px">Cargo</label><select id="new-cargo" style="padding:11px 12px;border-radius:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;outline:none;transition:border-color .15s;"><option value="">-- Sem cargo --</option><optgroup label="Lideranca"><option value="Lider Comercial">Lider Comercial</option><option value="Lider Recursos Humanos">Lider Recursos Humanos</option><option value="Lider Marketing">Lider Marketing</option><option value="Lider Concierge">Lider Concierge</option><option value="Lider Financeiro">Lider Financeiro</option><option value="Lider Eventos">Lider Eventos</option><option value="Diretoria">Diretoria</option></optgroup><optgroup label="Analistas"><option value="Analista Comercial">Analista Comercial</option><option value="Analista Recursos Humanos">Analista Recursos Humanos</option><option value="Analista Marketing">Analista Marketing</option><option value="Analista Financeiro">Analista Financeiro</option><option value="Analista Eventos">Analista Eventos</option></optgroup></select></div><div style="display:flex;flex-direction:column;grid-column:span 2"><label style="color:#aaa;font-size:12px;margin-bottom:5px">Acesso a Pastas</label><div id="new-folder-container" style="padding:2px 0;min-height:28px;"></div></div>
            <div style="grid-column:span 4;text-align:right;"><button onclick="createUser()" style="background:linear-gradient(135deg, #66cc00, #4d9900);color:#000;padding:12px 30px;border-radius:8px;font-weight:700;border:none;cursor:pointer;">Criar Usuário</button></div>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
          <div class="sec-label" style="margin-bottom:0;">Usuários Cadastrados</div>
          <span id="user-count" style="color:#3a5040;font-size:11px;"></span>
        </div>
        <div style="display:flex;gap:8px;margin-bottom:14px;">
          <div style="position:relative;flex:1;">
            <span style="position:absolute;left:9px;top:50%;transform:translateY(-50%);color:#3a5040;font-size:12px;pointer-events:none;">&#128269;</span>
            <input id="user-search" type="text" placeholder="Buscar usuário..." oninput="filterUsers()" style="width:100%;box-sizing:border-box;padding:8px 10px 8px 28px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;border-radius:8px;font-size:12px;outline:none;font-family:inherit;">
          </div>
          <select id="filter-team" onchange="filterUsers()" style="width:160px;flex-shrink:0;padding:8px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;border-radius:8px;font-size:12px;outline:none;font-family:inherit;">
            <option value="">Todos os times</option>
            <option value="Atenção">Atenção</option><option value="Comercial">Comercial</option><option value="Recursos Humanos">RH</option><option value="Administrativo">Administrativo</option><option value="Concierge">Concierge</option><option value="Suporte">Suporte</option><option value="Eventos">Eventos</option><option value="Diretoria">Diretoria</option>
          </select>
          <select id="filter-role" onchange="filterUsers()" style="width:140px;flex-shrink:0;padding:8px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;border-radius:8px;font-size:12px;outline:none;font-family:inherit;">
            <option value="">Todos os níveis</option>
            <option value="ouvinte">Ouvinte</option><option value="admin">Admin</option><option value="master">Master</option><option value="anjo-caido">Anjo Caído</option>
          </select>
        </div>
        <div id="users-tbody" class="user-list"></div>`;
        document.getElementById('new-folder-container').innerHTML=['master','anjo-caido'].includes(myRole)?'<div class="folder-chips">'+permList.map(p=>`<span class="folder-chip${p.isSub?' sub':''}" data-val="${p.val}" onclick="this.classList.toggle('active')">${p.label}</span>`).join('')+'</div>':'<small style="color:#555;font-size:11px;">Sem permissão</small>';
    }
}
function renderFolders(folders){ const grid=document.getElementById('folders-grid');grid.innerHTML=''; folders.forEach(f=>{let sub='';if(f.hasMainIndex)sub+=`<a class="subfolder-link" onclick="logAction('Painel acessado',this.getAttribute('href').replace('/viewer.html?url=',''))" href="/viewer.html?url=/${f.name}/index.html">📄 Principal</a>`;f.categories.forEach(c=>{if(c.isProject){sub+=`<a class="subfolder-link" onclick="logAction('Painel acessado',this.getAttribute('href').replace('/viewer.html?url=',''))" href="/viewer.html?url=${c.path}/index.html">📊 ${c.name}</a>`;}else if(c.children&&c.children.length>0){sub+=`<span class="subfolder-link" style="cursor:default;opacity:0.7">📁 ${c.name}</span>`;c.children.forEach(ch=>{sub+=`<a class="subfolder-link" onclick="logAction('Painel acessado',this.getAttribute('href').replace('/viewer.html?url=',''))" href="/viewer.html?url=${ch.path}/index.html" style="padding-left:20px;font-size:11px;">${ch.isProject?'📊':'└─'} ${ch.name}</a>`;});}else{sub+=`<a class="subfolder-link" onclick="logAction('Painel acessado',this.getAttribute('href').replace('/viewer.html?url=',''))" href="/viewer.html?url=${c.path}/index.html">📁 ${c.name}</a>`;}});grid.innerHTML+=`<div class="folder-card"><div style="font-size:30px">📁</div><div style="font-weight:600;color:#fff;margin-top:5px;">${f.name}</div><div class="subfolders">${sub||'Vazio'}</div></div>`;}); }
let allUsers=[];
window.filterUsers=function(){
    const q=(document.getElementById('user-search')?.value||'').toLowerCase().trim();
    const ft=(document.getElementById('filter-team')?.value||'');
    const fr=(document.getElementById('filter-role')?.value||'');
    const tbody=document.getElementById('users-tbody');if(!tbody)return;
    const filtered=allUsers.filter(u=>{
        const name=(u.usernameDisplay||u.username||'').toLowerCase();
        const team=(u.team||'').toLowerCase();
        if(q&&!name.includes(q)&&!team.includes(q.toLowerCase()))return false;
        if(ft&&u.team!==ft)return false;
        if(fr){
            const role=u.role||'';
            if(fr==='anjo-caido'&&role!=='anjo-caido'&&u.username.toLowerCase()!=='petterson')return false;
            if(fr!=='anjo-caido'&&role!==fr)return false;
        }
        return true;
    });
    const countEl=document.getElementById('user-count');
    if(countEl)countEl.textContent=filtered.length+' de '+allUsers.length;
    tbody.innerHTML='';
    filtered.forEach(u=>renderUserCard(u,tbody));
};
function renderUserCard(u,tbody){
    const isTargetDeus=u.username==='saulorogerio'; const isTargetAnjo=(u.role==='anjo-caido' || u.username.toLowerCase()==='petterson');
    const canEdit=(myRole==='master')||(!isTargetDeus && !isTargetAnjo)||(myUser===u.username);
    let roleSel=''; if(isTargetDeus) roleSel='<span style="background:rgba(255,204,0,0.15);color:#ffcc00;border:1px solid rgba(255,204,0,0.35);padding:4px 10px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:.05em;">DEUS</span>'; else if(isTargetAnjo) roleSel='<span style="background:rgba(0,120,255,0.1);color:#4da6ff;border:1px solid rgba(0,120,255,0.3);padding:4px 10px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:.05em;">Anjo Caído</span>'; else roleSel=`<select id="role-${u.username}" style="background:rgba(255,255,255,0.05);color:#d0dcd2;border:1px solid rgba(255,255,255,0.1);padding:6px 10px;border-radius:7px;font-size:11px;"><option value="ouvinte" ${u.role==='ouvinte'?'selected':''}>Ouvinte</option><option value="admin" ${u.role==='admin'?'selected':''}>Admin</option><option value="master" ${u.role==='master'?'selected':''}>Master</option></select>`;
    const btnDel=(myRole==='master' && !isTargetDeus)?`<button onclick="delUser('${u.username}')" style="background:rgba(255,0,0,0.1);color:#ff4444;border:1px solid #ff4444;padding:6px 10px;border-radius:6px;margin-left:8px;cursor:pointer;">X</button>`:(!isTargetDeus && !isTargetAnjo && myRole==='anjo-caido')?`<button onclick="delUser('${u.username}')" style="background:rgba(255,0,0,0.1);color:#ff4444;border:1px solid #ff4444;padding:6px 10px;border-radius:6px;margin-left:8px;cursor:pointer;">X</button>`:'';
    const btnSave=canEdit?`<button onclick="save('${u.username}')" style="background:rgba(102,204,0,0.15);border:1px solid rgba(102,204,0,0.35);padding:6px 14px;border-radius:6px;color:#66cc00;font-weight:600;cursor:pointer;font-size:11px;transition:all .15s;">Salvar</button>`:`<button disabled style="background:transparent;color:#2a3a2a;border:1px solid rgba(255,255,255,0.05);padding:6px 14px;border-radius:6px;font-size:11px;">Bloqueado</button>`;
    const cargoSel=cargoSelectHtml(u.username,u.cargo||'',(['master','anjo-caido'].includes(myRole))&&canEdit&&!isTargetDeus&&!isTargetAnjo);
    const fBox=(['master','anjo-caido'].includes(myRole)&&canEdit)?`<div id="f-${u.username}" class="folder-chips">`+permList.map(p=>`<span class="folder-chip${p.isSub?' sub':''}${(u.folders||[]).includes(p.val)?' active':''}" data-val="${p.val}" onclick="this.classList.toggle('active')">${p.label}</span>`).join('')+`</div>`:`<div style="font-size:11px;color:#888;">${u.folders?.length>0?u.folders.join(', '):'Sem acessos'}</div>`;
    tbody.innerHTML+=`<div class="user-card"><div class="user-card-top"><div class="user-card-name"><strong>${u.usernameDisplay}</strong><span class="user-card-team">${u.team||'--'}</span></div><div class="user-card-controls">${roleSel}${cargoSel}</div><div class="user-card-actions">${btnSave}${btnDel}</div></div><div class="user-card-folders">${fBox}</div></div>`;
}
async function loadTable(){
    const users=await(await fetch('/api/users')).json();
    allUsers=users;
    const countEl=document.getElementById('user-count');
    if(countEl)countEl.textContent=users.length+' de '+users.length;
    const tbody=document.getElementById('users-tbody'); tbody.innerHTML='';
    users.forEach(u=>{
        renderUserCard(u,tbody);
    });
}
window.save = async function(t){
    const roleEl=document.getElementById(`role-${t}`); let role=roleEl?roleEl.value:(t==='saulorogerio'?'master':'anjo-caido');const cargoEl=document.getElementById('cargo-'+t);const cargo=cargoEl?cargoEl.value:undefined;
    let folders=[]; const fDiv=document.getElementById(`f-${t}`);if(fDiv) fDiv.querySelectorAll('.folder-chip.active').forEach(chip=>folders.push(chip.dataset.val));
    try{ const res=await fetch(`/api/users/${t}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({role,folders,cargo})}); if(res.ok){showToast('Permissões salvas!'); loadTable();}else throw new Error(); }catch(e){showToast('Erro ao salvar permissões.','error');}
};
// BYPASS DE DELETE NO NGINX PARA USUARIOS (USANDO POST)
window.delUser = async function(t){
    if(!confirm('Deseja apagar a conta '+t+'?')) return;
    try{ const res=await fetch(`/api/users/delete/${t}`,{method:'POST'}); if(res.ok){showToast('Usuário apagado!'); loadTable();}else throw new Error();}catch(e){showToast('Erro ao apagar.','error');}
};
window.createUser = async function(){
    const username=document.getElementById('new-user').value; const email=document.getElementById('new-email').value; const password=document.getElementById('new-pass').value; const team=document.getElementById('new-team').value; const role=document.getElementById('new-role').value;const cargo=document.getElementById('new-cargo')?.value||'';
    let folders=[]; document.querySelectorAll('#new-folder-container .folder-chip.active').forEach(chip=>folders.push(chip.dataset.val));
    if(!username||!email) return showToast('Preencha usuário e email!','error');
    try{ const res=await fetch('/api/add-user',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username,email,password,role,team,folders,cargo})}); if(res.ok){showToast('Usuário criado!');logAction('Usuario criado',username);loadTable();document.getElementById('new-user').value='';document.getElementById('new-email').value='';}else throw new Error();}catch(e){showToast('Erro ao criar usuário.','error');}
};
async function loadFiles(){
    const f=await(await fetch('/api/files')).json();let html='';
    if(['master','admin','anjo-caido'].includes(myRole)){ html+=`<div style="padding:15px;border-bottom:1px solid #222;display:flex;gap:15px;align-items:center;background:rgba(0,0,0,0.2);border-radius:10px;margin-bottom:10px;"><input type="file" id="file-in" style="color:#ccc;font-size:12px;flex:1;"><button onclick="uploadFile()" style="background:#66cc00;color:#000;border:none;padding:8px 15px;border-radius:6px;font-weight:bold;cursor:pointer;">Enviar</button></div>`; }
    html+=f.map(x=>`<div style="padding:12px 15px;border-bottom:1px solid #222;"><a href="/Central_Arquivos/${x.name}" target="_blank" style="color:#66cc00;text-decoration:none;font-size:13px;font-weight:500;">📄 ${x.name}</a></div>`).join(''); document.getElementById('files-list').innerHTML=html;
}
window.uploadFile = async function(){
    const fileIn=document.getElementById('file-in');if(!fileIn.files[0]) return showToast('Selecione um arquivo.','error');
    const fd=new FormData();fd.append('file',fileIn.files[0]); const btn=fileIn.nextElementSibling; btn.innerText='Enviando...';btn.disabled=true;
    try{ const res=await fetch('/api/files',{method:'POST',body:fd}); if(res.ok){showToast('Arquivo na Central!');logAction('Arquivo enviado',fileIn.files[0]?.name||'');loadFiles();}else throw new Error();}catch(e){showToast('Erro no envio.','error');} btn.innerText='Enviar';btn.disabled=false;
};
window.toggleAdmin = function(){document.getElementById('admin-section').classList.toggle('visible');};


// ===== NAV / SWITCH VIEW =====

// ===== SISTEMA DE FOLGAS =====
let allFolgas=[];
let allFeriasAprv=[];
let allFolgasAprv=[];
let folgasCalMonth=new Date().getMonth();
let folgasCalYear=new Date().getFullYear();

async function loadFolgas(){
    try{allFolgas=await(await fetch('/api/folgas')).json();renderFolgasWidget();updateBell();loadAllAprovadas();}
    catch(e){console.error('loadFolgas:',e);}
}

function renderFolgasWidget(){
    var container=document.getElementById('folgas-main-view');
    if(!container)return;
    var isMaster=['master','anjo-caido'].includes(myRole);
    var isLider=!!(myCargo&&(myCargo.startsWith('Lider')||myCargo==='Diretoria'))||myRhAccess;
    var pendentes=allFolgas.filter(function(f){
        if(f.status!=='pendente')return false;
        if(isMaster)return true;
        return f.liderDireto===myUser||(myCargo==='Lider Recursos Humanos'||myRhAccess);
    });
    var aprovadas=allFolgasAprv.length>0?allFolgasAprv:allFolgas.filter(function(f){return f.status==='aprovado';});
    var minhas=allFolgas.filter(function(f){return f.user===myUser;});
    var today=new Date();today.setHours(0,0,0,0);
    var upcoming=aprovadas.filter(function(f){return new Date(f.endDate+'T23:59:59')>=today;}).sort(function(a,b){return new Date(a.startDate)-new Date(b.startDate);}).slice(0,5);

    window._openFolgasModal=function(){document.getElementById('folgas-modal').classList.add('active');};
    var html='<button onclick="window._openFolgasModal()" style="width:100%;margin-bottom:18px;background:rgba(102,204,0,0.08);border:1px solid rgba(102,204,0,0.3);color:#66cc00;padding:11px;border-radius:9px;font-weight:600;cursor:pointer;font-size:13px;letter-spacing:.02em;">+ Solicitar Folga</button>';
    html+=buildCalendar(aprovadas,folgasCalYear,folgasCalMonth,'folgasCalPrev','folgasCalNext');

    if(upcoming.length>0){
        html+='<div class="sec-label" style="margin-top:16px;margin-bottom:10px;">Próximas Folgas Aprovadas</div>';
        upcoming.forEach(function(f){
            var dStr=f.startDate===f.endDate?fmtDate(f.startDate):fmtDate(f.startDate)+' → '+fmtDate(f.endDate);
            html+='<div style="background:rgba(102,204,0,0.05);border-left:3px solid #66cc00;border-radius:6px;padding:8px 10px;margin-bottom:6px;"><div style="display:flex;justify-content:space-between;align-items:center;"><strong style="color:#d0dcd2;font-size:12px">'+f.user+'</strong><div style="display:flex;align-items:center;gap:6px;">'+(f.cargo?'<span style="color:#555;font-size:10px">'+f.cargo+'</span>':'')+(isMaster||isLider?'<button onclick="cancelarFolga('+f.id+')" style="background:rgba(255,100,0,0.1);border:1px solid rgba(255,100,0,0.3);color:#ff9944;cursor:pointer;font-size:10px;padding:2px 6px;border-radius:4px;font-family:inherit;">Cancelar</button>':'')+'</div></div><div style="color:#aaa;font-size:11px;margin-top:2px;">'+dStr+'</div></div>';
        });
    }

    var minhasRec=minhas.sort(function(a,b){return b.id-a.id;}).slice(0,5);
    if(minhasRec.length>0){
        html+='<div class="sec-label" style="margin-top:16px;margin-bottom:10px;">Minhas Solicitações</div>';
        minhasRec.forEach(function(f){
            var sc=f.status==='aprovado'?'#66cc00':f.status==='rejeitado'?'#ff4444':f.status==='cancelado'?'#888':'#ffcc00';
            var sl=f.status==='aprovado'?'✓ Aprovado':f.status==='rejeitado'?'✗ Recusado':f.status==='cancelado'?'✕ Cancelado':'⏳ Pendente';
            var dStr=f.startDate===f.endDate?fmtDate(f.startDate):fmtDate(f.startDate)+' → '+fmtDate(f.endDate);
            var reasonHtml=(f.status==='rejeitado'&&f.rejectionReason)?'<div style="color:#555;font-size:10px;margin-top:2px;font-style:italic;">Motivo: '+f.rejectionReason+'</div>':(f.status==='cancelado'&&f.cancelReason)?'<div style="color:#555;font-size:10px;margin-top:2px;font-style:italic;">Motivo: '+f.cancelReason+'</div>':'';
            var actionBtn=f.status==='pendente'?'<button onclick="deletarFolga('+f.id+')" style="background:none;border:none;color:#ff4444;cursor:pointer;font-size:16px;padding:0 4px;flex-shrink:0;">×</button>':f.status==='aprovado'?'<button onclick="cancelarFolga('+f.id+')" style="background:rgba(255,100,0,0.1);border:1px solid rgba(255,100,0,0.3);color:#ff9944;cursor:pointer;font-size:10px;padding:3px 7px;border-radius:5px;flex-shrink:0;font-family:inherit;">Cancelar</button>':'';
            html+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px;margin-bottom:6px;"><div style="display:flex;justify-content:space-between;align-items:flex-start;"><div><div style="color:#d0dcd2;font-size:12px">'+dStr+'</div><div style="color:'+sc+';font-size:11px;margin-top:2px">'+sl+reasonHtml+'</div></div>'+actionBtn+'</div></div>';
        });
    }

    if((isMaster||isLider)&&pendentes.length>0){
        html+='<div class="sec-label" style="margin-top:16px;margin-bottom:10px;color:#ffcc00;">Aguardando Aprovação ('+pendentes.length+')</div>';
        pendentes.forEach(function(f){
            var dStr=f.startDate===f.endDate?fmtDate(f.startDate):fmtDate(f.startDate)+' → '+fmtDate(f.endDate);
            var msgHtml=f.mensagem?'<div style="color:#555;font-size:10px;margin-bottom:8px;font-style:italic;">"'+f.mensagem+'"</div>':'';
            html+='<div style="background:rgba(255,204,0,0.05);border:1px solid rgba(255,204,0,0.2);border-radius:8px;padding:10px;margin-bottom:8px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;"><strong style="color:#d0dcd2;font-size:12px">'+f.user+'</strong><span style="color:#aaa;font-size:10px">'+f.cargo+'</span></div><div style="color:#aaa;font-size:11px;margin-bottom:6px;">'+dStr+'</div>'+msgHtml+'<div style="display:flex;gap:8px;"><button onclick="aprovarFolga('+f.id+')" style="flex:1;background:rgba(102,204,0,0.12);border:1px solid #66cc00;color:#66cc00;padding:6px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:bold;">Aprovar</button><button onclick="rejeitarFolga('+f.id+')" style="flex:1;background:rgba(255,68,68,0.1);border:1px solid #ff4444;color:#ff4444;padding:6px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:bold;">Rejeitar</button></div></div>';
        });
    }
    if(isLider&&allFolgas.length>0){html+='<div class="sec-label" style="margin-top:16px;margin-bottom:10px;color:#94a3b8;">Todas as Solicitações ('+allFolgas.length+')</div>';var sorted=allFolgas.slice().sort(function(a,b){return b.id-a.id;});sorted.forEach(function(f){var sc=f.status==='aprovado'?'#66cc00':f.status==='rejeitado'?'#ff4444':f.status==='cancelado'?'#555':'#ffcc00';var sl=f.status==='aprovado'?'✓ Aprovado':f.status==='rejeitado'?'✗ Recusado':f.status==='cancelado'?'✕ Cancelado':'⏳ Pendente';var dStr=f.startDate===f.endDate?fmtDate(f.startDate):fmtDate(f.startDate)+' → '+fmtDate(f.endDate);var cancelBtn=(f.status==='aprovado'||f.status==='pendente')?'<button onclick="cancelarFolga('+f.id+')" style="background:rgba(255,100,0,0.1);border:1px solid rgba(255,100,0,0.3);color:#ff9944;cursor:pointer;font-size:10px;padding:3px 7px;border-radius:5px;font-family:inherit;">Cancelar</button>':'';html+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px;margin-bottom:6px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><div style="color:#d0dcd2;font-size:12px;font-weight:500;">'+f.user+'<span style="color:#555;font-size:10px;margin-left:6px;">'+f.cargo+'</span></div><div style="color:#aaa;font-size:11px;margin-top:2px;">'+dStr+'</div>'+(f.motivo?'<div style="color:#888;font-size:10px;margin-top:1px;">'+f.motivo+'</div>':'')+' </div><div style="display:flex;align-items:center;gap:6px;"><span style="color:'+sc+';font-size:10px;">'+sl+'</span>'+cancelBtn+'</div></div></div>';});}
    container.innerHTML=html;
}

window.folgasCalPrev=function(){folgasCalMonth--;if(folgasCalMonth<0){folgasCalMonth=11;folgasCalYear--;}renderFolgasWidget();};
window.folgasCalNext=function(){folgasCalMonth++;if(folgasCalMonth>11){folgasCalMonth=0;folgasCalYear++;}renderFolgasWidget();};

window.submitFolga=async function(){
    var s=document.getElementById('folgas-start').value;
    var e=document.getElementById('folgas-end').value;
    var lider=document.getElementById('folgas-lider').value;
    var motivo=document.getElementById('folgas-motivo').value;
    var msg=document.getElementById('folgas-msg')?.value||'';
    if(!s||!e){showToast('Preencha as datas.','error');return;}
    if(new Date(e)<new Date(s)){showToast('Data de retorno inválida.','error');return;}
    if(!lider){showToast('Selecione o líder direto.','error');return;}
    if(!motivo){showToast('Selecione o motivo da folga.','error');return;}
    try{
        const res=await fetch('/api/folgas/solicitar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({startDate:s,endDate:e,liderDireto:lider,motivo:motivo,mensagem:msg})});
        if(res.ok){showToast('Folga solicitada! Aguardando aprovação.');document.getElementById('folgas-modal').classList.remove('active');var msgEl=document.getElementById('folgas-msg');if(msgEl)msgEl.value='';var motivoEl=document.getElementById('folgas-motivo');if(motivoEl)motivoEl.value='';await loadFolgas();}
        else{var d=await res.json();showToast(d.error||'Erro.','error');}
    }catch(e){showToast('Erro ao solicitar.','error');}
};
window.aprovarFolga=async function(id){
    try{var res=await fetch('/api/folgas/aprovar/'+id,{method:'POST'});if(res.ok){showToast('Folga aprovada!');await loadFolgas();}else{var d=await res.json();showToast(d.error||'Erro.','error');}}catch(e){showToast('Erro.','error');}
};
window.deletarFolga=async function(id){
    if(!confirm('Cancelar esta solicitação?'))return;
    try{var res=await fetch('/api/folgas/delete/'+id,{method:'POST'});if(res.ok){showToast('Solicitação cancelada.');await loadFolgas();}else throw new Error();}catch(e){showToast('Erro.','error');}
};

// ===== FIM SISTEMA DE FOLGAS =====
window.switchView = function(view) {
    currentView = view;
    var views = {dashboard:'view-dashboard', ferias:'view-ferias', folgas:'view-folgas', historico:'view-historico', admin:'view-admin', logs:'view-logs', rh:'view-rh', lideres:'view-lideres', compras:'view-compras'};
    var navs  = {dashboard:'nav-dashboard',  ferias:'nav-ferias',  folgas:'nav-folgas', historico:'nav-historico', admin:'nav-admin', logs:'nav-logs', rh:'nav-rh', lideres:'nav-lideres', compras:'nav-compras'};
    // Show/hide views
    Object.keys(views).forEach(function(k){
        var el=document.getElementById(views[k]);
        if(el) el.style.display = (k===view) ? '' : 'none';
    });
    // Active nav item
    Object.keys(navs).forEach(function(k){
        var el=document.getElementById(navs[k]);
        if(el) el.classList.toggle('lnav-active', k===view);
    });
    if(view==='ferias'){ loadFerias(); loadLideres(); }
    if(view==='folgas'){ loadFolgas(); loadLideres(); }
    if(view==='historico'){ loadHistorico(); }
    if(view==='logs'){ loadLogs(); }
    if(view==='rh'){ loadRH(); }
    if(view==='lideres'){ loadLideresView(); }
    if(view==='compras'){ loadComprasView(); }
    if(view==='admin'){var adminSec=document.getElementById('admin-section');if(adminSec)adminSec.classList.add('visible');
        if(typeof setupAdminForm==='function') setupAdminForm();
        if(typeof loadTable==='function') loadTable();
    }
};

async function loadLideres() {
    try {
        var res = await fetch('/api/lideres');
        var lideres = await res.json();
        // popula folgas-lider também
        var flSel=document.getElementById('folgas-lider');
        if(flSel){flSel.innerHTML='<option value="">Selecione o líder...</option>';lideres.forEach(function(l){var o=document.createElement('option');o.value=l.username;o.textContent=l.username+(l.cargo?' ('+l.cargo+')':'');flSel.appendChild(o);});}
        var sel = document.getElementById('ferias-lider');
        if(sel) {
            sel.innerHTML = '<option value="">Selecione o lider direto...</option>' +
                lideres.map(function(l){ return '<option value="'+l.username+'">'+l.username+' — '+l.cargo+'</option>'; }).join('');
        }
    } catch(e) { console.error('loadLideres:', e); }
}

// ===== SISTEMA DE FERIAS =====
let feriasCalMonth=new Date().getMonth();
let feriasCalYear=new Date().getFullYear();
let allFerias=[];
const CARGO_LIDER_JS={'Analista Comercial':'Lider Comercial','Analista Recursos Humanos':'Lider Recursos Humanos','Analista Marketing':'Lider Marketing','Analista Financeiro':'Lider Financeiro','Analista Eventos':'Lider Eventos'};

function cargoSelectHtml(username,currentCargo,editable){
    var groups=[['Lideranca',['Lider Comercial','Lider Recursos Humanos','Lider Marketing','Lider Concierge','Lider Financeiro','Lider Eventos','Diretoria']],['Analistas',['Analista Comercial','Analista Recursos Humanos','Analista Marketing','Analista Financeiro','Analista Eventos']]];
    if(!editable)return '<span style="color:#aaa;font-size:11px">'+(currentCargo||'--')+'</span>';
    var s='<select id="cargo-'+username+'" style="background:rgba(255,255,255,0.04);color:#d0dcd2;border:1px solid rgba(255,255,255,0.1);padding:6px 8px;border-radius:6px;font-size:11px;min-width:155px;"><option value="">-- Sem cargo --</option>';
    groups.forEach(function(item){var g=item[0];var items=item[1];s+='<optgroup label="'+g+'">';items.forEach(function(c){s+='<option value="'+c+'"'+(currentCargo===c?' selected':'')+'>'+c+'</option>';});s+='</optgroup>';});
    s+='</select>';return s;
}

async function loadFerias(){
    try{allFerias=await(await fetch('/api/ferias')).json();renderFeriasWidget();updateBell();loadAllAprovadas();}
    catch(e){console.error('loadFerias:',e);}
}

function fmtDate(d){if(!d)return'';var p=d.split('-');return p[2]+'/'+p[1]+'/'+p[0];}
function fmtDateTime(iso){if(!iso)return'';var d=new Date(iso);return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric'})+' '+d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});}

function renderFeriasWidget(){
    var container=document.getElementById('ferias-main-view');
    if(!container)return;
    var isMaster=['master','anjo-caido'].includes(myRole);
    var isLider=!!(myCargo&&(myCargo.startsWith('Lider')||myCargo==='Diretoria'))||myRhAccess;
    var pendentes=allFerias.filter(function(f){
        if(f.status!=='pendente')return false;
        if(isMaster)return true;
        return f.liderDireto===myUser||(myCargo==='Lider Recursos Humanos'||myRhAccess);
    });
    var aprovadas=allFerias.filter(function(f){return f.status==='aprovado';});
    var minhas=allFerias.filter(function(f){return f.user===myUser;});
    var today=new Date();today.setHours(0,0,0,0);
    var upcoming=aprovadas.filter(function(f){return new Date(f.endDate+'T23:59:59')>=today;}).sort(function(a,b){return new Date(a.startDate)-new Date(b.startDate);}).slice(0,5);

    var html='<button onclick="document.getElementById(\'ferias-modal\').classList.add(\'active\')" style="width:100%;margin-bottom:18px;background:rgba(102,204,0,0.08);border:1px solid rgba(102,204,0,0.3);color:#66cc00;padding:11px;border-radius:9px;font-weight:600;cursor:pointer;font-size:13px;transition:all .15s;letter-spacing:.02em;">+ Solicitar Férias</button>';
    html+=buildFeriasCalendar(aprovadas);

    if(upcoming.length>0){
        html+='<div style="margin-top:12px;"><div style="font-size:10px;color:#aaa;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">Proximas Ferias Aprovadas</div>';
        upcoming.forEach(function(f){
            html+='<div style="background:rgba(102,204,0,0.05);border-left:3px solid #66cc00;border-radius:6px;padding:8px 10px;margin-bottom:6px;"><div style="display:flex;justify-content:space-between;align-items:center;"><strong style="color:#fff;font-size:12px">'+f.user+'</strong><div style="display:flex;align-items:center;gap:6px;">'+(f.cargo?'<span style="color:#555;font-size:10px">'+f.cargo+'</span>':'')+(isMaster||isLider?'<button onclick="cancelarFerias('+f.id+')" style="background:rgba(255,100,0,0.1);border:1px solid rgba(255,100,0,0.3);color:#ff9944;cursor:pointer;font-size:10px;padding:2px 6px;border-radius:4px;font-family:inherit;">Cancelar</button>':'')+'</div></div><div style="color:#aaa;font-size:11px;margin-top:2px;">'+fmtDate(f.startDate)+' ate '+fmtDate(f.endDate)+'</div></div>';
        });
        html+='</div>';
    }

    var minhasRec=minhas.sort(function(a,b){return b.id-a.id;}).slice(0,3);
    if(minhasRec.length>0){
        html+='<div style="margin-top:12px;"><div style="font-size:10px;color:#aaa;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">Minhas Solicitacoes</div>';
        minhasRec.forEach(function(f){
            var sc=f.status==='aprovado'?'#66cc00':f.status==='rejeitado'?'#ff4444':f.status==='cancelado'?'#888':'#ffcc00';
            var sl=f.status==='aprovado'?'✓ Aprovado':f.status==='rejeitado'?'✗ Recusado':f.status==='cancelado'?'✕ Cancelado':'⏳ Pendente';
            var reasonHtml=(f.status==='rejeitado'&&f.rejectionReason)?'<div style="color:#555;font-size:10px;margin-top:3px;font-style:italic;">Motivo: '+f.rejectionReason+'</div>':(f.status==='cancelado'&&f.cancelReason)?'<div style="color:#555;font-size:10px;margin-top:3px;font-style:italic;">Motivo: '+f.cancelReason+'</div>':'';
            var actionBtn=f.status==='pendente'?'<button onclick="deletarFerias('+f.id+')" style="background:none;border:none;color:#ff4444;cursor:pointer;font-size:16px;line-height:1;padding:0 4px;flex-shrink:0;">×</button>':f.status==='aprovado'?'<button onclick="cancelarFerias('+f.id+')" style="background:rgba(255,100,0,0.1);border:1px solid rgba(255,100,0,0.3);color:#ff9944;cursor:pointer;font-size:10px;padding:3px 7px;border-radius:5px;flex-shrink:0;font-family:inherit;">Cancelar</button>':'';
            html+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px;margin-bottom:6px;"><div style="display:flex;justify-content:space-between;align-items:flex-start;"><div><div style="color:#d0dcd2;font-size:12px">'+fmtDate(f.startDate)+' → '+fmtDate(f.endDate)+'</div><div style="color:'+sc+';font-size:11px;margin-top:2px">'+sl+reasonHtml+'</div></div>'+actionBtn+'</div></div>';
        });
        html+='</div>';
    }

    if((isMaster||isLider)&&pendentes.length>0){
        html+='<div style="margin-top:12px;"><div style="font-size:10px;color:#ffcc00;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">Aguardando Aprovacao ('+pendentes.length+')</div>';
        pendentes.forEach(function(f){
            html+='<div style="background:rgba(255,204,0,0.05);border:1px solid rgba(255,204,0,0.2);border-radius:8px;padding:10px;margin-bottom:8px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;"><strong style="color:#fff;font-size:12px">'+f.user+'</strong><span style="color:#aaa;font-size:10px">'+f.cargo+'</span></div><div style="color:#aaa;font-size:11px;margin-bottom:8px;">'+fmtDate(f.startDate)+' ate '+fmtDate(f.endDate)+'</div><div style="display:flex;gap:8px;"><button onclick="aprovarFerias('+f.id+')" style="flex:1;background:rgba(102,204,0,0.12);border:1px solid #66cc00;color:#66cc00;padding:6px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:bold;">Aprovar</button><button onclick="rejeitarFerias('+f.id+')" style="flex:1;background:rgba(255,68,68,0.1);border:1px solid #ff4444;color:#ff4444;padding:6px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:bold;">Rejeitar</button></div></div>';
        });
        html+='</div>';
    }
    if(isLider&&allFerias.length>0){html+='<div style="margin-top:16px;"><div style="font-size:10px;color:#94a3b8;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">Todas as Solicitações ('+allFerias.length+')</div>';var sorted=allFerias.slice().sort(function(a,b){return b.id-a.id;});sorted.forEach(function(f){var sc=f.status==='aprovado'?'#66cc00':f.status==='rejeitado'?'#ff4444':f.status==='cancelado'?'#555':'#ffcc00';var sl=f.status==='aprovado'?'✓ Aprovado':f.status==='rejeitado'?'✗ Recusado':f.status==='cancelado'?'✕ Cancelado':'⏳ Pendente';var cancelBtn=(f.status==='aprovado'||f.status==='pendente')?'<button onclick="cancelarFerias('+f.id+')" style="background:rgba(255,100,0,0.1);border:1px solid rgba(255,100,0,0.3);color:#ff9944;cursor:pointer;font-size:10px;padding:3px 7px;border-radius:5px;font-family:inherit;">Cancelar</button>':'';html+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px;margin-bottom:6px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><div style="color:#d0dcd2;font-size:12px;font-weight:500;">'+f.user+'<span style="color:#555;font-size:10px;margin-left:6px;">'+f.cargo+'</span></div><div style="color:#aaa;font-size:11px;margin-top:2px;">'+fmtDate(f.startDate)+' → '+fmtDate(f.endDate)+'</div></div><div style="display:flex;align-items:center;gap:6px;"><span style="color:'+sc+';font-size:10px;">'+sl+'</span>'+cancelBtn+'</div></div></div>';});html+='</div>';}
    container.innerHTML=html;
    renderDashboardCalendar();
}

function buildCalendar(aprovadas,yr,mo,prevFn,nextFn){
    var dim=new Date(yr,mo+1,0).getDate();
    var fd=new Date(yr,mo,1).getDay();
    var mn=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
    var dayData={};
    aprovadas.forEach(function(f){
        var s=new Date(f.startDate+'T00:00:00'),e=new Date(f.endDate+'T23:59:59');
        for(var d=new Date(s);d<=e;d.setDate(d.getDate()+1)){
            if(d.getFullYear()===yr&&d.getMonth()===mo){
                var k=d.getDate();
                if(!dayData[k])dayData[k]={ppl:[],sameTeam:false};
                dayData[k].ppl.push(f.user);
                if(myTeam&&f.team&&f.team===myTeam)dayData[k].sameTeam=true;
            }
        }
    });
    var today=new Date();
    var html='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:14px;">';
    html+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">';
    html+='<button onclick="'+prevFn+'()" style="background:none;border:none;color:#66cc00;cursor:pointer;font-size:20px;line-height:1;padding:0 8px;">&#8249;</button>';
    html+='<span style="color:#d0dcd2;font-size:13px;font-weight:600;">'+mn[mo]+' '+yr+'</span>';
    html+='<button onclick="'+nextFn+'()" style="background:none;border:none;color:#66cc00;cursor:pointer;font-size:20px;line-height:1;padding:0 8px;">&#8250;</button>';
    html+='</div>';
    html+='<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:2px;text-align:center;">';
    ['D','S','T','Q','Q','S','S'].forEach(function(d){html+='<div style="color:#3a5040;font-size:10px;padding:4px 0;">'+d+'</div>';});
    for(var i=0;i<fd;i++)html+='<div></div>';
    for(var day=1;day<=dim;day++){
        var isToday=today.getFullYear()===yr&&today.getMonth()===mo&&today.getDate()===day;
        var data=dayData[day]||{ppl:[],sameTeam:false};
        var hasV=data.ppl.length>0;
        var isSame=data.sameTeam;
        var bg=isToday?'rgba(102,204,0,0.15)':hasV?(isSame?'rgba(255,60,60,0.13)':'rgba(77,130,255,0.1)'):'transparent';
        var brd=isToday?'1px solid rgba(102,204,0,0.6)':hasV?(isSame?'1px solid rgba(255,60,60,0.4)':'1px solid rgba(77,130,255,0.35)'):'1px solid transparent';
        var clr=isToday?'#a0e070':hasV?(isSame?'#ff7070':'#7aaaff'):'#555';
        var dotBg=isSame?'#ff7070':'#7aaaff';
        var tt=data.ppl.join(', ');
        var _nameHtml='';if(hasV){var _fn=data.ppl[0].split('.')[0];_fn=_fn.charAt(0).toUpperCase()+_fn.slice(1);var _more=data.ppl.length>1?' +' +(data.ppl.length-1):'';_nameHtml='<div style="font-size:7.5px;color:'+clr+';overflow:hidden;text-overflow:ellipsis;white-space:nowrap;line-height:1.3;margin-top:1px;">'+(_fn.length>7?_fn.slice(0,6)+'...':_fn)+(_more?'<span style="opacity:.6"> '+_more+'</span>':'')+'</div>';}
        html+='<div title="'+tt+'" style="position:relative;padding:5px 2px 3px;border-radius:5px;font-size:11px;cursor:'+(hasV?'pointer':'default')+';background:'+bg+';border:'+brd+';color:'+clr+';font-weight:'+(isToday?'bold':'normal')+';">'+day+_nameHtml+'</div>';
    }
    html+='</div>';
    if(Object.keys(dayData).length>0){
        html+='<div style="display:flex;gap:12px;margin-top:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.04);">';
        html+='<div style="display:flex;align-items:center;gap:5px;font-size:10px;color:#7aaaff;"><div style="width:8px;height:8px;border-radius:2px;background:rgba(77,130,255,0.3);border:1px solid rgba(77,130,255,0.35);"></div>Outro time</div>';
        html+='<div style="display:flex;align-items:center;gap:5px;font-size:10px;color:#ff7070;"><div style="width:8px;height:8px;border-radius:2px;background:rgba(255,60,60,0.2);border:1px solid rgba(255,60,60,0.4);"></div>Meu time</div>';
        html+='</div>';
    }
    html+='</div>';
    return html;
}
function buildFeriasCalendar(aprovadas){
    // Usa allFeriasAprv se disponivel (mostra ferias de todos), senao usa o passado
    var data=allFeriasAprv.length>0?allFeriasAprv:aprovadas;
    return buildCalendar(data,feriasCalYear,feriasCalMonth,'feriasCalPrev','feriasCalNext');
}
let dashCalMonth=new Date().getMonth();
let dashCalYear=new Date().getFullYear();
function buildDashboardCalendar(aprovadas){
    return buildCalendar(aprovadas,dashCalYear,dashCalMonth,'dashCalPrev','dashCalNext');
}
window.dashCalPrev=function(){dashCalMonth--;if(dashCalMonth<0){dashCalMonth=11;dashCalYear--;}renderDashboardCalendar();};
window.dashCalNext=function(){dashCalMonth++;if(dashCalMonth>11){dashCalMonth=0;dashCalYear++;}renderDashboardCalendar();};
function renderDashboardCalendar(){
    var el=document.getElementById('dash-cal');if(!el)return;
    // Merge ferias + folgas aprovadas para mostrar tudo no calendario do dashboard
    var aprovadas=allFeriasAprv.concat(allFolgasAprv);
    el.innerHTML=buildDashboardCalendar(aprovadas);
}

window.feriasCalPrev=function(){feriasCalMonth--;if(feriasCalMonth<0){feriasCalMonth=11;feriasCalYear--;}renderFeriasWidget();};
window.feriasCalNext=function(){feriasCalMonth++;if(feriasCalMonth>11){feriasCalMonth=0;feriasCalYear++;}renderFeriasWidget();};

window.submitFerias=async function(){
    var s=document.getElementById('ferias-start').value;
    var e=document.getElementById('ferias-end').value;
    var lider=document.getElementById('ferias-lider')?.value||'';var msg=document.getElementById('ferias-msg')?.value||'';
    if(!s||!e)return showToast('Preencha as datas!','error');
    if(!lider)return showToast('Selecione o lider direto!','error');
    if(new Date(s)>new Date(e))return showToast('Data de saida maior que a de retorno!','error');
    try{
        var res=await fetch('/api/ferias/solicitar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({startDate:s,endDate:e,liderDireto:lider,mensagem:msg})});
        if(res.ok){showToast('Solicitacao enviada! Aguardando aprovacao.');document.getElementById('ferias-modal').classList.remove('active');var msgEl=document.getElementById('ferias-msg');if(msgEl)msgEl.value='';await loadFerias();}
        else{var d=await res.json();showToast(d.error||'Erro ao solicitar.','error');}
    }catch(err){showToast('Erro ao solicitar.','error');}
};
window.aprovarFerias=async function(id){
    try{var res=await fetch('/api/ferias/aprovar/'+id,{method:'POST'});
    if(res.ok){showToast('Ferias aprovadas!');await loadFerias();}
    else{var d=await res.json();showToast(d.error||'Sem permissao.','error');}}
    catch(e){showToast('Erro.','error');}
};
let _pendingRejectId=null;let _pendingRejectType='ferias';
let _pendingCancelId=null;let _pendingCancelType='ferias';
window.rejeitarFerias=function(id){_pendingRejectType='ferias';_pendingRejectId=id;document.getElementById('reject-reason').value='';document.getElementById('reject-modal').classList.add('active');};
window.rejeitarFolga=function(id){_pendingRejectType='folgas';_pendingRejectId=id;document.getElementById('reject-reason').value='';document.getElementById('reject-modal').classList.add('active');};
window.confirmRejeitar=async function(){
    const reason=document.getElementById('reject-reason').value.trim();
    if(!reason){showToast('Motivo da recusa é obrigatório.','error');return;}
    try{
        const res=await fetch('/api/'+_pendingRejectType+'/rejeitar/'+_pendingRejectId,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rejectionReason:reason})});
        if(res.ok){document.getElementById('reject-modal').classList.remove('active');showToast('Solicitação recusada.');if(_pendingRejectType==='ferias')loadFerias();else loadFolgas();}
        else{const d=await res.json();showToast(d.error||'Erro.','error');}
    }catch(e){showToast('Erro ao recusar.','error');}
};
window.deletarFerias=async function(id){
    if(!confirm('Cancelar esta solicitacao?'))return;
    try{var res=await fetch('/api/ferias/delete/'+id,{method:'POST'});
    if(res.ok){showToast('Solicitacao cancelada.');await loadFerias();}
    else showToast('Erro.','error');}
    catch(e){showToast('Erro.','error');}
};


// ===== CANCELAR FERIAS/FOLGAS =====
window.cancelarFerias=function(id){_pendingCancelType='ferias';_pendingCancelId=id;document.getElementById('cancel-reason').value='';document.getElementById('cancel-modal').classList.add('active');};
window.cancelarFolga=function(id){_pendingCancelType='folgas';_pendingCancelId=id;document.getElementById('cancel-reason').value='';document.getElementById('cancel-modal').classList.add('active');};
window.confirmCancelar=async function(){
    var reason=document.getElementById('cancel-reason').value.trim();
    if(!reason){showToast('Motivo do cancelamento é obrigatório.','error');return;}
    try{
        var res=await fetch('/api/'+_pendingCancelType+'/cancelar/'+_pendingCancelId,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cancelReason:reason})});
        if(res.ok){document.getElementById('cancel-modal').classList.remove('active');showToast('Cancelado com sucesso.');if(_pendingCancelType==='ferias')loadFerias();else loadFolgas();}
        else{var d=await res.json();showToast(d.error||'Erro.','error');}
    }catch(e){showToast('Erro ao cancelar.','error');}
};

// ===== NOTIFICACOES (BELL) =====
function generateNotifications(){
    var seen=new Set(JSON.parse(localStorage.getItem('bell_seen')||'[]'));
    var isMaster=['master','anjo-caido'].includes(myRole);
    var notifs=[];
    allFerias.filter(function(f){return f.user===myUser&&f.status!=='pendente';}).forEach(function(f){
        var key='f_'+f.id+'_'+f.status;
        var sc=f.status==='aprovado'?'#66cc00':f.status==='rejeitado'?'#ff4444':'#888';
        var sl=f.status==='aprovado'?'✓ Férias aprovadas':f.status==='rejeitado'?'✗ Férias recusadas':'✕ Férias canceladas';
        var dt=f.approvedAt||f.rejectedAt||f.cancelledAt||'';
        notifs.push({key:key,color:sc,label:sl,sub:fmtDate(f.startDate)+' → '+fmtDate(f.endDate),dt:dt,read:seen.has(key),type:'status'});
    });
    allFolgas.filter(function(f){return f.user===myUser&&f.status!=='pendente';}).forEach(function(f){
        var key='fg_'+f.id+'_'+f.status;
        var sc=f.status==='aprovado'?'#66cc00':f.status==='rejeitado'?'#ff4444':'#888';
        var sl=f.status==='aprovado'?'✓ Folga aprovada':f.status==='rejeitado'?'✗ Folga recusada':'✕ Folga cancelada';
        var dStr=f.startDate===f.endDate?fmtDate(f.startDate):fmtDate(f.startDate)+' → '+fmtDate(f.endDate);
        var dt=f.approvedAt||f.rejectedAt||f.cancelledAt||'';
        notifs.push({key:key,color:sc,label:sl,sub:dStr,dt:dt,read:seen.has(key),type:'status'});
    });
    var isMgr=isMaster||(myCargo==='Lider Recursos Humanos'||myRhAccess);
    var pend=[].concat(
        allFerias.filter(function(f){return f.status==='pendente'&&(isMaster||f.liderDireto===myUser||(myCargo==='Lider Recursos Humanos'||myRhAccess));}),
        allFolgas.filter(function(f){return f.status==='pendente'&&(isMaster||f.liderDireto===myUser||(myCargo==='Lider Recursos Humanos'||myRhAccess));})
    );
    if(pend.length>0){
        var pendKey='pend_'+pend.map(function(f){return f.id;}).sort().join('_');
        notifs.push({key:pendKey,color:'#ffcc00',label:'⏳ '+pend.length+' aguardando sua aprovação',sub:'',dt:'',read:seen.has(pendKey),type:'pending'});
    }
    return notifs.sort(function(a,b){return (b.dt||'').localeCompare(a.dt||'');});
}

function renderBellList(notifs){
    var list=document.getElementById('bell-list');
    if(!list)return;
    if(notifs.length===0){list.innerHTML='<div style="padding:20px;text-align:center;color:#555;font-size:12px;">Sem notificações</div>';return;}
    list.innerHTML=notifs.map(function(n){
        return '<div data-bellkey="'+encodeURIComponent(n.key)+'" style="padding:10px 16px;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;gap:10px;align-items:flex-start;background:'+(n.read?'transparent':'rgba(102,204,0,0.025)')+';cursor:pointer;">'
            +'<div style="color:'+n.color+';font-size:14px;flex-shrink:0;margin-top:2px;">●</div>'
            +'<div style="flex:1;min-width:0;"><div style="color:'+(n.read?'#666':'#d0dcd2')+';font-size:12px;font-weight:'+(n.read?'400':'600')+';">'+n.label+'</div>'
            +(n.sub?'<div style="color:#555;font-size:11px;margin-top:1px;">'+n.sub+'</div>':'')
            +(n.dt?'<div style="color:#3a5040;font-size:10px;margin-top:2px;">'+fmtDateTime(n.dt)+'</div>':'')
            +'</div></div>';
    }).join('');
    list.querySelectorAll('[data-bellkey]').forEach(function(el){
        el.addEventListener('click',function(){window.markRead(decodeURIComponent(el.getAttribute('data-bellkey')));});
    });
}

function updateBell(){
    var notifs=generateNotifications();
    var unread=notifs.filter(function(n){return !n.read&&n.type==='status';}).length;
    var badge=document.getElementById('bell-badge');
    if(!badge)return;
    if(unread>0){badge.style.display='flex';badge.textContent=unread>9?'9+':String(unread);}
    else{badge.style.display='none';}
    var dd=document.getElementById('bell-dropdown');
    if(dd&&dd.style.display!=='none')renderBellList(notifs);
}

window.toggleBell=function(){
    var dd=document.getElementById('bell-dropdown');
    if(!dd)return;
    if(dd.style.display!=='none'){dd.style.display='none';}
    else{dd.style.display='block';renderBellList(generateNotifications());}
};
window.markRead=function(key){
    var seen=new Set(JSON.parse(localStorage.getItem('bell_seen')||'[]'));
    seen.add(key);localStorage.setItem('bell_seen',JSON.stringify([...seen]));
    updateBell();renderBellList(generateNotifications());
};
window.markAllRead=function(){
    var notifs=generateNotifications();
    var seen=new Set(JSON.parse(localStorage.getItem('bell_seen')||'[]'));
    notifs.forEach(function(n){seen.add(n.key);});
    localStorage.setItem('bell_seen',JSON.stringify([...seen]));
    updateBell();renderBellList(generateNotifications());
};
document.addEventListener('click',function(e){
    var wrap=document.getElementById('bell-wrap');
    if(wrap&&!wrap.contains(e.target)){var dd=document.getElementById('bell-dropdown');if(dd)dd.style.display='none';}
});

// ===== HISTORICO =====
async function loadHistorico(){
    var container=document.getElementById('historico-main');
    if(!container)return;
    var isMaster=['master','anjo-caido'].includes(myRole);
    var isLider=(myCargo==='Lider Recursos Humanos'||myRhAccess)||isMaster;
    var events=[];
    var feriasToShow=isMaster||isLider?allFerias:allFerias.filter(function(f){return f.user===myUser||f.liderDireto===myUser;});
    feriasToShow.forEach(function(f){
        if(f.requestedAt)events.push({dt:f.requestedAt,user:f.user,icon:'🏖️',label:'Férias solicitada',sub:fmtDate(f.startDate)+' → '+fmtDate(f.endDate),color:'#7aaaff'});
        if(f.approvedAt&&f.status==='aprovado')events.push({dt:f.approvedAt,user:f.user,icon:'✅',label:'Férias aprovada por '+(f.approvedBy||'?'),sub:fmtDate(f.startDate)+' → '+fmtDate(f.endDate),color:'#66cc00'});
        if(f.rejectedAt&&f.status==='rejeitado')events.push({dt:f.rejectedAt,user:f.user,icon:'❌',label:'Férias recusada'+(f.rejectionReason?' — '+f.rejectionReason:''),sub:fmtDate(f.startDate)+' → '+fmtDate(f.endDate),color:'#ff4444'});
        if(f.cancelledAt&&f.status==='cancelado')events.push({dt:f.cancelledAt,user:f.user,icon:'🚫',label:'Férias cancelada'+(f.cancelReason?' — '+f.cancelReason:''),sub:fmtDate(f.startDate)+' → '+fmtDate(f.endDate),color:'#888'});
    });
    var folgasToShow=isMaster||isLider?allFolgas:allFolgas.filter(function(f){return f.user===myUser||f.liderDireto===myUser;});
    folgasToShow.forEach(function(f){
        var dStr=f.startDate===f.endDate?fmtDate(f.startDate):fmtDate(f.startDate)+' → '+fmtDate(f.endDate);
        if(f.requestedAt)events.push({dt:f.requestedAt,user:f.user,icon:'📅',label:'Folga solicitada',sub:dStr,color:'#7aaaff'});
        if(f.approvedAt&&f.status==='aprovado')events.push({dt:f.approvedAt,user:f.user,icon:'✅',label:'Folga aprovada por '+(f.approvedBy||'?'),sub:dStr,color:'#66cc00'});
        if(f.rejectedAt&&f.status==='rejeitado')events.push({dt:f.rejectedAt,user:f.user,icon:'❌',label:'Folga recusada'+(f.rejectionReason?' — '+f.rejectionReason:''),sub:dStr,color:'#ff4444'});
        if(f.cancelledAt&&f.status==='cancelado')events.push({dt:f.cancelledAt,user:f.user,icon:'🚫',label:'Folga cancelada'+(f.cancelReason?' — '+f.cancelReason:''),sub:dStr,color:'#888'});
    });
    allNotices.forEach(function(n){
        if(n.author&&(isMaster||isLider||n.author===myUser))
            events.push({dt:n.date||'',user:n.author,icon:'📢',label:'Aviso publicado: '+(n.text||'').substring(0,60)+(n.text&&n.text.length>60?'...':''),sub:'',color:'#ffcc00'});
    });
    events.sort(function(a,b){return (b.dt||'').localeCompare(a.dt||'');});
    if(events.length===0){container.innerHTML='<div style="text-align:center;color:#555;padding:40px 20px;font-size:13px;">Nenhum histórico encontrado.</div>';return;}
    var html='<div class="sec-label" style="margin-bottom:16px;">Histórico de Atividades</div>';
    events.forEach(function(e){
        html+='<div style="display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04);">';
        html+='<div style="font-size:18px;flex-shrink:0;width:26px;text-align:center;margin-top:1px;">'+e.icon+'</div>';
        html+='<div style="flex:1;min-width:0;">';
        html+='<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">';
        html+='<div><div style="color:'+e.color+';font-size:12px;font-weight:500;">'+e.label+'</div>';
        if(e.sub)html+='<div style="color:#777;font-size:11px;margin-top:2px;">'+e.sub+'</div>';
        if((isMaster||isLider)&&e.user)html+='<div style="color:#3a5040;font-size:11px;margin-top:1px;">👤 '+e.user+'</div>';
        html+='</div>';
        if(e.dt)html+='<div style="color:#3a5040;font-size:10px;white-space:nowrap;flex-shrink:0;">'+fmtDateTime(e.dt)+'</div>';
        html+='</div></div></div>';
    });
    container.innerHTML=html;
}


// ===== CARREGA TODAS APROVADAS (PARA CALENDARIOS) =====
async function loadAllAprovadas(){
    try{
        var [fa,fo]=await Promise.all([
            fetch('/api/ferias/aprovadas').then(function(r){return r.json();}),
            fetch('/api/folgas/aprovadas').then(function(r){return r.json();})
        ]);
        allFeriasAprv=fa;allFolgasAprv=fo;
        renderDashboardCalendar();
    }catch(e){console.error('loadAllAprovadas:',e);}
}



window._rhTab = window._rhTab || 'painel';
window._rhCalYear = window._rhCalYear || new Date().getFullYear();
window._rhCalMonth = window._rhCalMonth || new Date().getMonth();
window._rhEditUser = null;

window.loadRH = async function(tab) {
    if(tab) window._rhTab = tab;
    if(!window._rhTab) window._rhTab = 'painel';
    if(!window._rhCalYear) window._rhCalYear = new Date().getFullYear();
    if(window._rhCalMonth === undefined || window._rhCalMonth === null) window._rhCalMonth = new Date().getMonth();
    var container = document.getElementById('rh-main');
    if(!container) return;
    container.innerHTML = '<div style="color:#3a5040;font-size:13px;padding:20px;">Carregando...</div>';
    try {
        // ---- TABS HEADER ----
        var tabs = [{id:'painel',label:'Painel',icon:'&#128202;'},{id:'colaboradores',label:'Colaboradores',icon:'&#128101;'},{id:'calendario',label:'Calendário',icon:'&#128197;'},{id:'relatorios',label:'Relatórios',icon:'&#128196;'},{id:'compras',label:'Compras',icon:'&#128722;'},{id:'adquiridas',label:'Adquiridas',icon:'&#128717;'},{id:'beneficios',label:'Benéficios',icon:'&#128176;'}];
        var tabsHtml = '<div style="display:flex;gap:4px;margin-bottom:24px;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:0;">';
        tabs.forEach(function(t){
            var active = window._rhTab === t.id;
            tabsHtml += '<button onclick="loadRH(\''+t.id+'\')" style="background:'+(active?'rgba(102,204,0,0.1)':'transparent')+';border:none;border-bottom:2px solid '+(active?'#66cc00':'transparent')+';color:'+(active?'#66cc00':'#666')+';padding:10px 18px;cursor:pointer;font-family:inherit;font-size:13px;font-weight:'+(active?'600':'400')+';border-radius:6px 6px 0 0;transition:all .15s;">'+t.icon+' '+t.label+'</button>';
        });
        tabsHtml += '</div>';

        function fmtD(d){ if(!d)return''; var p=d.split('-'); return p[2]+'/'+p[1]+'/'+p[0]; }
        function daysLeft(endDate){
            var e=new Date(endDate+'T00:00:00'),t=new Date();t.setHours(0,0,0,0);
            var diff=Math.ceil((e-t)/(1000*60*60*24));
            if(diff<0)return '<span style="color:#888;font-size:10px;">retornou</span>';
            if(diff===0)return '<span style="color:#66cc00;font-size:10px;font-weight:700;">retorna hoje</span>';
            return '<span style="color:#ffcc00;font-size:10px;">retorna em '+diff+'d</span>';
        }
        function ageDays(iso){return iso?(Date.now()-new Date(iso))/(1000*60*60*24):0;}
        function timeAgo(iso){
            if(!iso)return '';
            var h=Math.floor((Date.now()-new Date(iso))/(1000*60*60));
            if(h<1)return 'há menos de 1h';
            if(h<24)return 'há '+h+'h';
            var d=Math.floor(h/24);return 'há '+d+' dia'+(d>1?'s':'');
        }
        function tenureStr(days){
            if(!days&&days!==0)return '—';
            if(days<30)return days+'d';
            if(days<365)return Math.floor(days/30)+'m';
            var y=Math.floor(days/365),m=Math.floor((days%365)/30);
            return y+'a'+(m>0?' '+m+'m':'');
        }
        function saldoBar(saldo, total, color){
            if(!saldo&&saldo!==0)return '';
            var pct=total>0?Math.min(100,Math.round(saldo/total*100)):0;
            return '<div style="background:rgba(255,255,255,0.06);border-radius:4px;height:5px;width:60px;display:inline-block;vertical-align:middle;"><div style="background:'+color+';width:'+pct+'%;height:100%;border-radius:4px;"></div></div>';
        }

        // ==============================
        // TAB: PAINEL
        // ==============================
        if(window._rhTab === 'painel'){
            var data = await (await fetch('/api/rh/dashboard')).json();
            if(data.error){ container.innerHTML=tabsHtml+'<div style="color:#ff4444;padding:20px;">'+data.error+'</div>'; return; }

            var cards=[
                {label:'Usuários Ativos',value:data.totalUsers,color:'#66cc00',icon:'&#128101;',sub:'total cadastrados'},
                {label:'Em Férias',value:data.feriasAtivas,color:'#7aaaff',icon:'&#127958;&#65039;',sub:'ausentes agora'},
                {label:'Em Folga',value:data.folgasAtivas,color:'#ff9944',icon:'&#128197;',sub:'ausentes agora'},
                {label:'Retornam em 7d',value:data.retornandoEmBreve,color:'#cc66ff',icon:'&#128336;',sub:'próximos 7 dias'},
                {label:'Aguardando Aprovação',value:data.pendentes,color:'#ffcc00',icon:'&#9203;',sub:'solicitações pendentes'},
            ];
            var leftHtml='<div style="flex:1;min-width:0;">';
            leftHtml+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(165px,1fr));gap:14px;margin-bottom:28px;">';
            cards.forEach(function(c){leftHtml+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-top:3px solid '+c.color+';border-radius:12px;padding:16px;"><div style="font-size:24px;margin-bottom:6px;">'+c.icon+'</div><div style="font-size:28px;font-weight:700;color:'+c.color+';">'+c.value+'</div><div style="color:#d0dcd2;font-size:12px;font-weight:600;margin-top:3px;">'+c.label+'</div><div style="color:#3a5040;font-size:10px;margin-top:1px;">'+c.sub+'</div></div>';});
            leftHtml+='</div>';

            // Alertas de retardo
            if(data.retardatarios && data.retardatarios.length>0){
                leftHtml+='<div style="background:rgba(255,68,68,0.06);border:1px solid rgba(255,68,68,0.25);border-radius:10px;padding:14px 16px;margin-bottom:20px;">';
                leftHtml+='<div style="color:#ff6060;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">&#9888; Retorno em Atraso ('+data.retardatarios.length+')</div>';
                data.retardatarios.forEach(function(f){
                    var tl=f.tipo==='Ferias'?'Férias':'Folga';
                    var tipoApi=f.tipo==='Ferias'?'ferias':'folgas';
                    leftHtml+='<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(255,68,68,0.1);">';
                    leftHtml+='<div><span style="color:#d0dcd2;font-size:12px;">'+f.user+(f.cargo?' <span style="color:#555;font-size:10px;">'+f.cargo+'</span>':'')+'</span><div style="color:#ff9090;font-size:10px;margin-top:2px;">'+tl+' — ret. '+fmtD(f.endDate)+'</div></div>';
                    leftHtml+='<button onclick="window._rhConfirmarRetorno(\''+tipoApi+'\','+f.id+')" style="background:rgba(102,204,0,0.1);color:#66cc00;border:1px solid rgba(102,204,0,0.3);padding:5px 12px;border-radius:6px;cursor:pointer;font-size:10px;font-family:inherit;white-space:nowrap;font-weight:600;">✓ Confirmar Retorno</button>';
                    leftHtml+='</div>';
                });
                leftHtml+='</div>';
            }

            // Stats por time
            if(data.teamStats && Object.keys(data.teamStats).length>0){
                leftHtml+='<div class="sec-label" style="margin-bottom:10px;">Ausências por Time</div>';
                leftHtml+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px;">';
                Object.entries(data.teamStats).forEach(function(e){
                    leftHtml+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:10px 14px;min-width:130px;"><div style="color:#d0dcd2;font-size:12px;font-weight:600;">'+e[0]+'</div><div style="color:#3a5040;font-size:10px;margin-top:3px;">'+e[1].ferias+' férias · '+e[1].folgas+' folgas</div><div style="color:#66cc00;font-size:18px;font-weight:700;">'+e[1].total+'</div></div>';
                });
                leftHtml+='</div>';
            }

            // Ausentes agora
            leftHtml+='<div class="sec-label" style="margin-bottom:12px;">Ausentes Agora ('+data.ausentes.length+')</div>';
            if(data.ausentes.length===0){leftHtml+='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:20px;text-align:center;color:#3a5040;font-size:13px;margin-bottom:24px;">Nenhum ausente.</div>';}
            else{
                leftHtml+='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden;margin-bottom:24px;">';
                leftHtml+='<div style="display:grid;grid-template-columns:1fr 90px 100px 100px 120px;gap:0;padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.03);"><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Colaborador</div><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Tipo</div><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Saída</div><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Retorno</div><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Status</div></div>';
                data.ausentes.forEach(function(f){var tc=f.tipo==='Ferias'?'#7aaaff':'#ff9944';var tl=f.tipo==='Ferias'?'Férias':'Folga';leftHtml+='<div style="display:grid;grid-template-columns:1fr 90px 100px 100px 120px;gap:0;padding:10px 14px;border-bottom:1px solid rgba(255,255,255,0.04);align-items:center;"><div><div style="color:#d0dcd2;font-size:12px;font-weight:500;">'+f.user+'</div>'+(f.cargo?'<div style="color:#555;font-size:10px;">'+f.cargo+'</div>':'')+' </div><div><span style="background:rgba('+(f.tipo==='Ferias'?'119,170,255':'255,153,68')+',0.12);color:'+tc+';border:1px solid '+tc+'44;padding:2px 7px;border-radius:20px;font-size:9px;font-weight:700;">'+tl+'</span></div><div style="color:#aaa;font-size:11px;">'+fmtD(f.startDate)+'</div><div style="color:#aaa;font-size:11px;">'+fmtD(f.endDate)+'</div><div>'+daysLeft(f.endDate)+'</div></div>';});
                leftHtml+='</div>';
            }

            // Retornando + Proximas
            if(data.retornando.length>0){
                leftHtml+='<div class="sec-label" style="margin-bottom:10px;">Retornando nos Próximos 7 Dias</div>';
                leftHtml+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;margin-bottom:24px;">';
                data.retornando.forEach(function(f){var tc=f.tipo==='Ferias'?'#7aaaff':'#ff9944';var tl=f.tipo==='Ferias'?'Férias':'Folga';leftHtml+='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-left:3px solid '+tc+';border-radius:8px;padding:10px 12px;display:flex;justify-content:space-between;align-items:center;"><div><div style="color:#d0dcd2;font-size:12px;font-weight:500;">'+f.user+'</div><div style="color:'+tc+';font-size:10px;margin-top:2px;">'+tl+'</div></div><div style="text-align:right;"><div style="color:#aaa;font-size:10px;">'+fmtD(f.endDate)+'</div><div style="margin-top:2px;">'+daysLeft(f.endDate)+'</div></div></div>';});
                leftHtml+='</div>';
            }
            if(data.proximas.length>0){
                leftHtml+='<div class="sec-label" style="margin-bottom:10px;">Próximas Ausências (30 dias)</div>';
                leftHtml+='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden;margin-bottom:24px;">';
                leftHtml+='<div style="display:grid;grid-template-columns:1fr 90px 100px 100px;gap:0;padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.03);"><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Colaborador</div><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Tipo</div><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Saída</div><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">Retorno</div></div>';
                data.proximas.forEach(function(f){var tc=f.tipo==='Ferias'?'#7aaaff':'#ff9944';var tl=f.tipo==='Ferias'?'Férias':'Folga';leftHtml+='<div style="display:grid;grid-template-columns:1fr 90px 100px 100px;gap:0;padding:10px 14px;border-bottom:1px solid rgba(255,255,255,0.04);align-items:center;"><div><div style="color:#d0dcd2;font-size:12px;font-weight:500;">'+f.user+'</div>'+(f.cargo?'<div style="color:#555;font-size:10px;">'+f.cargo+'</div>':'')+' </div><div><span style="background:rgba('+(f.tipo==='Ferias'?'119,170,255':'255,153,68')+',0.12);color:'+tc+';border:1px solid '+tc+'44;padding:2px 7px;border-radius:20px;font-size:9px;font-weight:700;">'+tl+'</span></div><div style="color:#aaa;font-size:11px;">'+fmtD(f.startDate)+'</div><div style="color:#aaa;font-size:11px;">'+fmtD(f.endDate)+'</div></div>';});
                leftHtml+='</div>';
            }
            leftHtml+='</div>';

            // SIDEBAR: ausentes + pendentes com ações
            var sideHtml='<div style="width:265px;flex-shrink:0;display:flex;flex-direction:column;gap:12px;position:sticky;top:80px;">';
            // Aniversariantes
            if(data.aniversariantes && data.aniversariantes.length>0){
                sideHtml+='<div style="background:rgba(255,200,0,0.05);border:1px solid rgba(255,200,0,0.2);border-radius:12px;padding:14px;">';
                sideHtml+='<div style="color:#ffcc00;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:10px;">&#127874; Aniversariantes do Mês</div>';
                data.aniversariantes.forEach(function(a){var day=a.birthday?a.birthday.split('-')[2]:'';sideHtml+='<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid rgba(255,200,0,0.1);"><span style="color:#d0dcd2;font-size:12px;">'+a.username+'</span><span style="color:#ffcc00;font-size:11px;">dia '+day+'</span></div>';});
                sideHtml+='</div>';
            }
            // Ausentes compacto
            sideHtml+='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px;">';
            sideHtml+='<div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:10px;">De Folga / Férias ('+data.ausentes.length+')</div>';
            if(data.ausentes.length===0){sideHtml+='<div style="color:#3a5040;font-size:12px;text-align:center;padding:8px 0;">Nenhum ausente</div>';}
            else{data.ausentes.forEach(function(f){var tc=f.tipo==='Ferias'?'#7aaaff':'#ff9944';var tl=f.tipo==='Ferias'?'Férias':'Folga';sideHtml+='<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);"><div><div style="color:#d0dcd2;font-size:11px;font-weight:500;">'+f.user+'</div>'+(f.cargo?'<div style="color:#555;font-size:9px;">'+f.cargo+'</div>':'')+' </div><div style="text-align:right;"><span style="background:rgba('+(f.tipo==='Ferias'?'119,170,255':'255,153,68')+',0.1);color:'+tc+';border:1px solid '+tc+'33;padding:1px 6px;border-radius:8px;font-size:8px;font-weight:700;">'+tl+'</span><div style="color:#555;font-size:9px;margin-top:1px;">ret. '+fmtD(f.endDate)+'</div></div></div>';});}
            sideHtml+='</div>';
            // Pendentes com ações
            var pending=data.pendingList||[];
            sideHtml+='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px;">';
            sideHtml+='<div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:10px;">Solicitações Pendentes ('+pending.length+')</div>';
            if(pending.length===0){sideHtml+='<div style="color:#3a5040;font-size:12px;text-align:center;padding:8px 0;">Nenhuma pendente</div>';}
            else{pending.forEach(function(f){var age=ageDays(f.requestedAt);var bc=age>2?'#ff4444':(age>1?'#ffcc00':'#66cc00');var bgc=age>2?'rgba(255,68,68,0.06)':(age>1?'rgba(255,204,0,0.06)':'rgba(102,204,0,0.04)');var tl=f.tipo==='Ferias'?'Férias':'Folga';var apiBase=f.tipo==='Ferias'?'/api/ferias':'/api/folgas';sideHtml+='<div style="border-left:3px solid '+bc+';background:'+bgc+';border-radius:0 8px 8px 0;padding:8px 10px;margin-bottom:8px;"><div style="display:flex;justify-content:space-between;align-items:center;"><span style="color:#d0dcd2;font-size:11px;font-weight:600;">'+f.user+'</span><span style="color:#555;font-size:8px;background:rgba(255,255,255,0.05);padding:1px 5px;border-radius:6px;">'+tl+'</span></div><div style="color:#888;font-size:9px;margin:2px 0;">'+fmtD(f.startDate)+' → '+fmtD(f.endDate)+'</div><div style="color:'+bc+';font-size:8px;margin-bottom:5px;font-weight:600;">'+timeAgo(f.requestedAt)+'</div><div style="display:flex;gap:5px;"><button onclick="window._rhAprovar(\''+apiBase+'\','+f.id+')" style="flex:1;background:rgba(102,204,0,0.15);color:#66cc00;border:1px solid rgba(102,204,0,0.3);padding:4px;border-radius:5px;cursor:pointer;font-size:9px;font-family:inherit;font-weight:600;">✓ Aprovar</button><button onclick="window._rhRejeitar(\''+apiBase+'\','+f.id+')" style="flex:1;background:rgba(255,68,68,0.1);color:#ff6060;border:1px solid rgba(255,68,68,0.25);padding:4px;border-radius:5px;cursor:pointer;font-size:9px;font-family:inherit;">✗ Rejeitar</button></div></div>';});}
            sideHtml+='</div></div>';

            container.innerHTML = tabsHtml + '<div style="display:flex;gap:18px;align-items:flex-start;">'+leftHtml+sideHtml+'</div>';

            window._rhAprovar = async function(base, id){
                try{var r=await fetch(base+'/aprovar/'+id,{method:'POST'});if(r.ok){showToast('Aprovado!');loadRH('painel');}else{var d=await r.json();showToast(d.error||'Erro','error');}}catch(e){showToast('Erro','error');}
            };
            window._rhConfirmarRetorno = async function(tipo, id){
                try{
                    var r=await fetch('/api/rh/confirmar-retorno/'+tipo+'/'+id,{method:'POST'});
                    if(r.ok){showToast('Retorno confirmado!');loadRH('painel');}
                    else{var d=await r.json();showToast(d.error||'Erro','error');}
                }catch(e){showToast('Erro','error');}
            };
            window._rhRejeitar = function(base, id){
                window._pendingRejectApiBase = base;
                window._pendingRejectRhId = id;
                document.getElementById('reject-reason').value='';
                document.getElementById('reject-modal').classList.add('active');
                window._pendingRejectRhMode = true;
            };
            // Override confirmRejeitar temporariamente
            var _origConfirm = window.confirmRejeitar;
            window.confirmRejeitar = async function(){
                if(!window._pendingRejectRhMode){_origConfirm&&_origConfirm();return;}
                var reason=document.getElementById('reject-reason').value.trim();
                if(!reason){showToast('Informe o motivo','error');return;}
                try{var r=await fetch(window._pendingRejectApiBase+'/rejeitar/'+window._pendingRejectRhId,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rejectionReason:reason})});
                if(r.ok){document.getElementById('reject-modal').classList.remove('active');showToast('Recusado.');window._pendingRejectRhMode=false;loadRH('painel');}
                else{var d=await r.json();showToast(d.error||'Erro','error');}
                }catch(e){showToast('Erro','error');}
            };
        }

        // ==============================
        // TAB: COLABORADORES
        // ==============================
        else if(window._rhTab === 'colaboradores'){
            var colabs = await (await fetch('/api/rh/colaboradores')).json();
            if(colabs.error){ container.innerHTML=tabsHtml+'<div style="color:#ff4444;padding:20px;">'+colabs.error+'</div>'; return; }

            var html='<div style="overflow-x:auto;">';
            html+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">';
            html+='<div style="color:#3a5040;font-size:11px;">'+colabs.length+' colaboradores</div>';
            html+='</div>';
            html+='<table style="width:100%;border-collapse:collapse;font-size:12px;">';
            html+='<thead><tr style="background:rgba(255,255,255,0.03);">';
            ['Colaborador','Time','Cargo','Entrada','Tempo','Saldo Férias','Ação'].forEach(function(h){html+='<th style="text-align:left;padding:10px 12px;color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,0.06);">'+h+'</th>';});
            html+='</tr></thead><tbody>';
            var prevTeam='';
            window._rhColabs = colabs;
            colabs.forEach(function(c, _ci){
                if(c.team!==prevTeam){
                    html+='<tr><td colspan="7" style="padding:14px 12px 4px;color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;">'+( c.team||'Sem time')+'</td></tr>';
                    prevTeam=c.team;
                }
                var saldoHtml='<span style="color:#555;font-size:10px;">Sem data entrada</span>';
                if(c.saldo){
                    if(!c.saldo.hasRight){
                        var d365=c.saldo.daysUntilRight;
                        saldoHtml='<span style="color:#555;font-size:10px;">Menos de 1 ano</span><div style="color:#3a5040;font-size:9px;">Direito em ~'+Math.ceil(d365/30)+'m</div>';
                    } else {
                        var rem=c.saldo.remaining;var used=c.saldo.used;var total=c.saldo.total;
                        var color=rem<=5?'#ff6060':(rem<=10?'#ffcc00':'#66cc00');
                        saldoHtml='<div style="display:flex;align-items:center;gap:6px;"><span style="color:'+color+';font-size:13px;font-weight:700;">'+rem+'</span><div style="font-size:9px;color:#555;">/<span style="color:#888;">'+total+'d</span><br>usados: '+used+'d</div></div>';
                        saldoHtml+='<div style="margin-top:4px;font-size:9px;color:#555;">Fim ano: <span style="color:#7aaaff;">'+c.saldo.fimAno.remaining+'d</span> · Ano: <span style="color:#66cc00;">'+c.saldo.durante.remaining+'d</span></div>';
                    }
                }
                var entradaHtml=c.dataEntrada?'<div style="color:#d0dcd2;font-size:11px;">'+fmtD(c.dataEntrada)+'</div>':'<span style="color:#555;font-size:10px;">—</span>';
                html+='<tr style="border-bottom:1px solid rgba(255,255,255,0.04);">';
                html+='<td style="padding:10px 12px;"><div style="color:#d0dcd2;font-size:12px;font-weight:500;">'+c.username+'</div><div style="color:#3a5040;font-size:10px;">'+c.email+'</div></td>';
                html+='<td style="padding:10px 12px;color:#888;font-size:11px;">'+(c.team||'—')+'</td>';
                html+='<td style="padding:10px 12px;color:#888;font-size:11px;">'+(c.cargo||'—')+'</td>';
                html+='<td style="padding:10px 12px;">'+entradaHtml+'</td>';
                html+='<td style="padding:10px 12px;color:#888;font-size:11px;">'+(c.tenureDays!==null?tenureStr(c.tenureDays):'—')+'</td>';
                html+='<td style="padding:10px 12px;">'+saldoHtml+'</td>';
                html+='<td style="padding:10px 12px;"><button onclick="window._rhOpenEdit('+_ci+')" style="background:rgba(102,204,0,0.08);color:#66cc00;border:1px solid rgba(102,204,0,0.25);padding:5px 10px;border-radius:6px;cursor:pointer;font-size:10px;font-family:inherit;">✎ Editar</button></td>';
                html+='</tr>';
            });
            html+='</tbody></table></div>';

            // Modal editar colaborador
            html+='<div id="rh-edit-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:9999;display:none;align-items:center;justify-content:center;"><div style="background:#080d09;border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:24px;width:400px;max-width:95vw;">';
            html+='<h3 style="color:#66cc00;margin-bottom:16px;font-size:15px;">✎ Editar Colaborador — <span id="rh-edit-name" style="color:#d0dcd2;font-weight:400;"></span></h3>';
            html+='<div style="display:flex;flex-direction:column;gap:12px;">';
            html+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">Data de Entrada</div><input type="date" id="rh-edit-entrada" style="width:100%;padding:9px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;"></div>';
            html+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">Cargo</div><input type="text" id="rh-edit-cargo" placeholder="ex: Analista Comercial" style="width:100%;padding:9px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;"></div>';
            html+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">Time</div><select id="rh-edit-team" style="width:100%;padding:9px 10px;background:#0a120b;border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;"><option value="">Selecione...</option><option>Atenção</option><option>Comercial</option><option>Eventos</option><option>Concierge</option><option>Suporte</option><option>Administrativo</option><option>Financeiro</option><option>Diretoria</option><option>Recursos Humanos</option></select></div>';
            html+='<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 0;"></div>';
            html+='<div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;padding-top:4px;">Dados Pessoais</div>';
            html+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">Nome Completo</div><input type="text" id="rh-edit-nome" placeholder="Nome completo" style="width:100%;padding:9px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;"></div>';
            html+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">CPF / CNPJ</div><input type="text" id="rh-edit-doc" placeholder="000.000.000-00 ou 00.000.000/0000-00" style="width:100%;padding:9px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;"></div>';
            html+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">E-mail</div><input type="email" id="rh-edit-email" placeholder="email@empresa.com" style="width:100%;padding:9px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;"></div>';
            html+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">Telefone</div><input type="text" id="rh-edit-tel" placeholder="(11) 99999-9999" style="width:100%;padding:9px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;"></div>';
            html+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">Endereço</div><input type="text" id="rh-edit-end" placeholder="Rua, número, bairro, cidade" style="width:100%;padding:9px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;"></div>';
            html+='</div>';
            html+='<div style="display:flex;gap:10px;justify-content:flex-end;margin-top:18px;">';
            html+='<button onclick="document.getElementById(\'rh-edit-modal\').style.display=\'none\'" style="background:transparent;color:#aaa;border:1px solid rgba(255,255,255,0.1);padding:9px 16px;border-radius:8px;cursor:pointer;font-family:inherit;">Cancelar</button>';
            html+='<button onclick="window._rhSalvarEdit()" style="background:linear-gradient(135deg,#66cc00,#4d9900);color:#000;border:none;padding:9px 20px;border-radius:8px;font-weight:700;cursor:pointer;font-family:inherit;">Salvar</button>';
            html+='</div></div></div>';

            container.innerHTML = tabsHtml + html;

            window._rhOpenEdit = function(idx){
                var c = window._rhColabs[idx];
                if(!c) return;
                window._rhEditUser = c.username;
                document.getElementById('rh-edit-name').textContent = c.username;
                document.getElementById('rh-edit-entrada').value = c.dataEntrada || '';
                document.getElementById('rh-edit-cargo').value = c.cargo || '';
                var sel = document.getElementById('rh-edit-team');
                sel.value = c.team || '';
                document.getElementById('rh-edit-nome').value = c.nomeCompleto || '';
                document.getElementById('rh-edit-doc').value = c.documento || '';
                document.getElementById('rh-edit-email').value = c.emailPerfil || '';
                document.getElementById('rh-edit-tel').value = c.telefone || '';
                document.getElementById('rh-edit-end').value = c.endereco || '';
                document.getElementById('rh-edit-modal').style.display = 'flex';
            };
            window._rhSalvarEdit = async function(){
                if(!window._rhEditUser) return;
                var body = {
                    dataEntrada: document.getElementById('rh-edit-entrada').value || null,
                    cargo: document.getElementById('rh-edit-cargo').value,
                    team: document.getElementById('rh-edit-team').value,
                    nomeCompleto: document.getElementById('rh-edit-nome').value || null,
                    documento: document.getElementById('rh-edit-doc').value || null,
                    email: document.getElementById('rh-edit-email').value || null,
                    telefone: document.getElementById('rh-edit-tel').value || null,
                    endereco: document.getElementById('rh-edit-end').value || null
                };
                try{
                    var r = await fetch('/api/rh/perfil/'+window._rhEditUser, {method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
                    if(r.ok){
                        document.getElementById('rh-edit-modal').style.display='none';
                        showToast('Perfil salvo!');
                        loadRH('colaboradores');
                    } else {
                        var d = await r.json(); showToast(d.error||'Erro','error');
                    }
                }catch(e){showToast('Erro','error');}
            };
        }

        // ==============================
        // TAB: CALENDÁRIO
        // ==============================
        else if(window._rhTab === 'calendario'){
            var [fa, fo] = await Promise.all([fetch('/api/ferias/aprovadas').then(r=>r.json()), fetch('/api/folgas/aprovadas').then(r=>r.json())]);
            var allAprov = [...fa.map(function(f){return{...f,tipo:'Ferias'};}),...fo.map(function(f){return{...f,tipo:'Folga'};})];

            var yr = window._rhCalYear, mo = window._rhCalMonth;
            var mn=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
            var dim = new Date(yr,mo+1,0).getDate();
            var fd = new Date(yr,mo,1).getDay();

            // Mapear ausentes por dia
            var dayMap = {};
            allAprov.forEach(function(f){
                var s=new Date(f.startDate+'T00:00:00'),e=new Date(f.endDate+'T23:59:59');
                for(var d=new Date(s);d<=e;d.setDate(d.getDate()+1)){
                    if(d.getFullYear()===yr&&d.getMonth()===mo){
                        var k=d.getDate();
                        if(!dayMap[k])dayMap[k]=[];
                        dayMap[k].push({user:f.user,tipo:f.tipo,cargo:f.cargo||''});
                    }
                }
            });

            var calHtml = '<div style="max-width:900px;">';
            calHtml += '<div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">';
            calHtml += '<button onclick="window._rhCalYear='+yr+';window._rhCalMonth='+(mo-1<0?11:mo-1)+';if('+(mo-1<0)+')window._rhCalYear='+(yr-1)+';loadRH(\'calendario\')" style="background:none;border:1px solid rgba(255,255,255,0.1);color:#66cc00;cursor:pointer;padding:6px 12px;border-radius:6px;font-family:inherit;">‹</button>';
            calHtml += '<span style="color:#d0dcd2;font-size:15px;font-weight:600;min-width:160px;text-align:center;">'+mn[mo]+' '+yr+'</span>';
            calHtml += '<button onclick="window._rhCalYear='+yr+';window._rhCalMonth='+(mo+1>11?0:mo+1)+';if('+(mo+1>11)+')window._rhCalYear='+(yr+1)+';loadRH(\'calendario\')" style="background:none;border:1px solid rgba(255,255,255,0.1);color:#66cc00;cursor:pointer;padding:6px 12px;border-radius:6px;font-family:inherit;">›</button>';
            calHtml += '</div>';

            // Grade
            var today2=new Date();
            calHtml += '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:3px;margin-bottom:4px;">';
            ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'].forEach(function(d){calHtml+='<div style="text-align:center;color:#3a5040;font-size:10px;font-weight:700;padding:6px 0;">'+d+'</div>';});
            calHtml += '</div>';
            calHtml += '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:3px;">';
            for(var i=0;i<fd;i++) calHtml += '<div></div>';
            for(var day=1;day<=dim;day++){
                var isToday2=today2.getFullYear()===yr&&today2.getMonth()===mo&&today2.getDate()===day;
                var people = dayMap[day]||[];
                var hasPeople = people.length>0;
                var bg=isToday2?'rgba(102,204,0,0.12)':(hasPeople?'rgba(119,170,255,0.07)':'rgba(255,255,255,0.02)');
                var brd=isToday2?'1px solid rgba(102,204,0,0.5)':(hasPeople?'1px solid rgba(119,170,255,0.25)':'1px solid rgba(255,255,255,0.04)');
                calHtml += '<div style="background:'+bg+';border:'+brd+';border-radius:6px;padding:6px 4px;min-height:70px;">';
                calHtml += '<div style="color:'+(isToday2?'#66cc00':(hasPeople?'#d0dcd2':'#555'))+';font-size:11px;font-weight:'+(isToday2?'700':'400')+';margin-bottom:3px;">'+day+'</div>';
                people.slice(0,3).forEach(function(p){
                    var fn=p.user.split('.')[0];fn=fn.charAt(0).toUpperCase()+fn.slice(1);
                    var tc=p.tipo==='Ferias'?'#7aaaff':'#ff9944';
                    calHtml += '<div style="background:rgba('+(p.tipo==='Ferias'?'119,170,255':'255,153,68')+',0.15);color:'+tc+';border-radius:3px;padding:1px 4px;font-size:8px;font-weight:600;margin-bottom:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="'+p.user+(p.cargo?' ('+p.cargo+')':'')+'">'+fn+'</div>';
                });
                if(people.length>3) calHtml += '<div style="color:#555;font-size:8px;padding:1px 4px;">+' +(people.length-3)+' mais</div>';
                calHtml += '</div>';
            }
            calHtml += '</div>';

            // Legenda
            calHtml += '<div style="display:flex;gap:16px;margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);">';
            calHtml += '<div style="display:flex;align-items:center;gap:5px;font-size:10px;color:#7aaaff;"><div style="width:10px;height:10px;border-radius:2px;background:rgba(119,170,255,0.25);"></div>Férias</div>';
            calHtml += '<div style="display:flex;align-items:center;gap:5px;font-size:10px;color:#ff9944;"><div style="width:10px;height:10px;border-radius:2px;background:rgba(255,153,68,0.25);"></div>Folga</div>';
            calHtml += '</div></div>';

            container.innerHTML = tabsHtml + calHtml;
        }

        // ==============================
        // TAB: RELATÓRIOS
        // ==============================
        else if(window._rhTab === 'relatorios'){
            var [fa2,fo2,colabs2] = await Promise.all([
                fetch('/api/ferias/aprovadas').then(r=>r.json()),
                fetch('/api/folgas/aprovadas').then(r=>r.json()),
                fetch('/api/rh/colaboradores').then(r=>r.json())
            ]);

            var html2='<div style="max-width:900px;">';

            // Export CSV
            html2+='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;margin-bottom:24px;">';
            html2+='<div class="sec-label" style="margin-bottom:14px;">Exportar CSV</div>';
            html2+='<div style="display:flex;gap:10px;flex-wrap:wrap;">';
            html2+='<a href="/api/rh/export/csv?tipo=all" download="ausencias.csv" style="background:rgba(102,204,0,0.1);color:#66cc00;border:1px solid rgba(102,204,0,0.3);padding:10px 18px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:600;">&#128229; Todas as Ausências</a>';
            html2+='<a href="/api/rh/export/csv?tipo=ferias" download="ferias.csv" style="background:rgba(119,170,255,0.1);color:#7aaaff;border:1px solid rgba(119,170,255,0.3);padding:10px 18px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:600;">&#127958; Somente Férias</a>';
            html2+='<a href="/api/rh/export/csv?tipo=folgas" download="folgas.csv" style="background:rgba(255,153,68,0.1);color:#ff9944;border:1px solid rgba(255,153,68,0.3);padding:10px 18px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:600;">&#128197; Somente Folgas</a>';
            html2+='</div></div>';

            // Saldo de férias por colaborador
            html2+='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;margin-bottom:24px;">';
            html2+='<div class="sec-label" style="margin-bottom:14px;">Saldo de Férias por Colaborador</div>';
            html2+='<div style="font-size:10px;color:#555;margin-bottom:12px;">Política: 30 dias/ano (PJ) · 20 dias fim de ano (dez/jan) · 10 dias durante o ano · Direito após 1 ano</div>';
            var colabsComDireito=colabs2.filter?colabs2.filter(function(c){return c.saldo&&c.saldo.hasRight;}):[];
            var colabsSemDireito=colabs2.filter?colabs2.filter(function(c){return c.saldo&&!c.saldo.hasRight;}):[];
            var colabsSemEntrada=colabs2.filter?colabs2.filter(function(c){return !c.saldo;}):[];
            if(colabsComDireito.length>0){
                html2+='<table style="width:100%;border-collapse:collapse;font-size:11px;margin-bottom:16px;">';
                html2+='<thead><tr style="background:rgba(255,255,255,0.03);"><th style="text-align:left;padding:8px 10px;color:#3a5040;font-size:9px;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);">Colaborador</th><th style="text-align:left;padding:8px 10px;color:#3a5040;font-size:9px;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);">Time</th><th style="text-align:center;padding:8px 10px;color:#7aaaff;font-size:9px;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);">Fim Ano (20d)</th><th style="text-align:center;padding:8px 10px;color:#66cc00;font-size:9px;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);">Durante Ano (10d)</th><th style="text-align:center;padding:8px 10px;color:#ffcc00;font-size:9px;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);">Total Restante</th></tr></thead><tbody>';
                colabsComDireito.forEach(function(c){
                    var rem=c.saldo.remaining;var color=rem<=5?'#ff6060':(rem<=10?'#ffcc00':'#66cc00');
                    html2+='<tr style="border-bottom:1px solid rgba(255,255,255,0.04);">';
                    html2+='<td style="padding:9px 10px;"><div style="color:#d0dcd2;font-size:12px;">'+c.username+'</div><div style="color:#3a5040;font-size:9px;">'+tenureStr(c.tenureDays)+'</div></td>';
                    html2+='<td style="padding:9px 10px;color:#888;font-size:11px;">'+(c.team||'—')+'</td>';
                    html2+='<td style="padding:9px 10px;text-align:center;"><span style="color:#7aaaff;font-weight:700;font-size:13px;">'+c.saldo.fimAno.remaining+'</span><span style="color:#555;font-size:9px;">/20</span></td>';
                    html2+='<td style="padding:9px 10px;text-align:center;"><span style="color:#66cc00;font-weight:700;font-size:13px;">'+c.saldo.durante.remaining+'</span><span style="color:#555;font-size:9px;">/10</span></td>';
                    html2+='<td style="padding:9px 10px;text-align:center;"><span style="color:'+color+';font-weight:700;font-size:15px;">'+rem+'</span><span style="color:#555;font-size:9px;">/30</span></td>';
                    html2+='</tr>';
                });
                html2+='</tbody></table>';
            }
            if(colabsSemDireito.length>0){
                html2+='<div style="color:#555;font-size:11px;margin-bottom:6px;">Sem direito ainda (menos de 1 ano):</div>';
                html2+='<div style="display:flex;flex-wrap:wrap;gap:6px;">';
                colabsSemDireito.forEach(function(c){html2+='<span style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:4px 8px;font-size:10px;color:#666;">'+c.username+' <span style="color:#444;">('+Math.ceil(c.saldo.daysUntilRight/30)+'m)</span></span>';});
                html2+='</div>';
            }
            html2+='</div>';

            // Stats por time
            html2+='<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;">';
            html2+='<div class="sec-label" style="margin-bottom:14px;">Ausências no Ano por Time</div>';
            var teamYear={};var anoAtual=new Date().getFullYear();
            [...fa2,...fo2].forEach(function(f){var t=f.team||'Sem time';var y=parseInt((f.startDate||'').split('-')[0]);if(y===anoAtual){if(!teamYear[t])teamYear[t]={ferias:0,folgas:0,dias:0};if(fa2.includes(f))teamYear[t].ferias++;else teamYear[t].folgas++;var s=new Date(f.startDate+'T00:00:00'),e=new Date(f.endDate+'T00:00:00');teamYear[t].dias+=Math.round((e-s)/(1000*60*60*24))+1;}});
            if(Object.keys(teamYear).length>0){
                html2+='<table style="width:100%;border-collapse:collapse;font-size:11px;">';
                html2+='<thead><tr style="background:rgba(255,255,255,0.03);"><th style="text-align:left;padding:8px 10px;color:#3a5040;font-size:9px;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);">Time</th><th style="text-align:center;padding:8px 10px;color:#7aaaff;font-size:9px;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);">Férias</th><th style="text-align:center;padding:8px 10px;color:#ff9944;font-size:9px;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);">Folgas</th><th style="text-align:center;padding:8px 10px;color:#66cc00;font-size:9px;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);">Total Dias</th></tr></thead><tbody>';
                Object.entries(teamYear).sort(function(a,b){return b[1].dias-a[1].dias;}).forEach(function(e){html2+='<tr style="border-bottom:1px solid rgba(255,255,255,0.04);"><td style="padding:9px 10px;color:#d0dcd2;font-size:12px;">'+e[0]+'</td><td style="padding:9px 10px;text-align:center;color:#7aaaff;">'+e[1].ferias+'</td><td style="padding:9px 10px;text-align:center;color:#ff9944;">'+e[1].folgas+'</td><td style="padding:9px 10px;text-align:center;color:#66cc00;font-weight:700;">'+e[1].dias+'d</td></tr>';});
                html2+='</tbody></table>';
            } else { html2+='<div style="color:#555;font-size:12px;text-align:center;padding:16px;">Sem dados para o ano atual.</div>'; }
            html2+='</div></div>';

            container.innerHTML = tabsHtml + html2;
        }


        // ==============================
        // TAB: COMPRAS (RH)
        // ==============================
        else if(window._rhTab === 'compras'){
            var allCompras = await (await fetch('/api/compras')).json();
            function fmtD2(d){if(!d)return'';var p=d.split('-');return p[2]+'/'+p[1]+'/'+p[0];}
            function fmtDT2(iso){if(!iso)return'';var d=new Date(iso);return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric',timeZone:'America/Sao_Paulo'});}
            function fmtBRL2(v){if(!v&&v!==0)return'\u2014';return'R$ '+parseFloat(v).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});}
            function urgBadge2(u){var c=u==='Alta'?'#ff4444':u==='Media'?'#ffcc00':'#66cc00';var dot=u==='Alta'?'&#128308;':u==='Media'?'&#128993;':'&#128994;';return '<span style="color:'+c+';font-size:9px;font-weight:700;">'+dot+' '+u+'</span>';}

            var pendentes2 = allCompras.filter(function(c){return c.status==='pendente';});
            var aprovadas2 = allCompras.filter(function(c){return c.status==='aprovado';});
            var rejeitadas2 = allCompras.filter(function(c){return c.status==='rejeitado';});
            var compradas2 = allCompras.filter(function(c){return c.status==='comprado';});

            var rhc = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin-bottom:24px;">';
            [{label:'Pendentes',value:pendentes2.length,color:'#ffcc00',icon:'&#9203;'},{label:'Aprovadas',value:aprovadas2.length,color:'#66cc00',icon:'&#9989;'},{label:'Recusadas',value:rejeitadas2.length,color:'#ff4444',icon:'&#10060;'},{label:'Compradas',value:compradas2.length,color:'#7aaaff',icon:'&#128717;'}].forEach(function(c){rhc+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-top:3px solid '+c.color+';border-radius:12px;padding:12px 14px;"><div style="font-size:18px;margin-bottom:4px;">'+c.icon+'</div><div style="font-size:24px;font-weight:700;color:'+c.color+';">'+c.value+'</div><div style="color:#888;font-size:11px;margin-top:1px;">'+c.label+'</div></div>';});
            rhc += '</div>';

            var aguardandoRH = allCompras.filter(function(c){return c.status==='aguardando_rh';}).sort(function(a,b){return new Date(b.requestedAt||0)-new Date(a.requestedAt||0);});
            var historicoRH = allCompras.filter(function(c){return c.status!=='aguardando_rh'&&c.status!=='pendente';}).sort(function(a,b){return new Date(b.requestedAt||0)-new Date(a.requestedAt||0);});
            var sorted2 = aguardandoRH.concat(historicoRH);
            rhc += '<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden;">';
            rhc += '<div style="display:grid;grid-template-columns:120px 1fr 80px 90px 100px 180px;gap:0;padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.03);">';
            ['Solicitante','Produto / Motivo','Urg\u00eancia','Valor','Status','A\u00e7\u00f5es'].forEach(function(h){rhc+='<div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">'+h+'</div>';});
            rhc += '</div>';

            if(sorted2.length===0){rhc+='<div style="padding:30px;text-align:center;color:#555;font-size:13px;">Nenhuma solicita\u00e7\u00e3o de compra.</div>';}
            else{sorted2.forEach(function(c){
                var sc=c.status==='aprovado'?'#66cc00':c.status==='comprado'?'#7aaaff':c.status==='rejeitado'?'#ff4444':c.status==='aguardando_rh'?'#cc88ff':'#ffcc00';
                var sl=c.status==='aprovado'?'✓ Aprovado':c.status==='comprado'?'✓ Comprado':c.status==='rejeitado'?'✗ Recusado':c.status==='aguardando_rh'?'⏳ Aguardando RH':'⏳ Aguard. Líder';
                var actions='';
                if(c.status==='aguardando_rh'){actions='<button onclick="window._rhAprovarCompra('+c.id+')" style="background:rgba(102,204,0,0.12);border:1px solid #66cc00;color:#66cc00;padding:4px 9px;border-radius:5px;cursor:pointer;font-size:10px;font-family:inherit;font-weight:600;">\u2713 Aprovar</button> <button onclick="window._rhRejeitarCompra('+c.id+')" style="background:rgba(255,68,68,0.1);border:1px solid #ff4444;color:#ff4444;padding:4px 9px;border-radius:5px;cursor:pointer;font-size:10px;font-family:inherit;">\u2717 Recusar</button>';}
                else if(c.status==='rejeitado'&&c.rejectionReason){actions='<span style="color:#555;font-size:9px;font-style:italic;">'+c.rejectionReason+'</span>';}
                rhc+='<div style="display:grid;grid-template-columns:120px 1fr 80px 90px 100px 180px;gap:0;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.04);align-items:start;">';
                rhc+='<div><div style="color:#d0dcd2;font-size:11px;font-weight:500;">'+c.user+'</div><div style="color:#555;font-size:9px;">'+(c.team||'')+'</div><div style="color:#444;font-size:9px;">'+(c.cargo||'')+'</div><div style="color:#3a5040;font-size:9px;margin-top:2px;">'+fmtDT2(c.requestedAt)+'</div></div>';
                rhc+='<div><div style="color:#d0dcd2;font-size:12px;font-weight:500;">'+c.produto+'</div><div style="color:#888;font-size:10px;margin-top:2px;line-height:1.4;">'+c.motivo+'</div>'+(c.link?'<a href="'+c.link+'" target="_blank" style="color:#66cc00;font-size:10px;text-decoration:none;">&#128279; Link</a>':'')+'</div>';
                rhc+='<div>'+urgBadge2(c.urgencia)+'</div>';
                rhc+='<div style="color:#66cc00;font-size:12px;font-weight:600;">'+fmtBRL2(c.valor)+'</div>';
                rhc+='<div><span style="color:'+sc+';font-size:10px;font-weight:600;">'+sl+'</span></div>';
                rhc+='<div style="display:flex;gap:5px;flex-wrap:wrap;">'+actions+'</div>';
                rhc+='</div>';
            });}
            rhc += '</div>';
            container.innerHTML = tabsHtml + rhc;

            window._rhAprovarCompra = async function(id){
                try{var r=await fetch('/api/compras/aprovar/'+id,{method:'POST'});if(r.ok){showToast('Aprovado!');loadRH('compras');}else{var d=await r.json();showToast(d.error||'Erro','error');}}catch(e){showToast('Erro','error');}
            };
            window._rhRejeitarCompra = function(id){
                window._pendingRejeitarCompraId=id;
                document.getElementById('compra-reject-reason').value='';
                document.getElementById('compra-rejeitar-modal').classList.add('active');
                window.confirmRejeitarCompra = async function(){
                    var reason=document.getElementById('compra-reject-reason').value.trim();
                    if(!reason){showToast('Informe o motivo','error');return;}
                    try{var r=await fetch('/api/compras/rejeitar/'+window._pendingRejeitarCompraId,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rejectionReason:reason})});
                    if(r.ok){document.getElementById('compra-rejeitar-modal').classList.remove('active');showToast('Recusado.');loadRH('compras');}
                    else{var d=await r.json();showToast(d.error||'Erro','error');}
                    }catch(e){showToast('Erro','error');}
                };
            };
        }

        // ==============================
        // TAB: ADQUIRIDAS (RH)
        // ==============================
        else if(window._rhTab === 'adquiridas'){
            var allC2 = await (await fetch('/api/compras')).json();
            function fmtD3(d){if(!d)return'';var p=d.split('-');return p[2]+'/'+p[1]+'/'+p[0];}
            function fmtDT3(iso){if(!iso)return'—';var d=new Date(iso);return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric',timeZone:'America/Sao_Paulo'});}
            function fmtBRL3(v){if(!v&&v!==0)return'—';return'R$ '+parseFloat(v).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});}

            var adquiridas = allC2.filter(function(c){return c.status==='aprovado'||c.status==='comprado';}).sort(function(a,b){return new Date(b.approvedAt||0)-new Date(a.approvedAt||0);});
            var totalInvestido = adquiridas.filter(function(c){return c.status==='comprado';}).reduce(function(acc,c){return acc+(c.valorFinal||c.valor||0);},0);
            var totalAprovado = adquiridas.filter(function(c){return c.status==='aprovado';}).reduce(function(acc,c){return acc+(c.valor||0);},0);

            var adqHtml = '';
            // Resumo
            adqHtml += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:24px;">';
            adqHtml += '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-top:3px solid #66cc00;border-radius:12px;padding:14px;"><div style="font-size:20px;margin-bottom:4px;">&#128717;</div><div style="font-size:22px;font-weight:700;color:#66cc00;">'+fmtBRL3(totalInvestido)+'</div><div style="color:#888;font-size:11px;margin-top:2px;">Total Investido</div></div>';
            adqHtml += '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-top:3px solid #ffcc00;border-radius:12px;padding:14px;"><div style="font-size:20px;margin-bottom:4px;">&#9203;</div><div style="font-size:22px;font-weight:700;color:#ffcc00;">'+fmtBRL3(totalAprovado)+'</div><div style="color:#888;font-size:11px;margin-top:2px;">A Comprar (aprovadas)</div></div>';
            adqHtml += '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-top:3px solid #7aaaff;border-radius:12px;padding:14px;"><div style="font-size:20px;margin-bottom:4px;">&#128203;</div><div style="font-size:22px;font-weight:700;color:#7aaaff;">'+adquiridas.length+'</div><div style="color:#888;font-size:11px;margin-top:2px;">Total Itens</div></div>';
            adqHtml += '</div>';

            // Tabela
            adqHtml += '<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden;">';
            adqHtml += '<div style="display:grid;grid-template-columns:140px 1fr 100px 100px 100px 110px 170px;gap:0;padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.03);">';
            ['Solicitante','Produto','Dt. Solicita\u00e7\u00e3o','Dt. Compra','Valor Orig.','Valor Final','A\u00e7\u00e3o'].forEach(function(h){adqHtml+='<div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">'+h+'</div>';});
            adqHtml += '</div>';

            if(adquiridas.length===0){adqHtml+='<div style="padding:30px;text-align:center;color:#555;font-size:13px;">Nenhuma compra aprovada ainda.</div>';}
            else{adquiridas.forEach(function(c,ci){
                var isComprado = c.status==='comprado';
                var sc = isComprado?'#7aaaff':'#ffcc00';
                var sl = isComprado?'&#128717; Comprado':'&#9203; Aprovado';
                var actionHtml = '';
                if(!isComprado){
                    actionHtml = '<div style="display:flex;flex-direction:column;gap:5px;">';
                    actionHtml += '<input type="number" id="vf-'+c.id+'" placeholder="Valor final" value="'+c.valor+'" min="0" step="0.01" style="padding:5px 7px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:6px;font-size:11px;font-family:inherit;width:100%;box-sizing:border-box;">';
                    actionHtml += '<button onclick="window._marcarComprado('+c.id+')" style="background:rgba(119,170,255,0.12);border:1px solid #7aaaff;color:#7aaaff;padding:5px 8px;border-radius:6px;cursor:pointer;font-size:10px;font-family:inherit;font-weight:600;">&#128717; Marcar Comprado</button>';
                    actionHtml += '</div>';
                } else {
                    actionHtml = '<span style="color:#555;font-size:10px;">Comprado por '+c.compradoPor+'</span>';
                }
                adqHtml+='<div style="display:grid;grid-template-columns:140px 1fr 100px 100px 100px 110px 170px;gap:0;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.04);align-items:start;">';
                adqHtml+='<div><div style="color:#d0dcd2;font-size:11px;font-weight:500;">'+c.user+'</div><div style="color:#555;font-size:9px;">'+(c.team||'')+'</div><div style="color:'+sc+';font-size:9px;margin-top:3px;font-weight:600;">'+sl+'</div></div>';
                adqHtml+='<div><div style="color:#d0dcd2;font-size:12px;font-weight:500;">'+c.produto+'</div>'+(c.link?'<a href="'+c.link+'" target="_blank" style="color:#66cc00;font-size:10px;text-decoration:none;">&#128279; Link</a>':'')+'</div>';
                adqHtml+='<div style="color:#aaa;font-size:11px;">'+fmtDT3(c.requestedAt)+'</div>';
                adqHtml+='<div style="color:#aaa;font-size:11px;">'+(isComprado?fmtDT3(c.compradoAt):'—')+'</div>';
                adqHtml+='<div style="color:#888;font-size:11px;">'+fmtBRL3(c.valor)+'</div>';
                adqHtml+='<div style="color:#66cc00;font-size:12px;font-weight:600;">'+(isComprado?fmtBRL3(c.valorFinal||c.valor):'—')+'</div>';
                adqHtml+=actionHtml;
                adqHtml+='</div>';
            });}
            // Rodapé com total
            adqHtml += '<div style="padding:12px 14px;background:rgba(255,255,255,0.02);display:flex;justify-content:flex-end;gap:24px;">';
            adqHtml += '<div style="color:#888;font-size:11px;">Total investido: <strong style="color:#66cc00;">'+fmtBRL3(totalInvestido)+'</strong></div>';
            adqHtml += '<div style="color:#888;font-size:11px;">Pendente de compra: <strong style="color:#ffcc00;">'+fmtBRL3(totalAprovado)+'</strong></div>';
            adqHtml += '</div></div>';

            container.innerHTML = tabsHtml + adqHtml;

            window._marcarComprado = async function(id){
                var inp = document.getElementById('vf-'+id);
                var vf = inp ? parseFloat(inp.value)||0 : 0;
                try{var r=await fetch('/api/compras/comprado/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({valorFinal:vf})});if(r.ok){showToast('Marcado como comprado!');loadRH('adquiridas');}else{var d=await r.json();showToast(d.error||'Erro','error');}}catch(e){showToast('Erro','error');}
            };
        }


        // ==============================
        // TAB: BENEFÍCIOS
        // ==============================
        else if(window._rhTab === 'beneficios'){
            var bData = await (await fetch('/api/rh/beneficios')).json();
            if(bData.error){ container.innerHTML=tabsHtml+'<div style="color:#ff4444;padding:20px;">'+bData.error+'</div>'; return; }

            function fmtBRL4(v){if(v==null||v===undefined)return'\u2014';return'R\u00a0'+parseFloat(v).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});}
            var nomesMeses4={'01':'Jan','02':'Fev','03':'Mar','04':'Abr','05':'Mai','06':'Jun','07':'Jul','08':'Ago','09':'Set','10':'Out','11':'Nov','12':'Dez'};
            function fmtMes4(ch){var p=ch.split('-');return nomesMeses4[p[1]]+'/'+p[0].slice(2);}

            var hoje4=new Date();
            var chaveAtual4=hoje4.getFullYear()+'-'+String(hoje4.getMonth()+1).padStart(2,'0');
            var todosMeses4=new Set();
            Object.values(bData).forEach(function(b){if(b.meses)Object.keys(b.meses).forEach(function(m){todosMeses4.add(m);});});
            var mesesList4=Array.from(todosMeses4).sort();
            var mesesShow4=mesesList4.slice(-4);

            var totalMesAtual4=0,totalAcumulado4=0,countAtivos4=0;
            Object.values(bData).forEach(function(b){
                if(b.status==='ATIVO')countAtivos4++;
                if(b.meses){if(b.meses[chaveAtual4])totalMesAtual4+=b.meses[chaveAtual4];Object.values(b.meses).forEach(function(v){if(v)totalAcumulado4+=v;});}
            });

            var benHtml='';
            benHtml+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px;">';
            benHtml+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-top:3px solid #66cc00;border-radius:12px;padding:14px;"><div style="font-size:20px;margin-bottom:4px;">&#128176;</div><div style="font-size:18px;font-weight:700;color:#66cc00;">'+fmtBRL4(totalMesAtual4)+'</div><div style="color:#888;font-size:11px;margin-top:2px;">Total Este M\u00eas</div></div>';
            benHtml+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-top:3px solid #7aaaff;border-radius:12px;padding:14px;"><div style="font-size:20px;margin-bottom:4px;">&#128101;</div><div style="font-size:22px;font-weight:700;color:#7aaaff;">'+countAtivos4+'</div><div style="color:#888;font-size:11px;margin-top:2px;">Colaboradores Ativos</div></div>';
            benHtml+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-top:3px solid #ffcc00;border-radius:12px;padding:14px;"><div style="font-size:20px;margin-bottom:4px;">&#128200;</div><div style="font-size:18px;font-weight:700;color:#ffcc00;">'+fmtBRL4(totalAcumulado4)+'</div><div style="color:#888;font-size:11px;margin-top:2px;">Total Acumulado</div></div>';
            benHtml+='</div>';

            benHtml+='<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;font-size:11px;min-width:800px;">';
            benHtml+='<thead><tr style="background:rgba(255,255,255,0.03);">';
            var bThs=['Colaborador','Tipo','Tipo VT','VT','Estac.','Academia','Aliment.'];
            mesesShow4.forEach(function(m){bThs.push(fmtMes4(m));});bThs.push('A\u00e7\u00e3o');
            bThs.forEach(function(h){benHtml+='<th style="text-align:left;padding:8px 10px;color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,0.06);white-space:nowrap;">'+h+'</th>';});
            benHtml+='</tr></thead><tbody>';
            window._benData=bData;
            Object.keys(bData).sort().forEach(function(uname){
                var b=bData[uname];
                var sColor=b.status==='ATIVO'?'#66cc00':'#ff4444';
                benHtml+='<tr style="border-bottom:1px solid rgba(255,255,255,0.04);">';
                benHtml+='<td style="padding:8px 10px;"><div style="color:#d0dcd2;font-weight:500;font-size:11px;">'+uname+'</div>'+(b.nomeCompleto?'<div style="color:#3a5040;font-size:9px;">'+b.nomeCompleto+'</div>':'')+'</td>';
                benHtml+='<td style="padding:8px 10px;"><span style="color:'+sColor+';font-size:10px;font-weight:600;">'+(b.tipoContrato||'\u2014')+'</span></td>';
                benHtml+='<td style="padding:8px 10px;color:#888;font-size:10px;">'+(b.tipoVT||'\u2014')+'</td>';
                benHtml+='<td style="padding:8px 10px;color:#d0dcd2;">'+fmtBRL4(b.deslocamento)+'</td>';
                benHtml+='<td style="padding:8px 10px;color:#d0dcd2;">'+(b.estacionamento!=null?fmtBRL4(b.estacionamento):'\u2014')+'</td>';
                benHtml+='<td style="padding:8px 10px;color:#d0dcd2;">'+fmtBRL4(b.academia)+'</td>';
                benHtml+='<td style="padding:8px 10px;color:#d0dcd2;">'+fmtBRL4(b.alimentacao)+'</td>';
                mesesShow4.forEach(function(m){
                    var v=b.meses&&b.meses[m]!=null?b.meses[m]:null;
                    var isAt=m===chaveAtual4;
                    benHtml+='<td style="padding:8px 10px;'+(isAt?'background:rgba(102,204,0,0.04);':'')+'">';
                    if(v!=null)benHtml+='<span style="color:'+(isAt?'#66cc00':'#d0dcd2')+';font-weight:'+(isAt?'700':'400')+';">'+fmtBRL4(v)+'</span>';
                    else benHtml+='<span style="color:#333;">\u2014</span>';
                    benHtml+='</td>';
                });
                benHtml+='<td style="padding:8px 10px;"><button onclick="window._openBenEdit(\''+uname+'\')" style="background:rgba(102,204,0,0.08);color:#66cc00;border:1px solid rgba(102,204,0,0.25);padding:5px 10px;border-radius:6px;cursor:pointer;font-size:10px;font-family:inherit;">\u270e Editar</button></td>';
                benHtml+='</tr>';
            });
            benHtml+='</tbody></table></div>';
            benHtml+='<div style="margin-top:14px;"><button onclick="window._openBenEdit(null)" style="background:rgba(102,204,0,0.1);color:#66cc00;border:1px solid rgba(102,204,0,0.3);padding:9px 18px;border-radius:8px;cursor:pointer;font-size:12px;font-family:inherit;font-weight:600;">+ Adicionar Colaborador</button></div>';

            // Modal benefícios
            benHtml+='<div id="ben-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.78);z-index:9999;align-items:flex-start;justify-content:center;overflow-y:auto;padding:24px 0;">';
            benHtml+='<div style="background:#080d09;border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:24px;width:520px;max-width:96vw;margin:auto;">';
            benHtml+='<h3 style="color:#66cc00;margin-bottom:16px;font-size:15px;">&#128176; Ben\u00e9ficios \u2014 <span id="ben-edit-name" style="color:#d0dcd2;font-weight:400;"></span></h3>';
            benHtml+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">';
            [['ben-username','Usu\u00e1rio (chave)','text','username'],['ben-nome','Nome Completo','text','Nome completo'],['ben-cnpj','CNPJ Contratado','text','00.000.000/0000-00'],['ben-data','Data do Contrato','date',''],['ben-status','Status','select',''],['ben-tcontrato','Tipo de Contrato','select',''],['ben-tvt','Tipo de VT','text','ex: Transporte p\u00fablico'],['ben-deslocamento','Deslocamento (R$)','number','0.00'],['ben-estac','Estacionamento (R$)','number','0.00'],['ben-academia','Academia (R$)','number','0.00'],['ben-aliment','Alimenta\u00e7\u00e3o (R$)','number','0.00']].forEach(function(field){
                var id=field[0],lbl=field[1],tp=field[2],ph=field[3];
                if(tp==='select'&&id==='ben-status'){
                    benHtml+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">'+lbl+'</div><select id="'+id+'" style="width:100%;padding:9px 10px;background:#0a120b;border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;font-size:12px;"><option>ATIVO</option><option>INATIVO</option></select></div>';
                } else if(tp==='select'&&id==='ben-tcontrato'){
                    benHtml+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">'+lbl+'</div><select id="'+id+'" style="width:100%;padding:9px 10px;background:#0a120b;border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;font-size:12px;"><option>PJ</option><option>CLT</option></select></div>';
                } else {
                    benHtml+='<div><div style="color:#aaa;font-size:11px;margin-bottom:4px;">'+lbl+'</div><input type="'+tp+'" id="'+id+'" placeholder="'+ph+'" style="width:100%;padding:9px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;box-sizing:border-box;font-family:inherit;font-size:12px;"'+(tp==='number'?' step="0.01"':'')+' ></div>';
                }
            });
            benHtml+='</div>';
            // Seção meses
            benHtml+='<div style="margin-top:16px;"><div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:10px;">Hist\u00f3rico Mensal (total pago)</div>';
            benHtml+='<div id="ben-meses-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;"></div>';
            benHtml+='<div style="display:flex;gap:8px;margin-top:10px;align-items:center;">';
            benHtml+='<input type="month" id="ben-new-mes" style="padding:7px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;font-family:inherit;font-size:11px;">';
            benHtml+='<input type="number" id="ben-new-val" placeholder="Valor R$" step="0.01" style="width:130px;padding:7px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:#d0dcd2;border-radius:8px;font-family:inherit;font-size:11px;">';
            benHtml+='<button onclick="window._benAdicionarMes()" style="background:rgba(102,204,0,0.1);color:#66cc00;border:1px solid rgba(102,204,0,0.3);padding:7px 12px;border-radius:8px;cursor:pointer;font-size:11px;font-family:inherit;">+ Adicionar</button>';
            benHtml+='</div></div>';
            benHtml+='<div style="display:flex;gap:10px;justify-content:flex-end;margin-top:18px;">';
            benHtml+='<button onclick="document.getElementById(\'ben-modal\').style.display=\'none\'" style="background:transparent;color:#aaa;border:1px solid rgba(255,255,255,0.1);padding:9px 16px;border-radius:8px;cursor:pointer;font-family:inherit;">Cancelar</button>';
            benHtml+='<button onclick="window._salvarBen()" style="background:linear-gradient(135deg,#66cc00,#4d9900);color:#000;border:none;padding:9px 20px;border-radius:8px;font-weight:700;cursor:pointer;font-family:inherit;">Salvar</button>';
            benHtml+='</div></div></div>';

            container.innerHTML=tabsHtml+benHtml;

            window._benMeses={};
            function renderBenMeses(){
                var g=document.getElementById('ben-meses-grid');if(!g)return;
                var html2='';
                Object.keys(window._benMeses).sort().forEach(function(m){
                    var p=m.split('-');var label=(nomesMeses4[p[1]]||p[1])+'/'+p[0].slice(2);
                    html2+='<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;">';
                    html2+='<span style="color:#888;font-size:10px;">'+label+'</span>';
                    html2+='<span style="color:#66cc00;font-size:11px;font-weight:600;">'+fmtBRL4(window._benMeses[m])+'</span>';
                    html2+='<button onclick="delete window._benMeses[\''+m+'\'];renderBenMeses();" style="background:none;border:none;color:#555;cursor:pointer;font-size:12px;padding:0 2px;">\u00d7</button>';
                    html2+='</div>';
                });
                g.innerHTML=html2||'<span style="color:#444;font-size:11px;grid-column:span 3;">Nenhum m\u00eas registrado</span>';
            }
            window._benAdicionarMes=function(){
                var m=document.getElementById('ben-new-mes').value;
                var v=parseFloat(document.getElementById('ben-new-val').value);
                if(!m||isNaN(v)){showToast('Informe m\u00eas e valor','error');return;}
                window._benMeses[m]=v;
                renderBenMeses();
                document.getElementById('ben-new-val').value='';
            };
            window._openBenEdit=function(uname){
                var b=uname&&window._benData[uname]?window._benData[uname]:{};
                document.getElementById('ben-edit-name').textContent=uname||'Novo';
                document.getElementById('ben-username').value=uname||'';
                document.getElementById('ben-nome').value=b.nomeCompleto||'';
                document.getElementById('ben-cnpj').value=b.cnpjContratado||'';
                document.getElementById('ben-data').value=b.dataContrato||'';
                document.getElementById('ben-status').value=b.status||'ATIVO';
                document.getElementById('ben-tcontrato').value=b.tipoContrato||'PJ';
                document.getElementById('ben-tvt').value=b.tipoVT||'';
                document.getElementById('ben-deslocamento').value=b.deslocamento!=null?b.deslocamento:'';
                document.getElementById('ben-estac').value=b.estacionamento!=null?b.estacionamento:'';
                document.getElementById('ben-academia').value=b.academia!=null?b.academia:'';
                document.getElementById('ben-aliment').value=b.alimentacao!=null?b.alimentacao:'';
                window._benMeses=b.meses?Object.assign({},b.meses):{};
                window._benEditKey=uname;
                renderBenMeses();
                document.getElementById('ben-modal').style.display='flex';
            };
            window._salvarBen=async function(){
                var key=document.getElementById('ben-username').value.trim();
                if(!key){showToast('Informe o usu\u00e1rio','error');return;}
                var body={
                    nomeCompleto:document.getElementById('ben-nome').value||null,
                    cnpjContratado:document.getElementById('ben-cnpj').value||null,
                    dataContrato:document.getElementById('ben-data').value||null,
                    status:document.getElementById('ben-status').value,
                    tipoContrato:document.getElementById('ben-tcontrato').value,
                    tipoVT:document.getElementById('ben-tvt').value||null,
                    deslocamento:document.getElementById('ben-deslocamento').value!==''?parseFloat(document.getElementById('ben-deslocamento').value):null,
                    estacionamento:document.getElementById('ben-estac').value!==''?parseFloat(document.getElementById('ben-estac').value):null,
                    academia:document.getElementById('ben-academia').value!==''?parseFloat(document.getElementById('ben-academia').value):null,
                    alimentacao:document.getElementById('ben-aliment').value!==''?parseFloat(document.getElementById('ben-aliment').value):null,
                    meses:window._benMeses
                };
                try{
                    var r=await fetch('/api/rh/beneficios/'+encodeURIComponent(key),{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
                    if(r.ok){document.getElementById('ben-modal').style.display='none';showToast('Ben\u00e9ficio salvo!');loadRH('beneficios');}
                    else{var d=await r.json();showToast(d.error||'Erro','error');}
                }catch(e){showToast('Erro','error');}
            };
        }
    } catch(e) {
        var container2 = document.getElementById('rh-main');
        if(container2) container2.innerHTML='<div style="color:#ff4444;padding:20px;">Erro: '+e.message+'</div>';
    }
};

window._lideresCalYear = window._lideresCalYear || new Date().getFullYear();
window._lideresCalMonth = (window._lideresCalMonth !== undefined && window._lideresCalMonth !== null) ? window._lideresCalMonth : new Date().getMonth();
window._lideresTeam = window._lideresTeam !== undefined ? window._lideresTeam : '';

window.loadLideresView = async function(teamOverride) {
    if(teamOverride !== undefined) window._lideresTeam = teamOverride || '';
    var container = document.getElementById('lideres-main');
    if(!container) return;
    container.innerHTML = '<div style="color:#3a5040;font-size:13px;padding:20px;">Carregando...</div>';
    try {
        var url = '/api/lideres/dashboard';
        if(window._lideresTeam) url += '?team=' + encodeURIComponent(window._lideresTeam);
        var data = await (await fetch(url)).json();
        if(data.error){ container.innerHTML = '<div style="color:#ff4444;padding:20px;">'+data.error+'</div>'; return; }
        var _comprasResp = await fetch('/api/compras');
        var _comprasAll = await _comprasResp.json();
        var _comprasPend = Array.isArray(_comprasAll) ? _comprasAll.filter(function(c){return c.status==='pendente'&&c.user!==myUser;}) : [];

        function fmtD(d){if(!d)return'';var p=d.split('-');return p[2]+'/'+p[1]+'/'+p[0];}
        function daysLeft(endDate){var e=new Date(endDate+'T00:00:00'),t=new Date();t.setHours(0,0,0,0);var diff=Math.ceil((e-t)/(1000*60*60*24));if(diff<0)return '<span style="color:#888;font-size:10px;">retornou</span>';if(diff===0)return '<span style="color:#66cc00;font-size:10px;font-weight:700;">retorna hoje</span>';return '<span style="color:#ffcc00;font-size:10px;">retorna em '+diff+'d</span>';}
        function timeAgo(iso){if(!iso)return '';var h=Math.floor((Date.now()-new Date(iso))/(1000*60*60));if(h<1)return 'h\u00e1 menos de 1h';if(h<24)return 'h\u00e1 '+h+'h';var dd=Math.floor(h/24);return 'h\u00e1 '+dd+' dia'+(dd>1?'s':'');}

        var teamTitle = data.meuTime || 'Todos os Times';
        var html = '';

        // Título + seletor
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">';
        html += '<div><div style="color:#3a5040;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:4px;">Painel do L\u00edder</div>';
        html += '<h2 style="color:#d0dcd2;font-size:20px;font-weight:700;margin:0;">&#128101; '+teamTitle+'</h2></div>';
        if(data.canSelectTeam){
            html += '<select onchange="loadLideresView(this.value)" style="padding:9px 12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;border-radius:8px;font-family:inherit;font-size:12px;">';
            html += '<option value="">Todos os Times</option>';
            data.teams.forEach(function(t){html += '<option value="'+t+'"'+(data.meuTime===t?' selected':'')+'>'+t+'</option>';});
            html += '</select>';
        }
        html += '</div>';

        // Cards stats
        var statsItems = [
            {label:'Colaboradores',value:data.colaboradores.length,color:'#66cc00',icon:'&#128101;',sub:'no time'},
            {label:'Ausentes Agora',value:data.ausentes.length,color:'#7aaaff',icon:'&#127958;&#65039;',sub:'f\u00e9rias e folgas'},
            {label:'Pendentes',value:data.pendentes.length,color:'#ffcc00',icon:'&#9203;',sub:'aguardando aprova\u00e7\u00e3o'}
        ];
        html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px;margin-bottom:28px;">';
        statsItems.forEach(function(c){
            html += '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-top:3px solid '+c.color+';border-radius:12px;padding:16px;">';
            html += '<div style="font-size:22px;margin-bottom:6px;">'+c.icon+'</div>';
            html += '<div style="font-size:28px;font-weight:700;color:'+c.color+';">'+c.value+'</div>';
            html += '<div style="color:#d0dcd2;font-size:12px;font-weight:600;margin-top:3px;">'+c.label+'</div>';
            html += '<div style="color:#3a5040;font-size:10px;margin-top:1px;">'+c.sub+'</div></div>';
        });
        html += '</div>';

        // Layout dois colunas
        html += '<div style="display:flex;gap:18px;align-items:flex-start;">';

        // ESQUERDA: calendário + pendentes + todas solicitações
        var leftHtml = '<div style="flex:1;min-width:0;">';

        leftHtml += '<div class="sec-label" style="margin-bottom:12px;">Calend\u00e1rio de Aus\u00eancias</div>';
        leftHtml += buildCalendar(data.aprovadas, window._lideresCalYear, window._lideresCalMonth, 'lideresCalPrev', 'lideresCalNext');

        // Pendentes
        if(data.pendentes.length > 0){
            leftHtml += '<div class="sec-label" style="margin:20px 0 10px;color:#ffcc00;">&#9203; Aguardando Aprova\u00e7\u00e3o ('+data.pendentes.length+')</div>';
            data.pendentes.forEach(function(f){
                var age = (Date.now()-new Date(f.requestedAt||0))/(1000*60*60*24);
                var bc = age>2?'#ff4444':(age>1?'#ffcc00':'#66cc00');
                var tl = f.tipo==='Ferias'?'F\u00e9rias':'Folga';
                var apiBase = f.tipo==='Ferias'?'/api/ferias':'/api/folgas';
                leftHtml += '<div style="border-left:3px solid '+bc+';background:rgba(255,255,255,0.02);border-radius:0 10px 10px 0;padding:12px;margin-bottom:8px;">';
                leftHtml += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">';
                leftHtml += '<div><strong style="color:#d0dcd2;font-size:12px;">'+f.user+'</strong><span style="color:#555;font-size:10px;margin-left:8px;">'+f.cargo+'</span></div>';
                leftHtml += '<span style="background:rgba(255,255,255,0.05);color:#aaa;border:1px solid rgba(255,255,255,0.1);padding:2px 8px;border-radius:6px;font-size:9px;font-weight:700;">'+tl+'</span></div>';
                leftHtml += '<div style="color:#aaa;font-size:11px;margin-bottom:2px;">'+fmtD(f.startDate)+' \u2192 '+fmtD(f.endDate)+'</div>';
                if(f.motivo)leftHtml += '<div style="color:#888;font-size:10px;margin-bottom:2px;">Motivo: '+f.motivo+'</div>';
                if(f.mensagem)leftHtml += '<div style="color:#555;font-size:10px;font-style:italic;margin-bottom:4px;">"'+f.mensagem+'"</div>';
                leftHtml += '<div style="color:'+bc+';font-size:9px;margin-bottom:8px;">'+timeAgo(f.requestedAt)+'</div>';
                leftHtml += '<div style="display:flex;gap:8px;">';
                leftHtml += '<button onclick="window._liderAprovar(\''+apiBase+'\','+f.id+')" style="flex:1;background:rgba(102,204,0,0.12);border:1px solid #66cc00;color:#66cc00;padding:7px;border-radius:7px;cursor:pointer;font-size:11px;font-weight:bold;font-family:inherit;">\u2713 Aprovar</button>';
                leftHtml += '<button onclick="window._liderRejeitar(\''+apiBase+'\','+f.id+')" style="flex:1;background:rgba(255,68,68,0.1);border:1px solid #ff4444;color:#ff4444;padding:7px;border-radius:7px;cursor:pointer;font-size:11px;font-weight:bold;font-family:inherit;">\u2717 Rejeitar</button>';
                leftHtml += '</div></div>';
            });
        }

        // Compras pendentes aguardando aprovacao do lider
        if(_comprasPend.length > 0){
            leftHtml += '<div class="sec-label" style="margin:20px 0 10px;color:#ffaa00;">&#128722; Compras Aguardando sua Aprovação ('+_comprasPend.length+')</div>';
            _comprasPend.forEach(function(c){
                var urgColor=c.urgencia==='Alta'?'#ff4444':c.urgencia==='Media'?'#ffcc00':'#66cc00';
                var urgDot=c.urgencia==='Alta'?'&#128308;':c.urgencia==='Media'?'&#128993;':'&#128994;';
                leftHtml += '<div style="border-left:3px solid '+urgColor+';background:rgba(255,255,255,0.02);border-radius:0 10px 10px 0;padding:12px;margin-bottom:8px;">';
                leftHtml += '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">';
                leftHtml += '<div><strong style="color:#d0dcd2;font-size:12px;">'+c.user+'</strong><span style="color:#555;font-size:10px;margin-left:8px;">'+(c.cargo||c.team||'')+'</span></div>';
                leftHtml += '<span style="color:'+urgColor+';font-size:9px;font-weight:700;">'+urgDot+' '+c.urgencia+'</span>';
                leftHtml += '</div>';
                leftHtml += '<div style="color:#d0dcd2;font-size:12px;font-weight:500;margin-bottom:3px;">'+c.produto+'</div>';
                leftHtml += '<div style="color:#888;font-size:10px;margin-bottom:3px;">'+c.motivo+'</div>';
                if(c.link)leftHtml += '<a href="'+c.link+'" target="_blank" style="color:#66cc00;font-size:10px;text-decoration:none;">&#128279; Ver produto</a>';
                if(c.valor)leftHtml += '<div style="color:#66cc00;font-size:11px;font-weight:600;margin-top:3px;">R$ '+parseFloat(c.valor).toLocaleString('pt-BR',{minimumFractionDigits:2})+'</div>';
                leftHtml += '<div style="display:flex;gap:8px;margin-top:8px;">';
                leftHtml += '<button onclick="window._liderAprovarCompra('+c.id+')" style="flex:1;background:rgba(102,204,0,0.12);border:1px solid #66cc00;color:#66cc00;padding:7px;border-radius:7px;cursor:pointer;font-size:11px;font-weight:bold;font-family:inherit;">✓ Aprovar</button>';
                leftHtml += '<button onclick="window._liderRejeitarCompra('+c.id+')" style="flex:1;background:rgba(255,68,68,0.1);border:1px solid #ff4444;color:#ff4444;padding:7px;border-radius:7px;cursor:pointer;font-size:11px;font-weight:bold;font-family:inherit;">✗ Recusar</button>';
                leftHtml += '</div></div>';
            });
        }

        // Todas as Solicitações
        leftHtml += '<div class="sec-label" style="margin:20px 0 10px;">Todas as Solicita\u00e7\u00f5es ('+data.todasSolicitacoes.length+')</div>';
        if(data.todasSolicitacoes.length === 0){
            leftHtml += '<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:20px;text-align:center;color:#3a5040;font-size:13px;">Nenhuma solicita\u00e7\u00e3o encontrada.</div>';
        } else {
            leftHtml += '<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden;">';
            leftHtml += '<div style="display:grid;grid-template-columns:1fr 80px 90px 90px 110px;gap:0;padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.03);">';
            ['Colaborador','Tipo','Sa\u00edda','Retorno','Status'].forEach(function(h){leftHtml += '<div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">'+h+'</div>';});
            leftHtml += '</div>';
            data.todasSolicitacoes.forEach(function(f){
                var sc = f.status==='aprovado'?'#66cc00':f.status==='rejeitado'?'#ff4444':f.status==='cancelado'?'#555':'#ffcc00';
                var sl = f.status==='aprovado'?'\u2713 Aprovado':f.status==='rejeitado'?'\u2717 Recusado':f.status==='cancelado'?'\u2715 Cancelado':'\u23f3 Pendente';
                var tc = f.tipo==='Ferias'?'#7aaaff':'#ff9944';
                var tl = f.tipo==='Ferias'?'F\u00e9rias':'Folga';
                leftHtml += '<div style="display:grid;grid-template-columns:1fr 80px 90px 90px 110px;gap:0;padding:10px 14px;border-bottom:1px solid rgba(255,255,255,0.04);align-items:center;">';
                leftHtml += '<div><div style="color:#d0dcd2;font-size:12px;font-weight:500;">'+f.user+'</div><div style="color:#555;font-size:10px;">'+(f.cargo||'')+'</div></div>';
                leftHtml += '<div><span style="color:'+tc+';font-size:9px;background:rgba(255,255,255,0.05);padding:2px 6px;border-radius:4px;">'+tl+'</span></div>';
                leftHtml += '<div style="color:#aaa;font-size:11px;">'+fmtD(f.startDate)+'</div>';
                leftHtml += '<div style="color:#aaa;font-size:11px;">'+fmtD(f.endDate)+'</div>';
                leftHtml += '<div style="color:'+sc+';font-size:10px;font-weight:500;">'+sl+'</div>';
                leftHtml += '</div>';
            });
            leftHtml += '</div>';
        }
        leftHtml += '</div>';

        // SIDEBAR DIREITA
        var sideHtml = '<div style="width:265px;flex-shrink:0;display:flex;flex-direction:column;gap:12px;position:sticky;top:80px;">';

        // Colaboradores
        sideHtml += '<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px;">';
        sideHtml += '<div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:10px;">Colaboradores ('+data.colaboradores.length+')</div>';
        if(data.colaboradores.length === 0){
            sideHtml += '<div style="color:#555;font-size:12px;text-align:center;padding:8px 0;">Nenhum colaborador.</div>';
        } else {
            var prevTeam = '';
            data.colaboradores.forEach(function(c){
                if(c.team !== prevTeam){
                    if(prevTeam !== '') sideHtml += '<div style="height:1px;background:rgba(255,255,255,0.04);margin:6px 0;"></div>';
                    if(c.team) sideHtml += '<div style="color:#2e4436;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin:4px 0;">'+c.team+'</div>';
                    prevTeam = c.team;
                }
                var initials = c.username.split('.').map(function(p){return p.charAt(0).toUpperCase();}).join('');
                var avatarBg = c.photo ? 'background-image:url(\''+c.photo+'\');background-size:cover;background-position:center;' : 'background:rgba(102,204,0,0.15);';
                sideHtml += '<div style="display:flex;align-items:center;gap:8px;padding:4px 0;">';
                sideHtml += '<div style="width:28px;height:28px;border-radius:50%;'+avatarBg+'flex-shrink:0;display:flex;align-items:center;justify-content:center;color:#66cc00;font-size:9px;font-weight:700;border:1px solid rgba(102,204,0,0.2);">'+(c.photo?'':initials)+'</div>';
                sideHtml += '<div style="min-width:0;"><div style="color:#d0dcd2;font-size:11px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'+c.username+'</div><div style="color:#555;font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'+(c.cargo||'\u2014')+'</div></div>';
                sideHtml += '</div>';
            });
        }
        sideHtml += '</div>';

        // Ausentes agora
        sideHtml += '<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px;">';
        sideHtml += '<div style="color:#3a5040;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:10px;">Ausentes Agora ('+data.ausentes.length+')</div>';
        if(data.ausentes.length === 0){
            sideHtml += '<div style="color:#3a5040;font-size:12px;text-align:center;padding:8px 0;">Nenhum ausente</div>';
        } else {
            data.ausentes.forEach(function(f){
                var tc = f.tipo==='Ferias'?'#7aaaff':'#ff9944';
                var tl = f.tipo==='Ferias'?'F\u00e9rias':'Folga';
                sideHtml += '<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">';
                sideHtml += '<div><div style="color:#d0dcd2;font-size:11px;font-weight:500;">'+f.user+'</div>'+(f.cargo?'<div style="color:#555;font-size:9px;">'+f.cargo+'</div>':'')+' </div>';
                sideHtml += '<div style="text-align:right;"><span style="color:'+tc+';font-size:8px;font-weight:700;">'+tl+'</span><div style="color:#555;font-size:9px;margin-top:1px;">ret. '+fmtD(f.endDate)+'</div><div style="margin-top:1px;">'+daysLeft(f.endDate)+'</div></div>';
                sideHtml += '</div>';
            });
        }
        sideHtml += '</div>';
        sideHtml += '</div>';

        html += leftHtml + sideHtml + '</div>';
        container.innerHTML = html;

        // Event handlers
        window.lideresCalPrev = function(){window._lideresCalMonth--;if(window._lideresCalMonth<0){window._lideresCalMonth=11;window._lideresCalYear--;}loadLideresView();};
        window.lideresCalNext = function(){window._lideresCalMonth++;if(window._lideresCalMonth>11){window._lideresCalMonth=0;window._lideresCalYear++;}loadLideresView();};

        window._liderAprovar = async function(base,id){
            try{var r=await fetch(base+'/aprovar/'+id,{method:'POST'});if(r.ok){showToast('Aprovado!');loadLideresView();}else{var d=await r.json();showToast(d.error||'Erro','error');}}catch(e){showToast('Erro','error');}
        };
        window._liderRejeitar = function(base,id){
            window._pendingRejectApiBase=base;window._pendingRejectRhId=id;
            document.getElementById('reject-reason').value='';
            document.getElementById('reject-modal').classList.add('active');
            window._pendingRejectRhMode=true;
            var _origConfirmL=window.confirmRejeitar;
            window.confirmRejeitar=async function(){
                if(!window._pendingRejectRhMode){_origConfirmL&&_origConfirmL();return;}
                var reason=document.getElementById('reject-reason').value.trim();
                if(!reason){showToast('Informe o motivo','error');return;}
                try{var r=await fetch(window._pendingRejectApiBase+'/rejeitar/'+window._pendingRejectRhId,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rejectionReason:reason})});
                if(r.ok){document.getElementById('reject-modal').classList.remove('active');showToast('Recusado.');window._pendingRejectRhMode=false;loadLideresView();}
                else{var d=await r.json();showToast(d.error||'Erro','error');}
                }catch(e){showToast('Erro','error');}
            };
        };

    } catch(e) {
        var c2=document.getElementById('lideres-main');
        if(c2) c2.innerHTML='<div style="color:#ff4444;padding:20px;">Erro: '+e.message+'</div>';
    }
};


window.loadComprasView = async function() {
    var container = document.getElementById('compras-main');
    if(!container) return;
    container.innerHTML = '<div style="color:#3a5040;font-size:13px;padding:20px;">Carregando...</div>';
    try {
        var all = await (await fetch('/api/compras')).json();
        if(all.error){ container.innerHTML='<div style="color:#ff4444;padding:20px;">'+all.error+'</div>'; return; }

        function fmtDT(iso){if(!iso)return'';var d=new Date(iso);return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric',timeZone:'America/Sao_Paulo'});}
        function fmtBRL(v){if(!v&&v!==0)return'\u2014';return'R$ '+parseFloat(v).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});}
        function urgBadge(u){var c=u==='Alta'?'#ff4444':u==='Media'?'#ffcc00':'#66cc00';var bg=u==='Alta'?'rgba(255,68,68,0.12)':u==='Media'?'rgba(255,204,0,0.1)':'rgba(102,204,0,0.1)';var dot=u==='Alta'?'&#128308;':u==='Media'?'&#128993;':'&#128994;';return '<span style="color:'+c+';background:'+bg+';border:1px solid '+c+'44;padding:2px 8px;border-radius:10px;font-size:9px;font-weight:700;">'+dot+' '+u+'</span>';}
        function statusBadge(s){var c=s==='aprovado'?'#66cc00':s==='comprado'?'#7aaaff':s==='rejeitado'?'#ff4444':s==='aguardando_rh'?'#cc88ff':'#ffcc00';var bg=s==='aprovado'?'rgba(102,204,0,0.1)':s==='comprado'?'rgba(119,170,255,0.1)':s==='rejeitado'?'rgba(255,68,68,0.1)':s==='aguardando_rh'?'rgba(200,136,255,0.1)':'rgba(255,204,0,0.08)';var label=s==='aprovado'?'\u2713 Aprovado':s==='comprado'?'\u2713 Comprado':s==='rejeitado'?'\u2717 Recusado':s==='aguardando_rh'?'\u23f3 Aguardando RH':'\u23f3 Aguardando L\u00edder';return '<span style="color:'+c+';background:'+bg+';border:1px solid '+c+'44;padding:3px 9px;border-radius:10px;font-size:10px;font-weight:700;">'+label+'</span>';}

        var minhas = all.filter(function(c){return c.user===myUser;});
        var pendentes = minhas.filter(function(c){return c.status==='pendente';}).length;
        var aprovadas = minhas.filter(function(c){return c.status==='aprovado';}).length;
        var rejeitadas = minhas.filter(function(c){return c.status==='rejeitado';}).length;
        var compradas = minhas.filter(function(c){return c.status==='comprado';}).length;

        var html = '';
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">';
        html += '<div><div style="color:#3a5040;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:4px;">Compras</div>';
        html += '<h2 style="color:#d0dcd2;font-size:20px;font-weight:700;margin:0;">&#128722; Minhas Solicita\u00e7\u00f5es</h2></div>';
        html += '<button onclick="document.getElementById(\'compras-modal\').classList.add(\'active\')" style="background:linear-gradient(135deg,#66cc00,#4d9900);color:#000;border:none;padding:11px 20px;border-radius:9px;font-weight:700;cursor:pointer;font-size:13px;font-family:inherit;">+ Nova Solicita\u00e7\u00e3o</button>';
        html += '</div>';

        html += '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:28px;">';
        [{label:'Pendentes',value:pendentes,color:'#ffcc00',icon:'&#9203;'},{label:'Aprovadas',value:aprovadas,color:'#66cc00',icon:'&#9989;'},{label:'Recusadas',value:rejeitadas,color:'#ff4444',icon:'&#10060;'},{label:'Compradas',value:compradas,color:'#7aaaff',icon:'&#128717;'}].forEach(function(c){
            html += '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-top:3px solid '+c.color+';border-radius:12px;padding:14px 16px;">';
            html += '<div style="font-size:20px;margin-bottom:5px;">'+c.icon+'</div>';
            html += '<div style="font-size:26px;font-weight:700;color:'+c.color+';">'+c.value+'</div>';
            html += '<div style="color:#888;font-size:11px;margin-top:2px;">'+c.label+'</div></div>';
        });
        html += '</div>';

        if(minhas.length === 0){
            html += '<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:40px;text-align:center;">';
            html += '<div style="font-size:40px;margin-bottom:12px;">&#128722;</div>';
            html += '<div style="color:#555;font-size:14px;">Voc\u00ea ainda n\u00e3o tem solicita\u00e7\u00f5es de compra.</div>';
            html += '<button onclick="document.getElementById(\'compras-modal\').classList.add(\'active\')" style="margin-top:16px;background:rgba(102,204,0,0.08);border:1px solid rgba(102,204,0,0.3);color:#66cc00;padding:10px 20px;border-radius:8px;font-weight:600;cursor:pointer;font-family:inherit;">+ Criar primeira solicita\u00e7\u00e3o</button>';
            html += '</div>';
        } else {
            var sorted = minhas.slice().sort(function(a,b){return new Date(b.requestedAt||0)-new Date(a.requestedAt||0);});
            sorted.forEach(function(c){
                var bc = c.status==='aprovado'?'#66cc00':c.status==='comprado'?'#7aaaff':c.status==='rejeitado'?'#ff4444':'rgba(255,255,255,0.08)';
                html += '<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-left:3px solid '+bc+';border-radius:0 12px 12px 0;padding:16px 18px;margin-bottom:10px;">';
                html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">';
                html += '<div style="flex:1;min-width:0;">';
                html += '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">';
                html += '<span style="color:#d0dcd2;font-size:14px;font-weight:600;">'+c.produto+'</span>';
                html += urgBadge(c.urgencia);
                html += statusBadge(c.status);
                html += '</div>';
                html += '<div style="color:#555;font-size:11px;margin-top:4px;">Solicitado em '+fmtDT(c.requestedAt)+'</div>';
                html += '</div>';
                html += '<div style="text-align:right;flex-shrink:0;margin-left:12px;">';
                html += '<div style="color:#66cc00;font-size:15px;font-weight:700;">'+fmtBRL(c.valorFinal||c.valor)+'</div>';
                if(c.valorFinal&&c.valorFinal!==c.valor)html += '<div style="color:#555;font-size:10px;text-decoration:line-through;">'+fmtBRL(c.valor)+'</div>';
                html += '</div></div>';
                html += '<div style="color:#aaa;font-size:12px;margin-bottom:6px;line-height:1.5;">&#128203; '+c.motivo+'</div>';
                if(c.link)html += '<a href="'+c.link+'" target="_blank" style="color:#66cc00;font-size:11px;text-decoration:none;">&#128279; Ver produto</a>';
                if(c.status==='rejeitado'&&c.rejectionReason)html += '<div style="color:#ff6060;font-size:11px;margin-top:6px;background:rgba(255,68,68,0.06);border:1px solid rgba(255,68,68,0.2);border-radius:6px;padding:6px 10px;">Motivo da recusa: '+c.rejectionReason+'</div>';
                if(c.status==='pendente')html += '<div style="margin-top:10px;"><button onclick="deletarCompra('+c.id+')" style="background:none;border:1px solid rgba(255,68,68,0.3);color:#ff4444;padding:5px 12px;border-radius:6px;cursor:pointer;font-size:11px;font-family:inherit;">Cancelar solicita\u00e7\u00e3o</button></div>';
                html += '</div>';
            });
        }
        container.innerHTML = html;

        window._pendingRejeitarCompraId = null;
        window.confirmRejeitarCompra = async function(){
            var reason = document.getElementById('compra-reject-reason').value.trim();
            if(!reason){showToast('Informe o motivo','error');return;}
            try{var r=await fetch('/api/compras/rejeitar/'+window._pendingRejeitarCompraId,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rejectionReason:reason})});
            if(r.ok){document.getElementById('compra-rejeitar-modal').classList.remove('active');showToast('Solicita\u00e7\u00e3o recusada.');loadComprasView();loadRH(window._rhTab);}
            else{var d=await r.json();showToast(d.error||'Erro','error');}
            }catch(e){showToast('Erro','error');}
        };

    } catch(e) {
        var c2=document.getElementById('compras-main');
        if(c2) c2.innerHTML='<div style="color:#ff4444;padding:20px;">Erro: '+e.message+'</div>';
    }
};

window.submitCompra = async function(){
    var produto = document.getElementById('compra-produto').value.trim();
    var link = document.getElementById('compra-link').value.trim();
    var motivo = document.getElementById('compra-motivo').value.trim();
    var urgencia = document.getElementById('compra-urgencia').value;
    var valor = parseFloat(document.getElementById('compra-valor').value)||0;
    if(!produto||!motivo){showToast('Produto e motivo s\u00e3o obrigat\u00f3rios','error');return;}
    try{
        var r=await fetch('/api/compras/solicitar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({produto,link,motivo,urgencia,valor})});
        if(r.ok){document.getElementById('compras-modal').classList.remove('active');document.getElementById('compra-produto').value='';document.getElementById('compra-link').value='';document.getElementById('compra-motivo').value='';document.getElementById('compra-valor').value='';showToast('Solicita\u00e7\u00e3o enviada ao RH!');loadComprasView();}
        else{var d=await r.json();showToast(d.error||'Erro','error');}
    }catch(e){showToast('Erro ao solicitar','error');}
};

window.deletarCompra = async function(id){
    if(!confirm('Cancelar esta solicita\u00e7\u00e3o?'))return;
    try{var r=await fetch('/api/compras/delete/'+id,{method:'POST'});if(r.ok){showToast('Cancelado.');loadComprasView();}else throw new Error();}catch(e){showToast('Erro','error');}
};

window.loadLogs = async function() {
    var container = document.getElementById('logs-main');
    if(!container) return;
    var from = document.getElementById('logs-filter-from') ? document.getElementById('logs-filter-from').value : '';
    var to   = document.getElementById('logs-filter-to')   ? document.getElementById('logs-filter-to').value   : '';
    var usr  = document.getElementById('logs-filter-user') ? document.getElementById('logs-filter-user').value  : '';
    var url  = '/api/logs?';
    if(from) url += 'from='+from+'&';
    if(to)   url += 'to='+to+'&';
    if(usr)  url += 'user='+encodeURIComponent(usr);
    try {
        var logsRes  = await fetch(url);
        var logs     = await logsRes.json();
        var usersRes = await fetch('/api/logs/users');
        var users    = await usersRes.json();
        if(logs.error){ container.innerHTML='<div style="color:#ff4444;padding:20px;">'+logs.error+'</div>'; return; }
        var usersOpts = '<option value="">Todos os usuarios</option>' + users.map(function(u){return '<option value="'+u+'"'+(u===usr?' selected':'')+'>'+u+'</option>';}).join('');
        var html = '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;align-items:flex-end;">'
            + '<div><div class="sec-label" style="margin-bottom:5px;">Usuario</div><select id="logs-filter-user" onchange="loadLogs()" style="padding:9px 12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;border-radius:8px;min-width:160px;font-family:inherit;">'+usersOpts+'</select></div>'
            + '<div><div class="sec-label" style="margin-bottom:5px;">De</div><input type="date" id="logs-filter-from" value="'+from+'" onchange="loadLogs()" style="padding:9px 12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;border-radius:8px;"></div>'
            + '<div><div class="sec-label" style="margin-bottom:5px;">Ate</div><input type="date" id="logs-filter-to" value="'+to+'" onchange="loadLogs()" style="padding:9px 12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);color:#d0dcd2;border-radius:8px;"></div>'
            + '<button onclick="document.getElementById(\'logs-filter-from\').value=\'\';document.getElementById(\'logs-filter-to\').value=\'\';document.getElementById(\'logs-filter-user\').value=\'\';loadLogs();" style="background:transparent;color:#888;border:1px solid rgba(255,255,255,0.1);padding:9px 14px;border-radius:8px;cursor:pointer;font-size:12px;font-family:inherit;">Limpar filtros</button>'
            + '</div>';
        html += '<div class="sec-label" style="margin-bottom:12px;">'+logs.length+' registro(s)</div>';
        if(logs.length === 0){
            html += '<div style="text-align:center;color:#555;padding:40px;font-size:13px;">Nenhum log encontrado.</div>';
        } else {
            var actionColors = {'Painel acessado':'#66cc00','Ferias solicitada':'#7aaaff','Ferias aprovada':'#66cc00','Ferias rejeitada':'#ff4444','Ferias cancelada':'#888','Folga solicitada':'#7aaaff','Folga aprovada':'#66cc00','Folga rejeitada':'#ff4444','Folga cancelada':'#888','Aviso publicado':'#ffcc00','Arquivo enviado':'#ff9944','Usuario criado':'#cc66ff'};
            html += logs.map(function(l){
                var color = actionColors[l.action] || '#aaa';
                var dt = '';
                try { dt = new Date(l.ts).toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'}); } catch(e){ dt = l.ts; }
                return '<div style="display:flex;gap:12px;align-items:flex-start;padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                    + '<div style="color:'+color+';font-size:14px;flex-shrink:0;width:20px;text-align:center;margin-top:2px;">&#9679;</div>'
                    + '<div style="flex:1;min-width:0;"><div style="display:flex;justify-content:space-between;gap:8px;align-items:flex-start;">'
                    + '<div>'
                    + '<span style="color:'+color+';font-size:12px;font-weight:600;">'+l.action+'</span>'
                    + (l.detail ? '<span style="color:#777;font-size:11px;margin-left:8px;">'+l.detail+'</span>' : '')
                    + '<div style="color:#3a5040;font-size:11px;margin-top:2px;">&#128100; '+l.user+'</div>'
                    + '</div>'
                    + '<div style="color:#3a5040;font-size:10px;white-space:nowrap;flex-shrink:0;margin-top:1px;">'+dt+'</div>'
                    + '</div></div></div>';
            }).join('');
        }
        container.innerHTML = html;
    } catch(e) {
        container.innerHTML = '<div style="color:#ff4444;padding:20px;">Erro ao carregar logs: '+e.message+'</div>';
    }
};
init();
