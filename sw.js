const CACHE='kitmsk-v1';
const CORE=['./','./index.html','./manifest.webmanifest','./icon.png'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>Promise.all(CORE.map(u=>c.add(u).catch(()=>{})))));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{const u=e.request.url;
 if(u.indexOf('firestore.googleapis.com')>=0||u.indexOf('firebaseio')>=0||u.indexOf('googleapis.com')>=0){return;}
 e.respondWith(fetch(e.request).then(r=>{try{const rc=r.clone();caches.open(CACHE).then(c=>c.put(e.request,rc)).catch(()=>{});}catch(_){}return r;}).catch(()=>caches.match(e.request).then(m=>m||caches.match('./index.html'))));});
