/* Site search: searches the product catalog in the browser, no server needed.
   Opens from the header button or the "/" key. On product pages the catalog loads on first use. */
(function(){
  "use strict";
  var VER=((document.currentScript&&document.currentScript.src)||"").split("?")[1]||"";
  var ROUTE=window.ROUTE||{}, GENERAL="General (any state)";
  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function money(v){return "$"+Number(v).toFixed(2);}
  function slugState(s){return s===GENERAL?"general":s.toLowerCase().replace(/ /g,"-");}
  var BASE=(function(){if(window.__B)return window.__B;var p=location.pathname.replace(/index\.html$/,"");var parts=p.split("/");if(parts[parts.length-1]==="")parts.pop();for(var i=0;i<(ROUTE.depth||0);i++)parts.pop();return parts.join("/")+"/";})();
  function pathFor(p){if(!(p.rank>0))return BASE+"#singles";return BASE+slugState(p.state||GENERAL)+"/"+p.level.toLowerCase()+"/"+p.year+"/"+p.tierSlug+"/";}
  function levelPath(state,level,year){return BASE+slugState(state)+"/"+level.toLowerCase()+"/"+year+"/";}

  /* overlay */
  var ov=document.createElement("div"); ov.id="search"; ov.className="srch"; ov.hidden=true; ov.setAttribute("aria-hidden","true");
  ov.innerHTML='<div class="srch-back" data-sclose></div><div class="srch-box" role="dialog" aria-modal="true" aria-label="Search">'+
    '<form class="srch-form" role="search" action="'+esc(BASE)+'search/" method="get"><input class="srch-q" name="q" type="search" placeholder="Search a state, package or product…" autocomplete="off" aria-label="Search"><button type="button" class="srch-x" data-sclose aria-label="Close">×</button></form>'+
    '<div class="srch-res" id="srchRes" aria-live="polite"></div><p class="srch-hint">Try “Texas master”, “flash cards” or “ultimate combo”. Press Esc to close.</p></div>';
  document.body.appendChild(ov);
  var q=ov.querySelector(".srch-q"), res=document.getElementById("srchRes"), opener=null;

  function ensureCatalog(cb){
    if(window.CATALOG){cb();return;}
    if(ensureCatalog.loading){ensureCatalog.cbs.push(cb);return;}
    ensureCatalog.loading=true; ensureCatalog.cbs=[cb];
    var s=document.createElement("script"); s.src=BASE+"shared/catalog.js"; s.onload=function(){ensureCatalog.cbs.forEach(function(f){f();});}; document.head.appendChild(s);
  }
  function tokens(s){return s.toLowerCase().replace(/[^a-z0-9+ ]/g," ").split(/\s+/).filter(Boolean);}
  /* words that say nothing about which product, so they never decide a match */
  var STOP={looking:1,look:1,for:1,the:1,a:1,an:1,in:1,of:1,to:1,my:1,me:1,i:1,im:1,need:1,want:1,get:1,buy:1,best:1,find:1,show:1,what:1,which:1,is:1,are:1,and:1,or:1,with:1,on:1,exam:1,exams:1,test:1,prep:1,preparation:1,study:1,license:1,licence:1,electrician:1,electrical:1,electric:1,package:1,packages:1,course:1,state:1,please:1,help:1,pass:1,passing:1,materials:1,material:1,stuff:1,good:1,cheap:1};
  function findState(text){
    var l=" "+text.toLowerCase().replace(/[^a-z ]/g," ").replace(/\s+/g," ")+" ", S=(window.CATALOG_STATES||[]).slice().sort(function(a,b){return b.length-a.length;});
    for(var i=0;i<S.length;i++){ if(l.indexOf(" "+S[i].toLowerCase()+" ")>-1) return S[i]; }
    return null;
  }
  function search(text){
    var C=window.CATALOG||[], STATES=window.CATALOG_STATES||[], all=tokens(text); if(!all.length) return {states:[],products:[]};
    var lv=all.indexOf("master")>-1?"Master":(all.indexOf("journeyman")>-1||all.indexOf("journeymen")>-1?"Journeyman":null);
    var state=findState(text);
    var stWords=state?tokens(state):[];
    /* what is left once state, level and filler words are taken out, e.g. "flash cards" or "ultimate" */
    var rest=all.filter(function(w){return !STOP[w]&&w!=="master"&&w!=="journeyman"&&w!=="journeymen"&&stWords.indexOf(w)<0&&!/^20\d\d$/.test(w);});
    var stateHits;
    if(state) stateHits=[state];
    else stateHits=rest.length?STATES.concat([GENERAL]).filter(function(s){var l=s.toLowerCase();return rest.every(function(w){return l.indexOf(w)>-1;})||rest.some(function(w){return w.length>2&&l.indexOf(w)===0;});}).slice(0,4):[];
    var pool=C.filter(function(p){
      if(lv&&p.level!==lv&&p.level!=="General") return false;
      if(state&&p.state&&p.state!==state) return false;           /* a state was named: no other state's products */
      if(state&&!p.state&&!rest.length) return false;               /* "texas master" shows the Texas packages only */
      if(state&&!p.state&&p.rank>0) return false;                   /* the any-state version of a package Texas already has */
      return true;
    });
    var scored=pool.map(function(p){
      var tier=p.tierName.toLowerCase(), sc=0;
      rest.forEach(function(w){ if(tier.indexOf(w)>-1) sc+=3; });
      if(state&&p.state===state) sc+=2;
      return {p:p,sc:sc};
    });
    var hits=rest.length?scored.filter(function(x){return x.sc>=(state?3:1);}):scored.filter(function(){return !!(state||lv);});
    if(!hits.length&&state) hits=scored.filter(function(x){return x.p.state===state;});   /* unknown extra words: still show that state */
    hits=hits.sort(function(a,b){return b.sc-a.sc||a.p.rank-b.p.rank||Number(a.p.price)-Number(b.p.price);}).slice(0,8);
    var scored2=hits;
    return {states:stateHits,products:scored2.map(function(x){return x.p;}),level:lv};
  }
  function stateRows(r,yr){return r.states.map(function(s){var rows="";if(!r.level||r.level==="Journeyman")rows+='<a class="srch-row" href="'+esc(levelPath(s,"Journeyman",yr))+'"><b>'+esc(s)+'</b><span>Journeyman packages</span></a>';if(!r.level||r.level==="Master")rows+='<a class="srch-row" href="'+esc(levelPath(s,"Master",yr))+'"><b>'+esc(s)+'</b><span>Master packages</span></a>';return rows;}).join("");}
  function render(text){
    var r=search(text);
    var AI=window.AI_ROW; if(!text.trim()){res.innerHTML=AI?AI(""):"";return;}
    var yr=(window.CATALOG||[]).map(function(p){return p.year;}).sort().reverse()[0]||"2026";
    var h=AI?AI(text):"";
    if(r.states.length) h+='<div class="srch-sec">States</div>'+stateRows(r,yr);
    if(r.products.length) h+='<div class="srch-sec">Products</div>'+r.products.map(function(p){return '<a class="srch-row" href="'+esc(pathFor(p))+'"><img src="'+esc(p.image)+'" alt="" loading="lazy"><span class="srch-t"><b>'+esc(p.tierName)+'</b><small>'+esc((p.state||"Any state")+" · "+p.level+" · "+p.year)+'</small></span><span class="srch-p">'+money(p.price)+'</span></a>';}).join("");
    if(!r.states.length&&!r.products.length) h+='<p class="srch-none">Nothing found for “'+esc(text)+'”. Try a state name or “journeyman” / “master”.</p>';
    res.innerHTML=h;
  }
  function open(){opener=document.activeElement;ov.hidden=false;ov.setAttribute("aria-hidden","false");document.documentElement.classList.add("modal-open");setTimeout(function(){q.focus();},20);ensureCatalog(function(){render(q.value);});}
  function close(){ov.hidden=true;ov.setAttribute("aria-hidden","true");document.documentElement.classList.remove("modal-open");if(opener&&opener.focus)opener.focus();}
  var tmr; q.addEventListener("input",function(){clearTimeout(tmr);tmr=setTimeout(function(){ensureCatalog(function(){render(q.value);});},80);});
  q.closest("form").addEventListener("submit",function(e){var first=res.querySelector("a.srch-row");if(first){e.preventDefault();location.href=first.href;}});
  document.addEventListener("click",function(e){if(e.target.closest("[data-sopen]")){e.preventDefault();open();}else if(e.target.closest("[data-sclose]")){e.preventDefault();close();}});
  document.addEventListener("keydown",function(e){
    if(e.key==="Escape"&&!ov.hidden){close();return;}
    if(e.key==="/"&&ov.hidden&&!/input|textarea|select/i.test((document.activeElement||{}).tagName||"")){e.preventDefault();open();}
  });
  /* AI exam advisor (shared/ai-finder.js), only when aiFinderUrl is set in site-config.json */
  window.SRCH={open:open,close:close,ensureCatalog:ensureCatalog,pathFor:pathFor,BASE:BASE,q:q};
  if((window.SITE||{}).aiFinder){var ai=document.createElement("script");ai.src=BASE+"shared/ai-finder.js"+(VER?"?"+VER:"");ai.defer=true;document.head.appendChild(ai);}
  /* /search/?q= page support */
  var sp=document.getElementById("searchPage");
  if(sp){var m=location.search.match(/[?&]q=([^&]*)/);var val=m?decodeURIComponent(m[1].replace(/\+/g," ")):"";var inp=sp.querySelector("input");inp.value=val;
    function go(){ensureCatalog(function(){var r=search(inp.value);var out=document.getElementById("searchOut");var yr=(window.CATALOG||[]).map(function(p){return p.year;}).sort().reverse()[0]||"2026";
      var h=stateRows(r,yr)+
        r.products.map(function(p){return '<a class="srch-row" href="'+esc(pathFor(p))+'"><img src="'+esc(p.image)+'" alt=""><span class="srch-t"><b>'+esc(p.tierName)+'</b><small>'+esc((p.state||"Any state")+" · "+p.level+" · "+p.year)+'</small></span><span class="srch-p">'+money(p.price)+'</span></a>';}).join("");
      out.innerHTML=h||(inp.value.trim()?'<p class="srch-none">Nothing found. Try a state name or “journeyman” / “master”.</p>':"");
      document.title=(inp.value.trim()?"Search: "+inp.value+" | ":"Search | ")+((window.SITE||{}).brand||"");});}
    inp.addEventListener("input",function(){clearTimeout(tmr);tmr=setTimeout(go,80);}); sp.addEventListener("submit",function(e){e.preventDefault();go();history.replaceState(null,"","?q="+encodeURIComponent(inp.value));}); go();}
})();
