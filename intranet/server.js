const express=require('express');const fs=require('fs');const path=require('path');const{execSync}=require('child_process');const yaml=require('yaml');const multer=require('multer');const nodemailer=require('nodemailer');
const app=express();app.use(express.json({limit:'50mb'}));app.use(express.urlencoded({limit:'50mb',extended:true}));app.use(express.text({limit:'50mb',type:'text/plain'}));
const upload=multer({dest:'/tmp/'});
const USERS_FILE='/authelia/users_database.yml';const SITES_DIR='/sites';const FILES_DIR='/sites/arquivos-gerais';const PROFILES_FILE='/app/profiles.json';const NOTICES_FILE='/app/notices.json';const BENEFICIOS_FILE='/app/beneficios.json';
fs.mkdirSync(SITES_DIR,{recursive:true});fs.mkdirSync(FILES_DIR,{recursive:true});
function readUsers(){try{return yaml.parse(fs.readFileSync(USERS_FILE,'utf8'))||{users:{}}}catch(e){return{users:{}}}}
function saveUsers(d){fs.writeFileSync(USERS_FILE,yaml.stringify(d))}
function readProfiles(){try{return JSON.parse(fs.readFileSync(PROFILES_FILE,'utf8'))}catch(e){return{}}}
function saveProfiles(d){fs.writeFileSync(PROFILES_FILE,JSON.stringify(d,null,2))}
function readNotices(){try{return JSON.parse(fs.readFileSync(NOTICES_FILE,'utf8'))}catch(e){return[]}}
function saveNotices(d){fs.writeFileSync(NOTICES_FILE,JSON.stringify(d,null,2))}
function readBeneficios(){try{return JSON.parse(fs.readFileSync(BENEFICIOS_FILE,'utf8'))}catch(e){return{}}}
function saveBeneficios(d){fs.writeFileSync(BENEFICIOS_FILE,JSON.stringify(d,null,2))}
function getUserRole(u,d){if(u==='saulorogerio')return'master';const g=d.users?.[u]?.groups||[];if(g.includes('anjo-caido'))return'anjo-caido';return g.includes('master')?'master':(g.includes('admin')?'admin':'ouvinte')}

app.get('/api/me',(req,res)=>{const u=req.headers['remote-user']||'desconhecido';const d=readUsers();res.json({user:u,role:getUserRole(u,d),profile:readProfiles()[u]||{}})});

app.post('/api/profile',(req,res)=>{try{const u=req.headers['remote-user']||'desconhecido';const{photo,birthday}=req.body;let p=readProfiles();if(!p[u])p[u]={};if(birthday!==undefined)p[u].birthday=birthday;if(photo!==undefined)p[u].photo=photo;saveProfiles(p);res.json({success:true,profile:p[u]})}catch(e){res.status(500).json({error:e.message})}});

app.get('/api/users',(req,res)=>{const d=readUsers();const p=readProfiles();res.json(Object.keys(d.users||{}).map(k=>({username:k,usernameDisplay:k,email:d.users[k].email,role:getUserRole(k,d),team:p[k]?.team,cargo:p[k]?.cargo||"",folders:(d.users[k].groups||[]).filter(g=>!['master','admin','ouvinte','anjo-caido','todos'].includes(g))})))});

app.post('/api/add-user',async(req,res)=>{
  const{username,email,password,role,team,folders,cargo}=req.body;
  const d=readUsers();
  const argon2=require('argon2');
  const chars='ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$';
  const finalPassword=password||Array.from({length:12},()=>chars[Math.floor(Math.random()*chars.length)]).join('');
  const h=await argon2.hash(finalPassword);
  if(!d.users)d.users={};
  d.users[username]={displayname:username,password:h,email,groups:[role,...(folders||[])]};
  saveUsers(d);
  let p=readProfiles();
  p[username]={team:team||'Atenção',cargo:cargo||''};
  saveProfiles(p);
  try{
    const transporter=nodemailer.createTransport({host:process.env.SMTP_HOST,port:parseInt(process.env.SMTP_PORT),secure:process.env.SMTP_PORT==='465',auth:{user:process.env.SMTP_USER,pass:process.env.SMTP_PASS}});
    transporter.sendMail({from:`"SDA Intra" <${process.env.SMTP_USER}>`,to:email,subject:'Bem-vindo(a) à SDA Intra',html:`<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto"><div style="background:#1a3a1a;padding:32px;text-align:center"><h1 style="color:#fff;margin:0">SEJA BEM-VINDO(A)</h1><div style="height:4px;background:#66cc00;margin-top:16px"></div></div><div style="padding:32px;background:#fff"><p>Olá, <strong>${username}</strong>, seja bem-vindo(a) ao <strong>TIME SDA!</strong></p><p>Você foi adicionado(a) na nossa <strong>INTRANET Corporativa</strong>.</p><div style="background:#f5f5f5;border-left:4px solid #66cc00;padding:16px;margin:24px 0"><p style="margin:0 0 8px;font-size:12px;color:#666">USUÁRIO:</p><p style="margin:0 0 16px;font-weight:bold">${username}</p><p style="margin:0 0 8px;font-size:12px;color:#666">SENHA PROVISÓRIA:</p><p style="margin:0;font-weight:bold">${finalPassword}</p></div><div style="text-align:center;margin:32px 0"><a href="https://intra.segredosdaaudiencia.com.br" style="background:#66cc00;color:#000;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:bold">Acessar Intranet</a></div></div><div style="background:#1a3a1a;padding:24px;text-align:center"><p style="color:#66cc00;margin:0 0 8px">Instagram | YouTube | LinkedIn</p><p style="color:#888;font-size:12px">Experiência muda frequência!</p></div></div>`}).catch(e=>console.error('Erro email:',e));
  }catch(e){console.error('Email error:',e)}
  
  
  res.json({success:true});
});

app.put('/api/users/:username',(req,res)=>{
  const t=req.params.username;
  if(t==='saulorogerio')return res.status(403).send('Negado');
  const{role,folders,team,cargo}=req.body;
  const d=readUsers();
  if(d.users&&d.users[t]){
    d.users[t].groups=[role,...(folders||[])];
    saveUsers(d);
  }
  let p=readProfiles();
  if(!p[t])p[t]={};
  if(team)p[t].team=team;if(cargo!==undefined)p[t].cargo=cargo;
  saveProfiles(p);
  res.json({success:true});
});

app.post('/api/users/delete/:username',(req,res)=>{const t=req.params.username;if(t==='saulorogerio')return res.status(403).send('Negado');const d=readUsers();if(d.users?.[t]){delete d.users[t];saveUsers(d);}let p=readProfiles();if(p[t]){delete p[t];saveProfiles(p);}res.json({success:true})});

app.post('/api/notices',(req,res)=>{try{const u=req.headers['remote-user'];const{text}=req.body;const n=readNotices();n.unshift({id:Date.now(),author:u,text,date:new Date().toLocaleDateString('pt-BR')});saveNotices(n);res.json({success:true})}catch(e){res.status(500).json({error:e.message})}});
app.post('/api/notices/delete/:id',(req,res)=>{try{let n=readNotices();n=n.filter(x=>String(x.id)!==String(req.params.id));saveNotices(n);res.json({success:true})}catch(e){res.status(500).json({error:e.message})}});
app.get('/api/notices',(req,res)=>res.json(readNotices()));

app.get('/api/files',(req,res)=>{try{res.json(fs.readdirSync(FILES_DIR).map(f=>({name:f})))}catch(e){res.json([])}});
app.post('/api/files',upload.single('file'),(req,res)=>{if(req.file){fs.renameSync(req.file.path,path.join(FILES_DIR,req.file.originalname));res.json({success:true})}else{res.status(400).send('No file')}});

app.get('/api/folders',(req,res)=>{
  const u=req.headers['remote-user']||'desconhecido';
  const d=readUsers();
  const role=getUserRole(u,d);
  const groups=(d.users?.[u]?.groups||[]).map(g=>g.toLowerCase());
  const allDirs=fs.readdirSync(SITES_DIR,{withFileTypes:true}).filter(d=>d.isDirectory()&&!['imagens','central_arquivos','arquivos-gerais'].includes(d.name.toLowerCase())).map(d=>d.name);
  const isMaster=(role==='master'||groups.includes('todos'));

  const result=[];
  allDirs.forEach(dir=>{
    const dirLower=dir.toLowerCase();
    const hasFullAccess=isMaster||groups.includes(dirLower);
    
    // Verificar subpastas autorizadas (ex: "trafego/geral")
    const authorizedSubs=groups.filter(g=>g.startsWith(dirLower+'/')).map(g=>g.split('/')[1]);
    
    if(!hasFullAccess && authorizedSubs.length===0) return;
    
    const cats=[];
    try{
      const subs=fs.readdirSync(path.join(SITES_DIR,dir),{withFileTypes:true}).filter(d=>d.isDirectory());
      subs.forEach(s=>{
        const subLower=s.name.toLowerCase();
        if(hasFullAccess||authorizedSubs.includes(subLower)){
          const subPath=path.join(SITES_DIR,dir,s.name);
          const hasIndex=fs.existsSync(path.join(subPath,'index.html'));
          // Se não tem index.html, pegar subpastas filhas
          const children=[];
          if(!hasIndex){
            try{
              fs.readdirSync(subPath,{withFileTypes:true}).filter(d=>d.isDirectory()).forEach(child=>{
                children.push({name:child.name,path:`/${dir}/${s.name}/${child.name}`,isProject:fs.existsSync(path.join(subPath,child.name,'index.html'))});
              });
            }catch(e){}
          }
          cats.push({name:s.name,path:`/${dir}/${s.name}`,isProject:hasIndex,children});
        }
      });
    }catch(e){}
    
    result.push({
      name:dir,
      categories:cats,
      hasMainIndex:hasFullAccess&&fs.existsSync(path.join(SITES_DIR,dir,'index.html'))
    });
  });
  res.json(result);
});


// Retorna {start, end} em ms do dia calendário em America/Sao_Paulo
// offset=0 → hoje, offset=1 → ontem, offset=6 → 6 dias atrás, etc.
function getDayBounds(offset){
  const nowInSP=new Date(new Date().toLocaleString('en-US',{timeZone:'America/Sao_Paulo'}));
  nowInSP.setHours(0,0,0,0);
  nowInSP.setDate(nowInSP.getDate()-offset);
  const pad=n=>String(n).padStart(2,'0');
  const y=nowInSP.getFullYear(),m=pad(nowInSP.getMonth()+1),d=pad(nowInSP.getDate());
  return{start:new Date(`${y}-${m}-${d}T00:00:00-03:00`).getTime(),end:new Date(`${y}-${m}-${d}T23:59:59.999-03:00`).getTime()};
}

const https=require("https");
const WEBHOOK_URL="https://n8n.srv1499138.hstgr.cloud/webhook/e98df072-70f8-41bf-9adf-f6750a9a3a49";
function sendWebhook(data){try{const b=JSON.stringify(data);const urlObj=new URL(WEBHOOK_URL);const opts={hostname:urlObj.hostname,path:urlObj.pathname+urlObj.search,method:"POST",headers:{"Content-Type":"application/json","Content-Length":Buffer.byteLength(b)}};const r=https.request(opts);r.on("error",()=>{});r.write(b);r.end();}catch(e){}}
const LOGS_FILE="/app/logs.json";
function readLogs(){try{return JSON.parse(require("fs").readFileSync(LOGS_FILE,"utf8"));}catch(e){return[];}}
function saveLogs(d){require("fs").writeFileSync(LOGS_FILE,JSON.stringify(d));}
function addLog(user,action,detail){try{const l=readLogs();l.unshift({ts:new Date().toISOString(),user,action,detail:detail||""});if(l.length>10000)l.splice(10000);saveLogs(l);}catch(e){}}
const TRACKING_FILE="/app/tracking.json";
function readTracking(){try{return JSON.parse(require("fs").readFileSync(TRACKING_FILE,"utf8"))}catch(e){return{visits:[],conversions:[]}}}
function saveTracking(d){require("fs").writeFileSync(TRACKING_FILE,JSON.stringify(d))}
function lpCors(req,res,next){res.header("Access-Control-Allow-Origin","https://lp.segredosdaaudiencia.com.br");res.header("Access-Control-Allow-Methods","GET,POST,OPTIONS");res.header("Access-Control-Allow-Headers","Content-Type");if(req.method==="OPTIONS")return res.sendStatus(200);next()}
app.options("/api/track/visit",lpCors,(req,res)=>res.sendStatus(200));
app.options("/api/track/conversion",lpCors,(req,res)=>res.sendStatus(200));
const BLOCKED_IPS=["189.39.211.67"];
app.post("/api/track/visit",lpCors,(req,res)=>{const ip=(req.headers["x-forwarded-for"]||"").split(",")[0].trim()||req.ip||"unknown";if(BLOCKED_IPS.includes(ip))return res.json({ok:true,ignored:true});const t=readTracking();t.visits.push({ts:Date.now(),ip,ref:req.body.ref||"",path:req.body.path||"//"});if(t.visits.length>100000)t.visits=t.visits.slice(-100000);saveTracking(t);res.json({ok:true})});
app.post("/api/track/conversion",lpCors,(req,res)=>{const ip=(req.headers["x-forwarded-for"]||"").split(",")[0].trim()||req.ip||"unknown";if(BLOCKED_IPS.includes(ip))return res.json({ok:true,ignored:true});const t=readTracking();t.conversions.push({ts:Date.now(),ip,form:req.body.form||"default",email:req.body.email||"",path:req.body.path||null});if(t.conversions.length>100000)t.conversions=t.conversions.slice(-100000);saveTracking(t);res.json({ok:true})});
app.get("/api/track/stats",(req,res)=>{const t=readTracking();const rate=(c,v)=>v>0?((c/v)*100).toFixed(1):"0.0";const td=getDayBounds(0),yd=getDayBounds(1);const wStart=getDayBounds(6).start,wEnd=getDayBounds(0).end;const todayV=t.visits.filter(v=>v.ts>=td.start&&v.ts<=td.end);const yesterdayV=t.visits.filter(v=>v.ts>=yd.start&&v.ts<=yd.end);const weekV=t.visits.filter(v=>v.ts>=wStart&&v.ts<=wEnd);const todayC=t.conversions.filter(v=>v.ts>=td.start&&v.ts<=td.end);const yesterdayC=t.conversions.filter(v=>v.ts>=yd.start&&v.ts<=yd.end);const weekC=t.conversions.filter(v=>v.ts>=wStart&&v.ts<=wEnd);const uniqueTotal=new Set(t.visits.map(v=>v.ip)).size;const todayU=new Set(todayV.map(v=>v.ip)).size;const yesterdayU=new Set(yesterdayV.map(v=>v.ip)).size;const weekU=new Set(weekV.map(v=>v.ip)).size;const nDays=Math.min(90,Math.max(1,parseInt(req.query.days||7)||7));const fPath=req.query.path||null;const ipLastPath={};t.visits.forEach(v=>{if(!ipLastPath[v.ip]||v.ts>ipLastPath[v.ip].ts)ipLastPath[v.ip]=v.path||"/";});const srcV=fPath?t.visits.filter(v=>(v.path||"/")===fPath):t.visits;const srcC=fPath?t.conversions.filter(c=>c.path?c.path===fPath:(ipLastPath[c.ip]||"/")===fPath):t.conversions;const days=[];for(let i=nDays-1;i>=0;i--){const b=getDayBounds(i);const dv=srcV.filter(v=>v.ts>=b.start&&v.ts<=b.end);const dc=srcC.filter(v=>v.ts>=b.start&&v.ts<=b.end);days.push({label:new Date(b.start).toLocaleDateString("pt-BR",{day:"2-digit",month:"2-digit",timeZone:"America/Sao_Paulo"}),visits:new Set(dv.map(v=>v.ip)).size,conversions:dc.length})}res.json({total_visits:t.visits.length,total_unique:uniqueTotal,total_conversions:t.conversions.length,today_unique:todayU,today_conversions:todayC.length,today_rate:rate(todayC.length,todayU),yesterday_unique:yesterdayU,yesterday_conversions:yesterdayC.length,yesterday_rate:rate(yesterdayC.length,yesterdayU),week_unique:weekU,week_conversions:weekC.length,week_rate:rate(weekC.length,weekU),total_rate:rate(t.conversions.length,uniqueTotal),conversion_rate:t.visits.length?((t.conversions.length/t.visits.length)*100).toFixed(1):"0.0",chart:days})});
app.get("/api/monitor/check",(req,res)=>{const start=Date.now();const r=https.get("https://lp.segredosdaaudiencia.com.br",{timeout:10000},(resp)=>{resp.resume();res.json({status:"up",statusCode:resp.statusCode,responseTime:Date.now()-start})});r.on("error",(e)=>res.json({status:"down",error:e.message,responseTime:Date.now()-start}));r.on("timeout",()=>{r.destroy();res.json({status:"down",error:"timeout",responseTime:10000})})});
const PAGESPEED_CACHE_FILE="/app/pagespeed_cache.json";
function readPsCache(){try{return JSON.parse(require("fs").readFileSync(PAGESPEED_CACHE_FILE,"utf8"))}catch(e){return null}}
function savePsCache(d){require("fs").writeFileSync(PAGESPEED_CACHE_FILE,JSON.stringify(d))}

app.get("/api/monitor/pagespeed",(req,res)=>{
  const strategy=req.query.strategy||"mobile";
  const TWELVE_H=12*60*60*1000;
  const cache=readPsCache();
  if(cache&&cache[strategy]&&(Date.now()-cache[strategy].cachedAt)<TWELVE_H){
    return res.json(cache[strategy]);
  }
  const url=encodeURIComponent("https://lp.segredosdaaudiencia.com.br");
  const psKey=process.env.PAGESPEED_KEY?"&key="+process.env.PAGESPEED_KEY:"";https.get("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url="+url+"&strategy="+strategy+psKey,(r)=>{
    let b="";r.on("data",d=>b+=d);r.on("end",()=>{
      try{
        const data=JSON.parse(b);
        if(data.error){
          if(cache&&cache[strategy])return res.json(Object.assign({},cache[strategy],{cached:true}));
          return res.status(502).json({error:"PageSpeed quota esgotada. Tente mais tarde."});
        }
        const cat=data.lighthouseResult&&data.lighthouseResult.categories;
        const aud=data.lighthouseResult&&data.lighthouseResult.audits;
        const fps2=data.lighthouseResult&&data.lighthouseResult.fullPageScreenshot&&data.lighthouseResult.fullPageScreenshot.screenshot;if(fps2&&fps2.data){const cc=readPsCache()||{};cc["screenshot_"+strategy]={data:fps2.data,width:fps2.width,height:fps2.height,cachedAt:Date.now()};savePsCache(cc);}
        const result={
          performance:Math.round((cat&&cat.performance&&cat.performance.score||0)*100),
          fcp:aud&&aud["first-contentful-paint"]&&aud["first-contentful-paint"].displayValue,
          lcp:aud&&aud["largest-contentful-paint"]&&aud["largest-contentful-paint"].displayValue,
          cls:aud&&aud["cumulative-layout-shift"]&&aud["cumulative-layout-shift"].displayValue,
          tbt:aud&&aud["total-blocking-time"]&&aud["total-blocking-time"].displayValue,
          si:aud&&aud["speed-index"]&&aud["speed-index"].displayValue,
          opportunities:(function(){var ids=["unused-javascript","render-blocking-resources","unused-css-rules","uses-optimized-images","uses-webp-images","uses-responsive-images","uses-text-compression","long-tasks","bootup-time","third-party-summary","lcp-lazy-loaded","cache-insight"];return ids.filter(function(id){return aud&&aud[id]&&aud[id].score!==null&&aud[id].score<0.9;}).map(function(id){var a=aud[id];return{id:id,title:a.title,score:a.score,displayValue:a.displayValue||null};}).sort(function(a,b){return a.score-b.score;});}()),
          cachedAt:Date.now()
        };
        const c=cache||{};c[strategy]=result;savePsCache(c);
        res.json(result);
      }catch(e){
        if(cache&&cache[strategy])return res.json(Object.assign({},cache[strategy],{cached:true}));
        res.status(500).json({error:e.message});
      }
    });
  }).on("error",(e)=>{
    if(cache&&cache[strategy])return res.json(Object.assign({},cache[strategy],{cached:true}));
    res.status(500).json({error:e.message});
  });
});


app.get("/api/track/conversions",(req,res)=>{const t=readTracking();const convs=t.conversions.map((c,i)=>({idx:i,ts:c.ts,email:c.email||'',ip:c.ip||'',form:c.form||'',path:c.path||null,date:new Date(c.ts).toLocaleString("pt-BR",{timeZone:"America/Sao_Paulo"})}));res.json(convs.reverse())});
app.post("/api/track/conversion/delete",(req,res)=>{try{const{ts}=req.body;const t=readTracking();t.conversions=t.conversions.filter(c=>c.ts!==ts);saveTracking(t);res.json({ok:true})}catch(e){res.status(500).json({error:e.message})}});
app.post("/api/track/visit/delete",(req,res)=>{try{const{ts,ip}=req.body;const t=readTracking();t.visits=t.visits.filter(v=>!(v.ts===ts&&v.ip===ip));saveTracking(t);res.json({ok:true})}catch(e){res.status(500).json({error:e.message})}});


app.get("/api/track/variants",(req,res)=>{
  const t=readTracking();
  const rate=(c,v)=>v>0?((c/v)*100).toFixed(1):"0.0";
  const td=getDayBounds(0),yd=getDayBounds(1);
  const wStart=getDayBounds(6).start,wEnd=getDayBounds(0).end;
  const fromTs=req.query.from?parseInt(req.query.from):null;
  const toTs=req.query.to?parseInt(req.query.to):null;
  const hasCustom=!!(fromTs&&toTs);
  // IP -> path mais recente (para atribuir conversões sem path)
  const ipPath={};
  t.visits.forEach(v=>{if(!ipPath[v.ip]||v.ts>ipPath[v.ip].ts)ipPath[v.ip]={path:v.path||'/',ts:v.ts}});
  // Todos os paths únicos
  const paths=[...new Set(t.visits.map(v=>v.path||'/'))].sort();
  const result=paths.map(p=>{
    const pV=t.visits.filter(v=>(v.path||'/')===p);
    const pC=t.conversions.filter(c=>c.path?c.path===p:(ipPath[c.ip]?.path||'/')===p);
    const tV=pV.filter(v=>v.ts>=td.start&&v.ts<=td.end);
    const yV=pV.filter(v=>v.ts>=yd.start&&v.ts<=yd.end);
    const wV=pV.filter(v=>v.ts>=wStart&&v.ts<=wEnd);
    const tC=pC.filter(c=>c.ts>=td.start&&c.ts<=td.end);
    const yC=pC.filter(c=>c.ts>=yd.start&&c.ts<=yd.end);
    const wC=pC.filter(c=>c.ts>=wStart&&c.ts<=wEnd);
    const tU=new Set(tV.map(v=>v.ip)).size;
    const yU=new Set(yV.map(v=>v.ip)).size;
    const wU=new Set(wV.map(v=>v.ip)).size;
    const totU=new Set(pV.map(v=>v.ip)).size;
    const obj={path:p,
      today:{visits:tU,conversions:tC.length,rate:rate(tC.length,tU)},
      yesterday:{visits:yU,conversions:yC.length,rate:rate(yC.length,yU)},
      week:{visits:wU,conversions:wC.length,rate:rate(wC.length,wU)},
      total:{visits:totU,conversions:pC.length,rate:rate(pC.length,totU)}
    };
    if(hasCustom){
      const cV=pV.filter(v=>v.ts>=fromTs&&v.ts<=toTs);
      const cC=pC.filter(c=>c.ts>=fromTs&&c.ts<=toTs);
      const cU=new Set(cV.map(v=>v.ip)).size;
      obj.custom={visits:cU,conversions:cC.length,rate:rate(cC.length,cU)};
    }
    return obj;
  });
  res.json(result);
});

// ---- VARIANT CONFIG ----
const VARIANT_CONFIG_FILE='/app/variant_config.json';
function readVarCfg(){try{return JSON.parse(require('fs').readFileSync(VARIANT_CONFIG_FILE,'utf8'))}catch(e){return{}}}
function saveVarCfg(d){require('fs').writeFileSync(VARIANT_CONFIG_FILE,JSON.stringify(d,null,2))}
app.options('/api/track/variant/config',lpCors,(req,res)=>res.sendStatus(200));
app.get('/api/track/variant/config',lpCors,(req,res)=>res.json(readVarCfg()));
app.post('/api/track/variant/config',(req,res)=>{try{const{path:vpath,active}=req.body;if(typeof vpath!=='string'||typeof active!=='boolean')return res.status(400).json({error:'path e active obrigatorios'});const cfg=readVarCfg();cfg[vpath]={active};saveVarCfg(cfg);res.json({ok:true,config:cfg})}catch(e){res.status(500).json({error:e.message})}});

// ---- SISTEMA DE FERIAS ----
const FERIAS_FILE='/app/ferias.json';
function readFerias(){try{return JSON.parse(fs.readFileSync(FERIAS_FILE,'utf8'));}catch(e){return[];}}
function saveFerias(d){fs.writeFileSync(FERIAS_FILE,JSON.stringify(d,null,2));}
const CARGO_LIDER_MAP={'Analista Comercial':'Lider Comercial','Analista Recursos Humanos':'Lider Recursos Humanos','Analista Marketing':'Lider Marketing','Analista Financeiro':'Lider Financeiro','Analista Eventos':'Lider Eventos'};
function isRH(u,cargo){const p=readProfiles();return cargo==='Lider Recursos Humanos'||p[u]?.rhAccess===true;}
function podeAprovar(approver,ac,item){if(approver==='saulorogerio')return true;if(item.liderDireto&&item.liderDireto===approver)return true;if(isRH(approver,ac))return true;return false;}
app.get('/api/ferias',(req,res)=>{const u=req.headers['remote-user']||'desconhecido';const p=readProfiles();const cargo=p[u]?.cargo||'';const all=readFerias();if(u==='saulorogerio'||isRH(u,cargo))return res.json(all);res.json(all.filter(f=>f.user===u||f.liderDireto===u));});
app.post('/api/ferias/solicitar',(req,res)=>{try{const u=req.headers['remote-user']||'desconhecido';const{startDate,endDate,liderDireto,mensagem}=req.body;if(!startDate||!endDate)return res.status(400).json({error:'Datas obrigatorias'});const prof=readProfiles()[u]||{};const cargo=prof.cargo||'';const team=prof.team||'';const ferias=readFerias();ferias.push({id:Date.now(),user:u,cargo,team,startDate,endDate,liderDireto:liderDireto||'',mensagem:mensagem||'',status:'pendente',requestedAt:new Date().toISOString()});saveFerias(ferias);sendWebhook({tipo_registro:'Ferias',tipo_solicitacao:'Solicitacao',usuario:u,email_usuario:readUsers().users[u]?.email||'',data_saida:startDate,data_retorno:endDate,lider_direto:liderDireto||'',email_lider:readUsers().users[liderDireto]?.email||'',data_solicitacao:new Date().toISOString(),mensagem:mensagem||''});addLog(u,'Ferias solicitada',startDate+' -> '+endDate);res.json({success:true});}catch(e){res.status(500).json({error:e.message});}});
app.post('/api/ferias/aprovar/:id',(req,res)=>{try{const approver=req.headers['remote-user']||'desconhecido';const ac=readProfiles()[approver]?.cargo||'';const ferias=readFerias();const idx=ferias.findIndex(f=>String(f.id)===String(req.params.id));if(idx===-1)return res.status(404).json({error:'Nao encontrado'});const item=ferias[idx];if(!podeAprovar(approver,ac,item))return res.status(403).json({error:'Sem permissao'});ferias[idx].status='aprovado';ferias[idx].approvedBy=approver;ferias[idx].approvedAt=new Date().toISOString();saveFerias(ferias);{const _fai=ferias[idx];sendWebhook({tipo_registro:'Ferias',tipo_solicitacao:'Aprovacao',usuario:_fai.user,email_usuario:readUsers().users[_fai.user]?.email||'',aprovado_por:approver,email_aprovador:readUsers().users[approver]?.email||'',data_saida:_fai.startDate,data_retorno:_fai.endDate,lider_direto:_fai.liderDireto||'',email_lider:readUsers().users[_fai.liderDireto]?.email||'',data_solicitacao:_fai.requestedAt||'',mensagem:_fai.mensagem||''});addLog(approver,'Ferias aprovada','de '+_fai.user+' ('+_fai.startDate+' -> '+_fai.endDate+')');}res.json({success:true});}catch(e){res.status(500).json({error:e.message});}});
app.post('/api/ferias/rejeitar/:id',(req,res)=>{try{const approver=req.headers['remote-user']||'desconhecido';const ac=readProfiles()[approver]?.cargo||'';const ferias=readFerias();const idx=ferias.findIndex(f=>String(f.id)===String(req.params.id));if(idx===-1)return res.status(404).json({error:'Nao encontrado'});const item=ferias[idx];if(!podeAprovar(approver,ac,item))return res.status(403).json({error:'Sem permissao'});const{rejectionReason}=req.body;ferias[idx].status='rejeitado';ferias[idx].rejectedBy=approver;ferias[idx].rejectedAt=new Date().toISOString();if(rejectionReason)ferias[idx].rejectionReason=rejectionReason;saveFerias(ferias);{const _fri=ferias[idx];sendWebhook({tipo_registro:'Ferias',tipo_solicitacao:'Rejeicao',usuario:_fri.user,email_usuario:readUsers().users[_fri.user]?.email||'',rejeitado_por:approver,email_aprovador:readUsers().users[approver]?.email||'',motivo:rejectionReason||'',data_saida:_fri.startDate,data_retorno:_fri.endDate,lider_direto:_fri.liderDireto||'',email_lider:readUsers().users[_fri.liderDireto]?.email||'',data_solicitacao:_fri.requestedAt||'',mensagem:_fri.mensagem||''});addLog(approver,'Ferias rejeitada','de '+_fri.user+' motivo: '+(rejectionReason||''));}res.json({success:true});}catch(e){res.status(500).json({error:e.message});}});
app.post('/api/ferias/delete/:id',(req,res)=>{try{const user=req.headers['remote-user']||'desconhecido';const ferias=readFerias();const item=ferias.find(f=>String(f.id)===String(req.params.id));if(!item)return res.status(404).json({error:'Nao encontrado'});if(user!=='saulorogerio'&&item.user!==user)return res.status(403).json({error:'Sem permissao'});saveFerias(ferias.filter(f=>String(f.id)!==String(req.params.id)));res.json({success:true});}catch(e){res.status(500).json({error:e.message});}});


app.get('/api/lideres',(req,res)=>{
  const d=readUsers();const p=readProfiles();
  const liderCargos=['Lider Comercial','Lider Recursos Humanos','Lider Marketing','Lider Concierge','Lider Financeiro','Lider Eventos','Diretoria'];
  const lideres=Object.keys(d.users||{}).filter(k=>liderCargos.includes(p[k]?.cargo||'')).map(k=>({username:k,cargo:p[k]?.cargo||''}));
  res.json(lideres);
});


// ===== FOLGAS =====
const FOLGAS_FILE='/app/folgas.json';
function readFolgas(){try{return JSON.parse(require('fs').readFileSync(FOLGAS_FILE,'utf8'));}catch(e){return[];}}
function saveFolgas(d){require('fs').writeFileSync(FOLGAS_FILE,JSON.stringify(d,null,2));}

app.get('/api/folgas',(req,res)=>{
  const u=req.headers['remote-user']||'desconhecido';
  const p=readProfiles();const cargo=p[u]?.cargo||'';const all=readFolgas();
  if(u==='saulorogerio'||isRH(u,cargo))return res.json(all);
  res.json(all.filter(f=>f.user===u||f.liderDireto===u));
});

app.post('/api/folgas/solicitar',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'desconhecido';
    const{startDate,endDate,liderDireto,motivo,mensagem}=req.body;
    if(!startDate||!endDate)return res.status(400).json({error:'Datas obrigatorias'});
    const prof=readProfiles()[u]||{};
    const cargo=prof.cargo||'';const team=prof.team||'';
    const folgas=readFolgas();
    folgas.push({id:Date.now(),user:u,cargo,team,startDate,endDate,liderDireto:liderDireto||'',motivo:motivo||'',mensagem:mensagem||'',status:'pendente',requestedAt:new Date().toISOString()});
    saveFolgas(folgas);sendWebhook({tipo_registro:'Folga',tipo_solicitacao:'Solicitacao',usuario:u,email_usuario:readUsers().users[u]?.email||'',data_saida:startDate,data_retorno:endDate,lider_direto:liderDireto||'',email_lider:readUsers().users[liderDireto]?.email||'',data_solicitacao:new Date().toISOString(),motivo:motivo||'',mensagem:mensagem||''});addLog(u,'Folga solicitada',startDate+' -> '+endDate);res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/folgas/aprovar/:id',(req,res)=>{
  try{
    const approver=req.headers['remote-user']||'desconhecido';
    const ac=readProfiles()[approver]?.cargo||'';
    const folgas=readFolgas();
    const idx=folgas.findIndex(f=>String(f.id)===String(req.params.id));
    if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
    if(!podeAprovar(approver,ac,folgas[idx]))return res.status(403).json({error:'Sem permissao'});
    folgas[idx].status='aprovado';folgas[idx].approvedBy=approver;folgas[idx].approvedAt=new Date().toISOString();
    saveFolgas(folgas);{const _gai=folgas[idx];sendWebhook({tipo_registro:'Folga',tipo_solicitacao:'Aprovacao',usuario:_gai.user,email_usuario:readUsers().users[_gai.user]?.email||'',aprovado_por:approver,email_aprovador:readUsers().users[approver]?.email||'',data_saida:_gai.startDate,data_retorno:_gai.endDate,lider_direto:_gai.liderDireto||'',email_lider:readUsers().users[_gai.liderDireto]?.email||'',data_solicitacao:_gai.requestedAt||'',mensagem:_gai.mensagem||''});addLog(approver,'Folga aprovada','de '+_gai.user+' ('+_gai.startDate+' -> '+_gai.endDate+')');}res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/folgas/rejeitar/:id',(req,res)=>{
  try{
    const approver=req.headers['remote-user']||'desconhecido';
    const ac=readProfiles()[approver]?.cargo||'';
    const folgas=readFolgas();
    const idx=folgas.findIndex(f=>String(f.id)===String(req.params.id));
    if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
    if(!podeAprovar(approver,ac,folgas[idx]))return res.status(403).json({error:'Sem permissao'});
    const{rejectionReason}=req.body;
    folgas[idx].status='rejeitado';folgas[idx].rejectedBy=approver;folgas[idx].rejectedAt=new Date().toISOString();
    if(rejectionReason)folgas[idx].rejectionReason=rejectionReason;
    saveFolgas(folgas);{const _gri=folgas[idx];sendWebhook({tipo_registro:'Folga',tipo_solicitacao:'Rejeicao',usuario:_gri.user,email_usuario:readUsers().users[_gri.user]?.email||'',rejeitado_por:approver,email_aprovador:readUsers().users[approver]?.email||'',motivo:rejectionReason||'',data_saida:_gri.startDate,data_retorno:_gri.endDate,lider_direto:_gri.liderDireto||'',email_lider:readUsers().users[_gri.liderDireto]?.email||'',data_solicitacao:_gri.requestedAt||'',mensagem:_gri.mensagem||''});addLog(approver,'Folga rejeitada','de '+_gri.user+' motivo: '+(rejectionReason||''));}res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/folgas/delete/:id',(req,res)=>{
  try{
    const user=req.headers['remote-user']||'desconhecido';
    const folgas=readFolgas();
    const item=folgas.find(f=>String(f.id)===String(req.params.id));
    if(!item)return res.status(404).json({error:'Nao encontrado'});
    if(user!=='saulorogerio'&&item.user!==user)return res.status(403).json({error:'Sem permissao'});
    saveFolgas(folgas.filter(f=>String(f.id)!==String(req.params.id)));
    res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

// ===== CANCELAR FERIAS/FOLGAS =====
app.post('/api/ferias/cancelar/:id',(req,res)=>{
  try{
    const user=req.headers['remote-user']||'desconhecido';
    const ac=readProfiles()[user]?.cargo||'';
    const ferias=readFerias();
    const idx=ferias.findIndex(f=>String(f.id)===String(req.params.id));
    if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
    const item=ferias[idx];
    if(user!=='saulorogerio'&&item.user!==user&&!podeAprovar(user,ac,item))return res.status(403).json({error:'Sem permissao'});
    const{cancelReason}=req.body;
    ferias[idx].status='cancelado';ferias[idx].cancelledBy=user;ferias[idx].cancelledAt=new Date().toISOString();
    if(cancelReason)ferias[idx].cancelReason=cancelReason;
    saveFerias(ferias);{const _fci=ferias[idx];sendWebhook({tipo_registro:'Ferias',tipo_solicitacao:'Cancelamento',usuario:_fci.user,email_usuario:readUsers().users[_fci.user]?.email||'',cancelado_por:user,email_aprovador:readUsers().users[user]?.email||'',motivo:cancelReason||'',data_saida:_fci.startDate,data_retorno:_fci.endDate,lider_direto:_fci.liderDireto||'',email_lider:readUsers().users[_fci.liderDireto]?.email||'',data_solicitacao:_fci.requestedAt||'',mensagem:_fci.mensagem||''});addLog(user,'Ferias cancelada','de '+_fci.user+' motivo: '+(cancelReason||''));}res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/folgas/cancelar/:id',(req,res)=>{
  try{
    const user=req.headers['remote-user']||'desconhecido';
    const ac=readProfiles()[user]?.cargo||'';
    const folgas=readFolgas();
    const idx=folgas.findIndex(f=>String(f.id)===String(req.params.id));
    if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
    const item=folgas[idx];
    if(user!=='saulorogerio'&&item.user!==user&&!podeAprovar(user,ac,item))return res.status(403).json({error:'Sem permissao'});
    const{cancelReason}=req.body;
    folgas[idx].status='cancelado';folgas[idx].cancelledBy=user;folgas[idx].cancelledAt=new Date().toISOString();
    if(cancelReason)folgas[idx].cancelReason=cancelReason;
    saveFolgas(folgas);{const _gci=folgas[idx];sendWebhook({tipo_registro:'Folga',tipo_solicitacao:'Cancelamento',usuario:_gci.user,email_usuario:readUsers().users[_gci.user]?.email||'',cancelado_por:user,email_aprovador:readUsers().users[user]?.email||'',motivo:cancelReason||'',data_saida:_gci.startDate,data_retorno:_gci.endDate,lider_direto:_gci.liderDireto||'',email_lider:readUsers().users[_gci.liderDireto]?.email||'',data_solicitacao:_gci.requestedAt||'',mensagem:_gci.mensagem||''});addLog(user,'Folga cancelada','de '+_gci.user+' motivo: '+(cancelReason||''));}res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

// ===== ENDPOINTS PUBLICOS: APROVADAS (para calendarios) =====
app.get('/api/ferias/aprovadas',(req,res)=>{
  try{const ferias=readFerias();res.json(ferias.filter(f=>f.status==='aprovado'));}
  catch(e){res.status(500).json({error:e.message});}
});
app.get('/api/folgas/aprovadas',(req,res)=>{
  try{const folgas=readFolgas();res.json(folgas.filter(f=>f.status==='aprovado'));}
  catch(e){res.status(500).json({error:e.message});}
});

app.get('/api/logs',(req,res)=>{
  const u=req.headers['remote-user']||'';
  const d=readUsers();
  const role=getUserRole(u,d);
  if(!['master','anjo-caido'].includes(role))return res.status(403).json({error:'Sem permissao'});
  const{from,to,user:fu}=req.query;
  let logs=readLogs();
  if(fu)logs=logs.filter(l=>l.user===fu);
  if(from)logs=logs.filter(l=>l.ts>=new Date(from).toISOString());
  if(to){const toEnd=new Date(to);toEnd.setHours(23,59,59,999);logs=logs.filter(l=>l.ts<=toEnd.toISOString());}
  res.json(logs.slice(0,5000));
});
app.post('/api/logs',(req,res)=>{
  const u=req.headers['remote-user']||'desconhecido';
  const{action,detail}=req.body;
  if(action)addLog(u,action,detail||'');
  res.json({ok:true});
});
app.get('/api/logs/users',(req,res)=>{
  const u=req.headers['remote-user']||'';
  const d=readUsers();
  const role=getUserRole(u,d);
  if(!['master','anjo-caido'].includes(role))return res.status(403).json({error:'Sem permissao'});
  const logs=readLogs();
  const users=[...new Set(logs.map(l=>l.user))].sort();
  res.json(users);
});

// ===== RECURSOS HUMANOS DASHBOARD =====
app.get('/api/rh/dashboard',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'';
    const d=readUsers();
    const p=readProfiles();
    const role=getUserRole(u,d);
    const cargo=p[u]?.cargo||'';
    const canView=['master','anjo-caido','admin'].includes(role)||isRH(u,cargo);
    if(!canView)return res.status(403).json({error:'Sem permissao'});

    const today=new Date();today.setHours(0,0,0,0);
    const in7=new Date(today);in7.setDate(in7.getDate()+7);
    const in30=new Date(today);in30.setDate(in30.getDate()+30);

    const allUsers=Object.keys(d.users||{});
    const ferias=readFerias().filter(f=>f.status==='aprovado');
    const folgas=readFolgas().filter(f=>f.status==='aprovado');
    const feriasPend=readFerias().filter(f=>f.status==='pendente');
    const folgasPend=readFolgas().filter(f=>f.status==='pendente');

    // Aniversariantes do mes
    const mesAtual=today.getMonth()+1;
    const aniversariantes=Object.keys(d.users||{}).filter(k=>{const b=p[k]?.birthday;if(!b)return false;return parseInt(b.split('-')[1])===mesAtual;}).map(k=>({username:k,birthday:p[k].birthday,cargo:p[k]?.cargo||'',team:p[k]?.team||''}));

    // Retardatarios (retorno esperado ja passou)
    const past7=new Date(today);past7.setDate(past7.getDate()-7);
    const allApproved=[...ferias.map(f=>({...f,tipo:'Ferias'})),...folgas.map(f=>({...f,tipo:'Folga'}))];
    const retardatarios=allApproved.filter(f=>{const e=new Date(f.endDate+'T00:00:00');return e<today&&e>=past7&&!f.returnedAt;}).map(f=>{if(p[f.user]){f.cargo=p[f.user].cargo||'';f.team=p[f.user].team||'';}return f;});

    function isActive(f){
      const s=new Date(f.startDate+'T00:00:00'),e=new Date(f.endDate+'T23:59:59');
      return today>=s&&today<=e;
    }
    function isUpcoming(f){
      const s=new Date(f.startDate+'T00:00:00');
      return s>today&&s<=in30;
    }
    function returningIn7(f){
      const e=new Date(f.endDate+'T00:00:00');
      return e>=today&&e<=in7;
    }

    const feriasAtivas=ferias.filter(isActive);
    const folgasAtivas=folgas.filter(isActive);

    const ausentes=[
      ...feriasAtivas.map(f=>({...f,tipo:'Ferias'})),
      ...folgasAtivas.map(f=>({...f,tipo:'Folga'}))
    ].sort((a,b)=>new Date(a.endDate)-new Date(b.endDate));

    const retornando=[...ferias,...folgas].filter(returningIn7).map(f=>({
      ...f,tipo:ferias.includes(f)?'Ferias':'Folga'
    })).sort((a,b)=>new Date(a.endDate)-new Date(b.endDate));

    const proximas=[...ferias,...folgas].filter(isUpcoming).map(f=>({
      ...f,tipo:ferias.includes(f)?'Ferias':'Folga'
    })).sort((a,b)=>new Date(a.startDate)-new Date(b.startDate)).slice(0,15);

    // Enrich with profile info
    [...ausentes,...retornando,...proximas].forEach(f=>{
      if(p[f.user]){f.cargo=f.cargo||p[f.user].cargo||'';f.team=f.team||p[f.user].team||'';}
    });

    const pendingList=[...feriasPend.map(f=>({...f,tipo:'Ferias'})),...folgasPend.map(f=>({...f,tipo:'Folga'}))].sort((a,b)=>new Date(a.requestedAt)-new Date(b.requestedAt));
    pendingList.forEach(f=>{if(p[f.user]){f.cargo=f.cargo||p[f.user].cargo||'';f.team=f.team||p[f.user].team||'';}});
    // TeamStats precisa de feriasAtivas/folgasAtivas definidas acima
    const teamStatsObj={};[...feriasAtivas.map(f=>({...f,tipo:'Ferias'})),...folgasAtivas.map(f=>({...f,tipo:'Folga'}))].forEach(f=>{const t=p[f.user]?.team||'Sem time';if(!teamStatsObj[t])teamStatsObj[t]={total:0,ferias:0,folgas:0};teamStatsObj[t].total++;if(f.tipo==='Ferias')teamStatsObj[t].ferias++;else teamStatsObj[t].folgas++;});
    res.json({
      totalUsers:allUsers.length,
      feriasAtivas:feriasAtivas.length,
      folgasAtivas:folgasAtivas.length,
      retornandoEmBreve:retornando.length,
      pendentes:feriasPend.length+folgasPend.length,
      ausentes,
      retornando,
      proximas,
      pendingList,
      aniversariantes,
      retardatarios,
      teamStats:teamStatsObj
    });
  }catch(e){res.status(500).json({error:e.message});}
});

const HEATMAP_FILE="/app/heatmap.json";
function readHeatmap(){try{return JSON.parse(require("fs").readFileSync(HEATMAP_FILE,"utf8"))}catch(e){return{clicks:[]}}}
function saveHeatmap(d){require("fs").writeFileSync(HEATMAP_FILE,JSON.stringify(d))}
app.options("/api/track/heatmap",lpCors,(req,res)=>res.sendStatus(200));
app.post("/api/track/heatmap",lpCors,(req,res)=>{const ip=(req.headers["x-forwarded-for"]||"").split(",")[0].trim()||req.ip||"unknown";if(BLOCKED_IPS.includes(ip))return res.json({ok:true,ignored:true});let _rb=req.body;if(typeof _rb==="string"){try{_rb=JSON.parse(_rb);}catch(e){return res.status(400).json({ok:false});}}const events=Array.isArray(_rb)?_rb:[_rb];const h=readHeatmap();for(const ev of events){if(typeof ev.x!=="number"||typeof ev.y!=="number")continue;h.clicks.push({ts:Date.now(),x:ev.x,y:ev.y,path:ev.path||"/",vw:ev.vw||1920,dh:ev.dh||5000,type:ev.type||"click"});}if(h.clicks.length>500000)h.clicks=h.clicks.slice(-500000);saveHeatmap(h);res.json({ok:true})});
app.get("/api/track/heatmap",(req,res)=>{const h=readHeatmap();const fpath=req.query.path||null;let since,until;if(req.query.from&&req.query.to){since=parseInt(req.query.from);until=parseInt(req.query.to);}else{const days=parseInt(req.query.days||30);since=Date.now()-(days*86400000);until=Date.now();}let clicks=h.clicks.filter(c=>c.ts>=since&&c.ts<=until);if(fpath)clicks=clicks.filter(c=>c.path===fpath);res.json({total:clicks.length,clicks});});
app.post("/api/track/heatmap/insights",async(req,res)=>{
  const key=process.env.ANTHROPIC_KEY;
  if(!key)return res.status(503).json({error:"ANTHROPIC_KEY nao configurada no servidor."});
  const{totalClicks,topClicks,midClicks,botClicks,scroll25,scroll50,scroll75,scroll100,path}=req.body;
  const pct=(a,b)=>b?Math.round(a/b*100):0;
  const prompt="Voce e especialista em CRO.\n\nAnalise os dados do mapa de calor da pagina "+(path||"/")+" (LP de evento presencial SDA AO VIVO 2026):\n\nCLIQUES ("+totalClicks+" total):\n- Topo: "+topClicks+" ("+pct(topClicks,totalClicks)+"%)\n- Meio: "+midClicks+" ("+pct(midClicks,totalClicks)+"%)\n- Rodape: "+botClicks+" ("+pct(botClicks,totalClicks)+"%)\n\nSCROLL:\n- 25%: "+scroll25+" sessoes\n- 50%: "+scroll50+" sessoes ("+pct(scroll50,scroll25)+"% dos que scrollaram)\n- 75%: "+scroll75+" sessoes ("+pct(scroll75,scroll25)+"% dos que scrollaram)\n- 100%: "+scroll100+" sessoes ("+pct(scroll100,scroll25)+"% dos que scrollaram)\n\nDe 3 a 5 insights praticos e diretos sobre engajamento, drop-off e melhorias concretas para aumentar conversao. Use os dados. Responda em portugues, sem introducao.";
  try{
    const Anthropic=require("@anthropic-ai/sdk");
    const client=new Anthropic({apiKey:key});
    const msg=await client.messages.create({model:"claude-sonnet-4-6",max_tokens:900,messages:[{role:"user",content:prompt}]});
    res.json({insights:msg.content[0].text});
  }catch(e){res.status(500).json({error:e.message});}
});
app.get('/api/monitor/screenshot',(req,res)=>{const strategy=req.query.strategy||'mobile';const c=readPsCache();const key='screenshot_'+strategy;if(c&&c[key])return res.json({data:c[key].data,width:c[key].width,height:c[key].height,cachedAt:c[key].cachedAt});res.status(404).json({error:'Screenshot nao disponivel. Rode o PageSpeed primeiro.'});});
// ===== RH: COLABORADORES =====
app.get('/api/rh/colaboradores',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(u,d);const cargo=p[u]?.cargo||'';
    if(!(['master','anjo-caido','admin'].includes(role)||isRH(u,cargo)))return res.status(403).json({error:'Sem permissao'});
    const feriasAll=readFerias().filter(f=>f.status==='aprovado');
    const hoje=new Date();hoje.setHours(0,0,0,0);
    const colabs=Object.keys(d.users||{}).map(k=>{
      const prof=p[k]||{};
      const dataEntrada=prof.dataEntrada||null;
      let saldo=null;let tenureDays=null;
      if(dataEntrada){
        const entrada=new Date(dataEntrada+'T00:00:00');
        tenureDays=Math.floor((hoje-entrada)/(1000*60*60*24));
        if(tenureDays>=365){
          const userFerias=feriasAll.filter(f=>f.user===k);
          let used=0;
          userFerias.forEach(f=>{
            const s=new Date(f.startDate+'T00:00:00'),e=new Date(f.endDate+'T00:00:00');
            // split: fim de ano (dez/jan) = 20d, durante ano = 10d
            let daysRange=Math.round((e-s)/(1000*60*60*24))+1;
            used+=daysRange;
          });
          const usedFimAno=userFerias.filter(f=>{const m=parseInt(f.startDate.split('-')[1]);return m===12||m===1;}).reduce((a,f)=>{const s=new Date(f.startDate+'T00:00:00'),e=new Date(f.endDate+'T00:00:00');return a+Math.round((e-s)/(1000*60*60*24))+1;},0);
          const usedDurante=used-usedFimAno;
          saldo={total:30,used,remaining:Math.max(0,30-used),hasRight:true,fimAno:{total:20,used:Math.min(usedFimAno,20),remaining:Math.max(0,20-usedFimAno)},durante:{total:10,used:Math.min(usedDurante,10),remaining:Math.max(0,10-usedDurante)}};
        } else {
          saldo={total:0,used:0,remaining:0,hasRight:false,daysUntilRight:365-tenureDays};
        }
      }
      return{username:k,email:d.users[k]?.email||'',team:prof.team||'',cargo:prof.cargo||'',dataEntrada,tenureDays,saldo,birthday:prof.birthday||null,hasPhoto:!!(prof.photo),nomeCompleto:prof.nomeCompleto||'',endereco:prof.endereco||'',telefone:prof.telefone||'',emailPerfil:prof.email||'',documento:prof.documento||''};
    }).sort((a,b)=>(a.team||'').localeCompare(b.team||'')||a.username.localeCompare(b.username));
    res.json(colabs);
  }catch(e){res.status(500).json({error:e.message});}
});

app.put('/api/rh/perfil/:username',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(u,d);const cargo=p[u]?.cargo||'';
    if(!(['master','anjo-caido'].includes(role)||isRH(u,cargo)))return res.status(403).json({error:'Sem permissao'});
    const target=req.params.username;
    const{dataEntrada,cargo:newCargo,team,nomeCompleto,endereco,telefone,email:profEmail,documento}=req.body;
    if(!p[target])p[target]={};
    if(dataEntrada!==undefined)p[target].dataEntrada=dataEntrada;
    if(newCargo!==undefined)p[target].cargo=newCargo;
    if(team!==undefined)p[target].team=team;
    if(nomeCompleto!==undefined)p[target].nomeCompleto=nomeCompleto;
    if(endereco!==undefined)p[target].endereco=endereco;
    if(telefone!==undefined)p[target].telefone=telefone;
    if(profEmail!==undefined)p[target].email=profEmail;
    if(documento!==undefined)p[target].documento=documento;
    saveProfiles(p);
    addLog(u,'Perfil RH editado',`${target}`);
    res.json({success:true,profile:p[target]});
  }catch(e){res.status(500).json({error:e.message});}
});


app.get('/api/rh/beneficios',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(u,d);const cargo=p[u]?.cargo||'';
    if(!(['master','anjo-caido','admin'].includes(role)||isRH(u,cargo)))return res.status(403).json({error:'Sem permissao'});
    res.json(readBeneficios());
  }catch(e){res.status(500).json({error:e.message});}
});

app.put('/api/rh/beneficios/:username',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(u,d);const cargo=p[u]?.cargo||'';
    if(!(['master','anjo-caido'].includes(role)||isRH(u,cargo)))return res.status(403).json({error:'Sem permissao'});
    const target=req.params.username;
    const b=readBeneficios();
    if(!b[target])b[target]={};
    const fields=['nomeCompleto','cnpjContratado','status','dataContrato','tipoContrato','tipoVT','deslocamento','estacionamento','academia','alimentacao'];
    fields.forEach(f=>{if(req.body[f]!==undefined)b[target][f]=req.body[f];});
    if(req.body.meses!==undefined)b[target].meses=req.body.meses;
    saveBeneficios(b);
    addLog(u,'Beneficios editados',target);
    res.json({success:true,beneficios:b[target]});
  }catch(e){res.status(500).json({error:e.message});}
});

app.get('/api/rh/export/csv',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(u,d);const cargo=p[u]?.cargo||'';
    if(!(['master','anjo-caido','admin'].includes(role)||isRH(u,cargo)))return res.status(403).json({error:'Sem permissao'});
    const tipo=req.query.tipo||'all';
    let rows=[];
    if(tipo==='all'||tipo==='ferias'){rows=[...rows,...readFerias().map(f=>({...f,tipo:'Ferias'}))]}
    if(tipo==='all'||tipo==='folgas'){rows=[...rows,...readFolgas().map(f=>({...f,tipo:'Folga'}))]}
    rows.sort((a,b)=>new Date(b.requestedAt||0)-new Date(a.requestedAt||0));
    const header='Tipo,Usuario,Cargo,Time,Data Saida,Data Retorno,Status,Solicitado em,Lider Direto,Motivo';
    const lines=rows.map(r=>[r.tipo,r.user,r.cargo||'',r.team||'',r.startDate,r.endDate,r.status,r.requestedAt?r.requestedAt.slice(0,10):'',r.liderDireto||'',r.rejectionReason||r.cancelReason||''].map(v=>`"${String(v).replace(/"/g,'""')}"`).join(','));
    res.setHeader('Content-Type','text/csv; charset=utf-8');
    res.setHeader('Content-Disposition','attachment; filename="ausencias.csv"');
    res.send('﻿'+header+'\n'+lines.join('\n'));
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/rh/confirmar-retorno/:tipo/:id',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(u,d);const cargo=p[u]?.cargo||'';
    if(!(['master','anjo-caido','admin'].includes(role)||isRH(u,cargo)))return res.status(403).json({error:'Sem permissao'});
    const tipo=req.params.tipo;const id=req.params.id;
    if(tipo==='ferias'){
      const arr=readFerias();const idx=arr.findIndex(f=>String(f.id)===String(id));
      if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
      arr[idx].returnedAt=new Date().toISOString();arr[idx].returnedBy=u;
      saveFerias(arr);addLog(u,'Retorno confirmado','ferias de '+arr[idx].user);
    } else if(tipo==='folgas'){
      const arr=readFolgas();const idx=arr.findIndex(f=>String(f.id)===String(id));
      if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
      arr[idx].returnedAt=new Date().toISOString();arr[idx].returnedBy=u;
      saveFolgas(arr);addLog(u,'Retorno confirmado','folga de '+arr[idx].user);
    } else return res.status(400).json({error:'Tipo invalido'});
    res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});


// ===== LIDERES DASHBOARD =====
app.get('/api/lideres/dashboard',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(u,d);const cargo=p[u]?.cargo||'';
    const isMaster=['master','anjo-caido'].includes(role);
    const isRhUser=isRH(u,cargo);
    const isLiderCargo=cargo.startsWith('Lider')||cargo==='Diretoria';
    if(!isMaster&&!isRhUser&&!isLiderCargo)return res.status(403).json({error:'Sem permissao'});
    let teamFilter=null;
    if(!isMaster&&!isRhUser){
      if(cargo==='Diretoria')teamFilter=null;
      else teamFilter=cargo.replace('Lider ','');
    }
    if(req.query.team!==undefined&&(isMaster||isRhUser))teamFilter=req.query.team||null;
    const today=new Date();today.setHours(0,0,0,0);
    const ferias=readFerias();const folgas=readFolgas();
    const feriasF=ferias.filter(f=>teamFilter?(f.team===teamFilter||f.liderDireto===u):true);
    const folgasF=folgas.filter(f=>teamFilter?(f.team===teamFilter||f.liderDireto===u):true);
    const colaboradores=Object.keys(d.users||{}).filter(k=>{
      if(teamFilter)return(p[k]?.team||'')===teamFilter;
      return true;
    }).map(k=>({username:k,email:d.users[k]?.email||'',team:p[k]?.team||'',cargo:p[k]?.cargo||'',hasPhoto:!!(p[k]?.photo),photo:p[k]?.photo||null,birthday:p[k]?.birthday||null})).sort((a,b)=>(a.team||'').localeCompare(b.team||'')||a.username.localeCompare(b.username));
    const ausentes=[
      ...feriasF.filter(f=>{if(f.status!=='aprovado')return false;const s=new Date(f.startDate+'T00:00:00'),e=new Date(f.endDate+'T23:59:59');return today>=s&&today<=e;}).map(f=>({...f,tipo:'Ferias'})),
      ...folgasF.filter(f=>{if(f.status!=='aprovado')return false;const s=new Date(f.startDate+'T00:00:00'),e=new Date(f.endDate+'T23:59:59');return today>=s&&today<=e;}).map(f=>({...f,tipo:'Folga'}))
    ].sort((a,b)=>new Date(a.endDate)-new Date(b.endDate));
    const pendentes=[
      ...feriasF.filter(f=>f.status==='pendente').map(f=>({...f,tipo:'Ferias'})),
      ...folgasF.filter(f=>f.status==='pendente').map(f=>({...f,tipo:'Folga'}))
    ].sort((a,b)=>new Date(a.requestedAt||0)-new Date(b.requestedAt||0));
    const aprovadas=[
      ...feriasF.filter(f=>f.status==='aprovado').map(f=>({...f,tipo:'Ferias'})),
      ...folgasF.filter(f=>f.status==='aprovado').map(f=>({...f,tipo:'Folga'}))
    ];
    const todasSolicitacoes=[
      ...feriasF.map(f=>({...f,tipo:'Ferias'})),
      ...folgasF.map(f=>({...f,tipo:'Folga'}))
    ].sort((a,b)=>new Date(b.requestedAt||0)-new Date(a.requestedAt||0));
    const teams=['Atenção','Comercial','Eventos','Concierge','Suporte','Administrativo','Financeiro','Diretoria','Recursos Humanos'];
    res.json({meuTime:teamFilter,meuCargo:cargo,canSelectTeam:isMaster||isRhUser,teams,colaboradores,ausentes,pendentes,aprovadas,todasSolicitacoes});
  }catch(e){res.status(500).json({error:e.message});}
});


// ===== SISTEMA DE COMPRAS =====
const COMPRAS_FILE='/app/compras.json';
function readCompras(){try{return JSON.parse(fs.readFileSync(COMPRAS_FILE,'utf8'));}catch(e){return[];}}
function saveCompras(d){fs.writeFileSync(COMPRAS_FILE,JSON.stringify(d,null,2));}

app.get('/api/compras',(req,res)=>{
  const u=req.headers['remote-user']||'desconhecido';
  const d=readUsers();const p=readProfiles();
  const role=getUserRole(u,d);const cargo=p[u]?.cargo||'';
  const all=readCompras();
  if(u==='saulorogerio'||isRH(u,cargo)||['master','anjo-caido'].includes(role))return res.json(all);
  if(cargo.startsWith('Lider ')){const meuTime=cargo.replace('Lider ','');return res.json(all.filter(c=>c.user===u||(c.team===meuTime&&c.status==='pendente')));}
  res.json(all.filter(c=>c.user===u));
});

app.post('/api/compras/solicitar',(req,res)=>{
  try{
    const u=req.headers['remote-user']||'desconhecido';
    const{produto,link,motivo,urgencia,valor}=req.body;
    if(!produto||!motivo)return res.status(400).json({error:'Produto e motivo obrigatorios'});
    const prof=readProfiles()[u]||{};
    const compras=readCompras();
    const isLider=(prof.cargo||'').startsWith('Lider ');
    const initStatus=isLider?'aguardando_rh':'pendente';
    compras.push({id:Date.now(),user:u,team:prof.team||'',cargo:prof.cargo||'',produto,link:link||'',motivo,urgencia:urgencia||'Media',valor:parseFloat(valor)||0,status:initStatus,requestedAt:new Date().toISOString()});
    saveCompras(compras);addLog(u,'Compra solicitada',produto);
    res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});


app.post('/api/compras/aprovar-lider/:id',(req,res)=>{
  try{
    const approver=req.headers['remote-user']||'desconhecido';
    const p=readProfiles();
    const cargo=p[approver]?.cargo||'';
    if(!cargo.startsWith('Lider ')&&approver!=='saulorogerio'){const d=readUsers();const role=getUserRole(approver,d);if(!['master','anjo-caido'].includes(role))return res.status(403).json({error:'Sem permissao'});}
    const meuTime=cargo.replace('Lider ','');
    const compras=readCompras();
    const idx=compras.findIndex(c=>String(c.id)===String(req.params.id));
    if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
    if(cargo.startsWith('Lider ')&&compras[idx].team!==meuTime)return res.status(403).json({error:'Nao pertence ao seu time'});
    if(compras[idx].status!=='pendente')return res.status(400).json({error:'Solicitacao nao esta pendente'});
    compras[idx].status='aguardando_rh';compras[idx].aprovadoLiderPor=approver;compras[idx].aprovadoLiderAt=new Date().toISOString();
    saveCompras(compras);addLog(approver,'Compra aprovada pelo lider',compras[idx].produto);
    res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/compras/rejeitar-lider/:id',(req,res)=>{
  try{
    const approver=req.headers['remote-user']||'desconhecido';
    const p=readProfiles();
    const cargo=p[approver]?.cargo||'';
    if(!cargo.startsWith('Lider ')&&approver!=='saulorogerio'){const d=readUsers();const role=getUserRole(approver,d);if(!['master','anjo-caido'].includes(role))return res.status(403).json({error:'Sem permissao'});}
    const meuTime=cargo.replace('Lider ','');
    const{rejectionReason}=req.body;
    const compras=readCompras();
    const idx=compras.findIndex(c=>String(c.id)===String(req.params.id));
    if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
    if(cargo.startsWith('Lider ')&&compras[idx].team!==meuTime)return res.status(403).json({error:'Nao pertence ao seu time'});
    compras[idx].status='rejeitado';compras[idx].rejectedBy=approver;compras[idx].rejectedAt=new Date().toISOString();compras[idx].rejectedByRole='lider';
    if(rejectionReason)compras[idx].rejectionReason=rejectionReason;
    saveCompras(compras);addLog(approver,'Compra rejeitada pelo lider',compras[idx].produto);
    res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/compras/aprovar/:id',(req,res)=>{
  try{
    const approver=req.headers['remote-user']||'desconhecido';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(approver,d);const cargo=p[approver]?.cargo||'';
    if(!['master','anjo-caido'].includes(role)&&!isRH(approver,cargo))return res.status(403).json({error:'Sem permissao'});
    const compras=readCompras();
    const idx=compras.findIndex(c=>String(c.id)===String(req.params.id));
    if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
    compras[idx].status='aprovado';compras[idx].approvedBy=approver;compras[idx].approvedAt=new Date().toISOString();
    saveCompras(compras);addLog(approver,'Compra aprovada',compras[idx].produto);
    res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/compras/rejeitar/:id',(req,res)=>{
  try{
    const approver=req.headers['remote-user']||'desconhecido';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(approver,d);const cargo=p[approver]?.cargo||'';
    if(!['master','anjo-caido'].includes(role)&&!isRH(approver,cargo))return res.status(403).json({error:'Sem permissao'});
    const{rejectionReason}=req.body;
    const compras=readCompras();
    const idx=compras.findIndex(c=>String(c.id)===String(req.params.id));
    if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
    compras[idx].status='rejeitado';compras[idx].rejectedBy=approver;compras[idx].rejectedAt=new Date().toISOString();
    if(rejectionReason)compras[idx].rejectionReason=rejectionReason;
    saveCompras(compras);addLog(approver,'Compra rejeitada',compras[idx].produto);
    res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/compras/comprado/:id',(req,res)=>{
  try{
    const user=req.headers['remote-user']||'desconhecido';
    const d=readUsers();const p=readProfiles();
    const role=getUserRole(user,d);const cargo=p[user]?.cargo||'';
    if(!['master','anjo-caido'].includes(role)&&!isRH(user,cargo))return res.status(403).json({error:'Sem permissao'});
    const{valorFinal}=req.body;
    const compras=readCompras();
    const idx=compras.findIndex(c=>String(c.id)===String(req.params.id));
    if(idx===-1)return res.status(404).json({error:'Nao encontrado'});
    compras[idx].status='comprado';compras[idx].compradoPor=user;compras[idx].compradoAt=new Date().toISOString();
    compras[idx].valorFinal=valorFinal!==undefined?parseFloat(valorFinal)||compras[idx].valor:compras[idx].valor;
    saveCompras(compras);addLog(user,'Compra realizada',compras[idx].produto);
    res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/api/compras/delete/:id',(req,res)=>{
  try{
    const user=req.headers['remote-user']||'desconhecido';
    const compras=readCompras();
    const item=compras.find(c=>String(c.id)===String(req.params.id));
    if(!item)return res.status(404).json({error:'Nao encontrado'});
    if(user!=='saulorogerio'&&item.user!==user)return res.status(403).json({error:'Sem permissao'});
    saveCompras(compras.filter(c=>String(c.id)!==String(req.params.id)));
    res.json({success:true});
  }catch(e){res.status(500).json({error:e.message});}
});

app.listen(3000,()=>console.log('API V25K BLINDADA ONLINE'));
