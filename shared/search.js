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
  /* forgiving matching: typos ("florda", "jouneyman"), abbreviations ("FL", "tx") */
  var ABBR={al:"Alabama",ak:"Alaska",az:"Arizona",ar:"Arkansas",ca:"California",co:"Colorado",ct:"Connecticut",de:"Delaware",fl:"Florida",ga:"Georgia",hi:"Hawaii",id:"Idaho",il:"Illinois","in":"Indiana",ia:"Iowa",ks:"Kansas",ky:"Kentucky",la:"Louisiana",me:"Maine",md:"Maryland",ma:"Massachusetts",mi:"Michigan",mn:"Minnesota",ms:"Mississippi",mo:"Missouri",mt:"Montana",ne:"Nebraska",nv:"Nevada",nh:"New Hampshire",nj:"New Jersey",nm:"New Mexico",ny:"New York",nc:"North Carolina",nd:"North Dakota",oh:"Ohio",ok:"Oklahoma",or:"Oregon",pa:"Pennsylvania",ri:"Rhode Island",sc:"South Carolina",sd:"South Dakota",tn:"Tennessee",tx:"Texas",ut:"Utah",vt:"Vermont",va:"Virginia",wa:"Washington",wv:"West Virginia",wi:"Wisconsin",wy:"Wyoming"};
  /* two-letter codes that are also everyday words only count when typed in capitals */
  var ABBR_WORDS={"in":1,or:1,me:1,hi:1,ok:1,oh:1,de:1,la:1,pa:1,ma:1,al:1,id:1,co:1,ga:1,mo:1,ne:1,wa:1,ar:1,mi:1,ia:1,ms:1,mt:1};
  function lev(a,b){ if(a===b) return 0; var m=a.length,n=b.length; if(Math.abs(m-n)>2) return 9; var d=[],i,j; for(i=0;i<=m;i++){d[i]=[i];} for(j=1;j<=n;j++) d[0][j]=j;
    for(i=1;i<=m;i++) for(j=1;j<=n;j++) { d[i][j]=Math.min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]===b[j-1]?0:1)); if(i>1&&j>1&&a[i-1]===b[j-2]&&a[i-2]===b[j-1]) d[i][j]=Math.min(d[i][j],d[i-2][j-2]+1); } return d[m][n]; }
  function okTypo(word,name){ var l=word.length; if(l<5) return false; return lev(word,name)<=(l>=8?2:1); }
  function matchStates(q,n){
    var S0=(window.CATALOG_STATES||[]), v=String(q||"").toLowerCase().replace(/[^a-z ]/g," ").replace(/\s+/g," ").trim(); if(!v) return [];
    if(v.length===2&&ABBR[v]&&S0.indexOf(ABBR[v])>-1) return [ABBR[v]];
    var scored=S0.map(function(s){ var l=s.toLowerCase(), sc=9;
      if(l===v) sc=0; else if(l.indexOf(v)===0) sc=1; else if(l.split(" ").some(function(w){return w.indexOf(v)===0;})) sc=2; else if(v.length>2&&l.indexOf(v)>-1) sc=3; else if(okTypo(v,l)||(v.length>=4&&lev(v,l.slice(0,v.length))<=1)) sc=4;
      return {s:s,sc:sc}; }).filter(function(x){return x.sc<9;}).sort(function(a,b){return a.sc-b.sc||a.s.localeCompare(b.s);});
    return scored.slice(0,n||6).map(function(x){return x.s;});
  }
  function findState(text){
    var l=" "+text.toLowerCase().replace(/[^a-z ]/g," ").replace(/\s+/g," ")+" ", S=(window.CATALOG_STATES||[]).slice().sort(function(a,b){return b.length-a.length;});
    for(var i=0;i<S.length;i++){ if(l.indexOf(" "+S[i].toLowerCase()+" ")>-1) return {state:S[i],words:tokens(S[i])}; }
    var raw=String(text).replace(/[^A-Za-z ]/g," ").split(/\s+/).filter(Boolean);
    for(i=0;i<raw.length;i++){ var w=raw[i].toLowerCase(); if(w.length===2&&ABBR[w]&&S.indexOf(ABBR[w])>-1&&(!ABBR_WORDS[w]||raw[i]===raw[i].toUpperCase())) return {state:ABBR[w],words:[w]}; }
    var t=tokens(text);
    for(i=0;i<t.length;i++){
      var two=t[i+1]?t[i]+" "+t[i+1]:null;
      for(var k=0;k<S.length;k++){ var nm=S[k].toLowerCase();
        if(two&&nm.indexOf(" ")>-1&&okTypo(two,nm)) return {state:S[k],words:[t[i],t[i+1]]};
        if(nm.indexOf(" ")<0&&okTypo(t[i],nm)) return {state:S[k],words:[t[i]]}; }
    }
    return null;
  }
  function findLevel(t){
    for(var i=0;i<t.length;i++){ var w=t[i];
      if(/^journ/.test(w)||w==="jman"||w==="jmen"||w==="jw"||lev(w,"journeyman")<=2||lev(w,"journeymen")<=2) return {level:"Journeyman",word:w};
      if(w==="master"||w==="masters"||(w.length>=5&&lev(w,"master")<=1)) return {level:"Master",word:w}; }
    return null;
  }
  function search(text){
    var C=window.CATALOG||[], STATES=window.CATALOG_STATES||[], all=tokens(text); if(!all.length) return {states:[],products:[]};
    var L=findLevel(all), lv=L?L.level:null;
    var F=findState(text), state=F?F.state:null;
    var stWords=F?F.words:[];
    /* what is left once state, level and filler words are taken out, e.g. "flash cards" or "ultimate" */
    var rest=all.filter(function(w){return !STOP[w]&&(!L||w!==L.word)&&stWords.indexOf(w)<0&&!/^20\d\d$/.test(w);});
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
  window.SRCH={open:open,close:close,ensureCatalog:ensureCatalog,pathFor:pathFor,BASE:BASE,q:q,matchStates:matchStates,findState:findState};
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
