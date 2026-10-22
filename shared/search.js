/* Site search: searches the product catalog in the browser, no server needed.
   Opens from the header button or the "/" key. On product pages the catalog loads on first use. */
(function(){
  "use strict";
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
  function search(text){
    var C=window.CATALOG||[], STATES=window.CATALOG_STATES||[], t=tokens(text); if(!t.length) return {states:[],products:[]};
    var lv=t.indexOf("master")>-1?"Master":(t.indexOf("journeyman")>-1?"Journeyman":null);
    var st=t.filter(function(w){return w!=="master"&&w!=="journeyman";});
    var stateHits=st.length?STATES.concat([GENERAL]).filter(function(s){var l=s.toLowerCase();return st.every(function(w){return l.indexOf(w)>-1;})||st.some(function(w){return w.length>2&&l.indexOf(w)===0;});}).slice(0,4):[];
    var scored=C.map(function(p){
      var hay=(p.title+" "+(p.state||"any state general")+" "+p.level+" "+p.tierName+" "+p.year).toLowerCase(), sc=0;
      t.forEach(function(w){ if(hay.indexOf(w)>-1){sc+=1; if(p.tierName.toLowerCase().indexOf(w)>-1)sc+=1; if((p.state||"").toLowerCase().indexOf(w)>-1)sc+=2; if(p.level.toLowerCase()===w)sc+=2;} });
      var allIn=t.every(function(w){return hay.indexOf(w)>-1;});
      return {p:p,sc:allIn?sc+5:sc};
    }).filter(function(x){return x.sc>0;}).sort(function(a,b){return b.sc-a.sc||a.p.rank-b.p.rank;}).slice(0,8);
    return {states:stateHits,products:scored.map(function(x){return x.p;}),level:lv};
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
  if((window.SITE||{}).aiFinder){var ai=document.createElement("script");ai.src=BASE+"shared/ai-finder.js";ai.defer=true;document.head.appendChild(ai);}
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
