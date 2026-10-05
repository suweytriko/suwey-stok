const C="suwey-v2";
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(["./","index.html","manifest.webmanifest","icon-192.png","apple-touch-icon.png"])));self.skipWaiting()});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
// Stok verisi ve sayfa: önce internetten dene, yoksa son kaydedileni göster. Fotoğraflar: önbellekten.
self.addEventListener("fetch",e=>{const r=e.request;if(r.method!=="GET")return;const u=new URL(r.url);
  const fresh=u.origin===location.origin&&((u.pathname.endsWith("data.json")||u.pathname.endsWith("crm.enc"))||r.mode==="navigate"||u.pathname.endsWith(".html"));
  if(fresh){e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(C).then(c=>c.put(r,cp));return res}).catch(()=>caches.match(r).then(m=>m||caches.match("index.html"))));return}
  e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{if(res.ok&&(u.origin===location.origin||u.host.includes("gstatic")||u.host.includes("googleapis"))){const cp=res.clone();caches.open(C).then(c=>c.put(r,cp))}return res})))});
