/* Exam advisor ("Max") inside the site search.
   Loaded by search.js only when "aiFinderUrl" is set in site-config.json.

   Built so anyone can use it without typing: it asks one simple question at a time with big buttons
   (state, which test, what they want) and shows the best package. Those steps run right here in the
   browser from catalog.js, so they are instant. Typing a question goes to the AI on the Cloudflare Worker.
   Buy now uses the same tagged checkout links as the rest of the site. */
(function(){
  "use strict";
  var S=window.SRCH, SITE=window.SITE||{}; if(!S||!SITE.aiFinder) return;
  var ENDPOINT=SITE.aiFinder.replace(/\/+$/,"")+(/\/chat$/.test(SITE.aiFinder)?"":"/chat");
  var STORE=SITE.storeUrl||"https://1examprep.com", KEY="ai_advisor_v3", NAME="Max";
  var PHONE=SITE.phone||((document.querySelector('a[href^="tel:"]')||{}).textContent||"").trim();
  function hello(){var h=new Date().getHours();return h<5?"Hi":h<12?"Good morning":h<18?"Good afternoon":"Good evening";}
  function greeting(){return hello()+"! I'm "+NAME+". I'll help you find the right books for your electrician test.\n\nIt's easy. Just tap your answers.";}

  /* ---- the guided questions ---- */
  var POPULAR=["Texas","Florida","California","New York","Georgia","North Carolina"];
  var LEVELS=[
    {v:"Journeyman",e:"🔧",t:"Journeyman",s:"My first electrician license"},
    {v:"Master",e:"⚡",t:"Master",s:"I'm already a journeyman and want to go higher"},
    {v:"unsure",e:"🤔",t:"I'm not sure",s:"Help me figure it out"}
  ];
  var WANTS=[
    {v:"ultimate",e:"⭐",t:"Everything",s:"Best chance to pass. Books, code book, flash cards and online tests"},
    {v:"nec-tabs",e:"📘",t:"Books and the code book",s:"Study guide plus the code book with tabs"},
    {v:"book-fc",e:"💵",t:"Cheapest way to start",s:"Study guide and flash cards"},
    {v:"help",e:"🙋",t:"Help me choose",s:"Show me the best one"}
  ];
  var WHY={
    ultimate:"Everything you need in one box, including online practice tests.",
    super:"All the books, code book, tabs and flash cards. No online tests.",
    calc:"Study guide, code book and extra practice on the math questions.",
    "nec-tabs":"Study guide plus the code book, already tabbed so you find things fast.",
    "book-fc":"The lowest price way to start studying.",
    nec:"Study guide plus the code book."
  };

  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function money(v){return "$"+Number(v).toFixed(2);}
  function cartUrl(id){return STORE+"/cart/"+id+":1"+(SITE.cartTag||"");}
  function load(){try{return JSON.parse(sessionStorage.getItem(KEY));}catch(e){return null;}}
  function save(){try{sessionStorage.setItem(KEY,JSON.stringify(st));}catch(e){}}
  function fresh(){return {messages:[],slots:{},view:[],greet:greeting()};}
  var st=load()||fresh(), busy=false;
  var reduceMotion=!!(window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches);

  var box=document.querySelector("#search .srch-box"), form=box.querySelector(".srch-form"), res=box.querySelector(".srch-res"), hint=box.querySelector(".srch-hint");
  var AVATAR='<span class="ai-av" aria-hidden="true">'+NAME.charAt(0)+'</span>';

  /* entry point: a row at the top of the normal search results */
  window.AI_ROW=function(text){
    var t=(text||"").trim();
    return '<button type="button" class="srch-row ai-ask" data-ai-ask="'+esc(t)+'">'+AVATAR+'<span class="srch-t"><b>'+(t?'Ask '+NAME+': “'+esc(t.length>48?t.slice(0,48)+"…":t)+'”':"Not sure what you need? Let "+NAME+" help")+'</b><small>Tap a few easy answers and get the right package.</small></span><span class="ai-go">Start</span></button>';
  };

  var panel=document.createElement("div"); panel.className="ai"; panel.hidden=true;
  panel.innerHTML='<div class="ai-head">'+AVATAR+'<div class="ai-who"><b>'+NAME+'</b><small><i class="ai-on-dot"></i><span class="ai-status">Exam helper · online</span></small></div><span class="ai-sp"></span><button type="button" class="ai-link" data-ai-reset>Start over</button><button type="button" class="ai-link" data-ai-back>Search instead</button><button type="button" class="srch-x" data-sclose aria-label="Close">×</button></div>'+
    '<div class="ai-log" aria-live="polite"></div><div class="ai-chips"></div>'+
    '<form class="ai-form" autocomplete="off"><input class="ai-in" type="text" maxlength="400" placeholder="Or type a question for '+NAME+'…" aria-label="Type a question"><button class="ai-send" type="submit" aria-label="Send"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M3 11.5 21 3l-8.5 18-2.2-7.3L3 11.5Z" fill="currentColor"/></svg></button></form>'+
    '<p class="ai-foot">'+NAME+' is an AI helper and only shows products we really sell.'+(PHONE?' Want a person? Call <a href="tel:'+esc(PHONE.replace(/[^0-9+]/g,""))+'">'+esc(PHONE)+'</a>.':'')+'</p>';
  box.appendChild(panel);
  var log=panel.querySelector(".ai-log"), chips=panel.querySelector(".ai-chips"), aForm=panel.querySelector(".ai-form"), input=panel.querySelector(".ai-in"), sendBtn=panel.querySelector(".ai-send"), status=panel.querySelector(".ai-status");

  function parts(text){return String(text||"").split(/\n\s*\n/).map(function(x){return x.trim();}).filter(Boolean).slice(0,3);}
  function scroll(){log.scrollTop=log.scrollHeight;}
  function row(role){
    var r=document.createElement("div"); r.className="ai-line "+role;
    if(role==="bot") r.innerHTML=AVATAR;
    log.appendChild(r); return r;
  }
  function bubble(role,text,fresh){
    var r=row(role), d=document.createElement("div"); d.className="ai-msg "+role+(fresh&&!reduceMotion?" pop":""); d.textContent=text; r.appendChild(d);
    var prev=r.previousElementSibling; if(role==="bot"&&prev&&prev.classList.contains("bot")) prev.classList.add("cont");
    scroll(); return d;
  }

  /* ---- products ---- */
  function byIdMap(){var m={};(window.CATALOG||[]).forEach(function(p){m[String(p.id)]=p;});return m;}
  function cards(products){
    if(!products||!products.length) return;
    var M=byIdMap();
    var html=products.map(function(x,i){
      var p=M[String(x.id)]; if(!p) return "";
      var v=(p.variants||[]).filter(function(v){return v.available!==false;})[0]||(p.variants||[])[0];
      return '<article class="ai-card'+(i===0?" top":"")+'" data-id="'+esc(p.id)+'"><img src="'+esc(p.image)+'" alt="'+esc(p.tierName)+'" loading="lazy" width="88" height="88">'+
        '<div>'+(i===0?'<span class="ai-badge">⭐ Best for you</span>':'<span class="ai-badge alt">Also good</span>')+'<h3>'+esc(p.tierName)+'</h3><small>'+esc((p.state||"Any state")+" · "+p.level)+'</small>'+
        (x.why?'<p class="ai-why">'+esc(x.why)+'</p>':"")+
        '<div class="ai-row"><span class="ai-price">'+money(p.price)+'</span>'+(v?'<a class="btn btn-buy ai-btn" href="'+esc(cartUrl(v.id))+'" rel="noopener">Buy now</a>':"")+'<a class="ai-more" href="'+esc(S.pathFor(p))+'">See what’s inside</a></div></div></article>';
    }).join("");
    if(!html) return;
    var w=document.createElement("div"); w.className="ai-cards"+(reduceMotion?"":" pop"); w.innerHTML=html; log.appendChild(w); scroll();
  }
  /* best package for the answers given, plus one other good option */
  function localPicks(sl){
    var C=(window.CATALOG||[]).filter(function(p){return p.state===sl.state&&p.level===sl.level&&p.rank>0&&(p.variants||[]).some(function(v){return v.available!==false;});});
    if(!C.length) return [];
    function tier(t){return C.filter(function(p){return p.tier===t;})[0];}
    var top, alt;
    if(sl.want==="ultimate"){top=tier("ultimate");alt=tier("super");}
    else if(sl.want==="nec-tabs"){top=tier("nec-tabs");alt=tier("ultimate");}
    else if(sl.want==="book-fc"){top=tier("book-fc");alt=tier("nec-tabs");}
    else {top=tier("ultimate");alt=tier("book-fc");}
    top=top||C.slice().sort(function(a,b){return b.rank-a.rank;})[0];
    return [top,alt].filter(function(p,i,a){return p&&a.indexOf(p)===i;}).map(function(p){return {id:p.id,why:WHY[p.tier]||""};});
  }

  /* ---- big tap buttons ---- */
  function bigButtons(list,kind){
    return '<div class="ai-big" data-kind="'+kind+'">'+list.map(function(o){
      return '<button type="button" class="ai-bigbtn" data-pick="'+esc(o.v)+'" data-label="'+esc(o.t)+'"><span class="ai-emo" aria-hidden="true">'+o.e+'</span><span><b>'+esc(o.t)+'</b><small>'+esc(o.s)+'</small></span></button>';
    }).join("")+'</div>';
  }
  function statePicker(){
    var states=window.CATALOG_STATES||[];
    var pop=POPULAR.filter(function(s){return states.indexOf(s)>-1;});
    return '<div class="ai-big ai-states" data-kind="state"><div class="ai-stbtns">'+pop.map(stateBtn).join("")+'</div>'+
      '<label class="ai-stfind"><span>Not here? Type your state</span><input type="text" class="ai-stin" placeholder="Like Ohio or OH" autocomplete="off" aria-label="Type your state"></label><div class="ai-stmatch"></div></div>';
  }
  function stateBtn(s){return '<button type="button" class="ai-stbtn" data-pick="'+esc(s)+'" data-label="'+esc(s)+'">'+esc(s)+'</button>';}
  function pickerFor(step){
    if(step==="state") return statePicker();
    if(step==="level") return bigButtons(LEVELS,"level");
    if(step==="want") return bigButtons(WANTS,"want");
    if(step==="done") return '<div class="ai-after"><a class="ai-all" href="'+esc(levelUrl())+'">See all '+esc(st.slots.state+" "+st.slots.level)+' packages</a><button type="button" class="ai-again" data-ai-reset>Start over</button></div>';
    return "";
  }
  function levelUrl(){var yr=((window.CATALOG||[])[0]||{}).year||"2026";return S.BASE+st.slots.state.toLowerCase().replace(/ /g,"-")+"/"+st.slots.level.toLowerCase()+"/"+yr+"/";}
  function showPicker(step){
    log.querySelectorAll(".ai-big,.ai-after").forEach(function(n){n.remove();});
    var html=pickerFor(step); if(!html) return;
    var w=document.createElement("div"); w.className="ai-pickwrap"+(reduceMotion?"":" pop"); w.innerHTML=html; log.appendChild(w); scroll();
  }
  function needStep(sl){ if(!sl.state) return "state"; if(!sl.level) return "level"; if(!sl.want) return "want"; return "done"; }
  var QUESTION={state:"Which state is your test in?",level:"Which test are you taking?",want:"What do you want to get?"};

  /* ---- conversation ---- */
  function render(animate){
    log.innerHTML=""; setChips([]);
    if(animate&&!st.view.length){ var g=greetRun={stop:false}; deliver(st.greet||greeting(),[],[],g).then(function(){ if(greetRun===g){greetRun=null; ask(needStep(st.slots));} }); return; }
    parts(st.greet||greeting()).forEach(function(t){bubble("bot",t);});
    st.view.forEach(function(v){ if(v.type==="user") bubble("user",v.text); else { parts(v.text).forEach(function(t){bubble("bot",t);}); cards(v.products); } });
    var last=st.view[st.view.length-1];
    if(last&&last.type==="bot"){ if(last.step) showPicker(last.step); setChips(last.suggestions||[]); }
    else if(!st.view.length) ask(needStep(st.slots));
  }
  function ask(step,lead){
    var text=(lead?lead+"\n\n":"")+(QUESTION[step]||"");
    if(step==="done"){ return showResults(lead); }
    st.view.push({type:"bot",text:text,step:step}); st.messages.push({role:"assistant",content:text}); save();
    return deliver(text,[],[]).then(function(){showPicker(step);});
  }
  function showResults(lead){
    var picks=localPicks(st.slots);
    var text=picks.length?(lead?lead+"\n\n":"")+"Here's the best one for you. Tap Buy now when you're ready.":"Hmm, I couldn't find packages for that. Try another state, or call us"+(PHONE?" at "+PHONE:"")+".";
    var M=byIdMap();
    st.view.push({type:"bot",text:text,products:picks,step:picks.length?"done":"state",suggestions:["How are they different?","Is the test open book?"]});
    st.messages.push({role:"assistant",content:text+(picks.length?" [Shown: "+picks.map(function(x){var p=M[x.id];return p.state+" "+p.level+" "+p.tierName;}).join("; ")+"]":"")});
    save(); track("ai_advisor_recommend",{products:picks.map(function(p){return p.id;}).join(","),mode:"guided"});
    return deliver(text,picks,["How are they different?","Is the test open book?"]).then(function(){showPicker(picks.length?"done":"state");});
  }
  function choose(kind,value,label){
    if(busy) return;
    if(greetRun){greetRun.stop=true;greetRun=null;}
    log.querySelectorAll(".ai-pickwrap").forEach(function(n){n.remove();}); setChips([]);
    st.view.push({type:"user",text:label}); st.messages.push({role:"user",content:label}); bubble("user",label,true);
    track("ai_advisor_tap",{step:kind,value:value});
    var lead="";
    if(kind==="state"){ st.slots.state=value; lead=value+", got it."; }
    if(kind==="level"){
      if(value==="unsure"){ save(); return ask("level","No problem. Most people start with Journeyman. That's your first license. Master is the next step, after you've worked as a journeyman for a few years."); }
      st.slots.level=value; lead=value==="Master"?"Master, nice. That's a big step.":"Journeyman, great choice.";
    }
    if(kind==="want"){ st.slots.want=value; lead=value==="help"?"Sure, here's what I'd get.":"Good pick."; }
    save();
    var step=needStep(st.slots);
    if(step==="done") return showResults(lead);
    return ask(step,lead);
  }

  function setChips(list){ chips.innerHTML=(list||[]).map(function(s){return '<button type="button" class="ai-chip">'+esc(s)+'</button>';}).join(""); }
  function typing(){
    var r=row("bot"); r.classList.add("typing");
    var d=document.createElement("div"); d.className="ai-msg bot"; d.innerHTML='<span class="ai-dots"><i></i><i></i><i></i></span>'; r.appendChild(d);
    var prev=r.previousElementSibling; if(prev&&prev.classList.contains("bot")) prev.classList.add("cont");
    status.textContent=NAME+" is typing…"; scroll();
    return {remove:function(){ r.remove(); var p=log.lastElementChild; if(p&&p.classList.contains("bot")) p.classList.remove("cont"); status.textContent="Exam helper · online"; }};
  }
  function wait(ms){return new Promise(function(r){setTimeout(r,reduceMotion?0:ms);});}
  /* each line takes 1 to 2 seconds of "typing", longer lines a bit longer */
  function pause(text){return Math.max(1000,Math.min(2000,700+String(text).length*12));}
  function setBusy(b){busy=b;sendBtn.disabled=b;input.disabled=b;}
  function track(name,params){try{if(window.dash&&dash.track)dash.track(name,params||{});}catch(e){} try{if(window.gtag)gtag("event",name,params||{});}catch(e){}}

  var greetRun=null;
  function deliver(reply,prods,sugg,ctl,waited){
    var list=parts(reply), i=0, t=null;
    function next(){
      if(ctl&&ctl.stop){ if(t) t.remove(); return Promise.resolve(); }
      if(i>=list.length){ if(t) t.remove(); cards(prods); setChips(sugg); return Promise.resolve(); }
      var text=list[i++];
      if(!t) t=typing();
      return wait(i===1?Math.max(0,pause(text)-(waited||0)):pause(text)).then(function(){ if(ctl&&ctl.stop){ if(t) t.remove(); return; } t.remove(); t=null; bubble("bot",text,true); if(i<list.length) t=typing(); return next(); });
    }
    return next();
  }

  /* typed questions go to the AI */
  function send(text){
    text=(text||"").trim(); if(!text||busy) return;
    if(greetRun){ greetRun.stop=true; greetRun=null; render(false); }
    log.querySelectorAll(".ai-pickwrap").forEach(function(n){n.remove();}); setChips([]);
    st.messages.push({role:"user",content:text}); st.view.push({type:"user",text:text}); bubble("user",text,true);
    input.value=""; setBusy(true);
    var dots=null, t0=Date.now(), slow=setTimeout(function(){dots=typing();},120);
    track("ai_advisor_message",{search_term:text.slice(0,100)});
    var slots={state:st.slots.state,level:st.slots.level,want:(st.slots.want&&st.slots.want!=="help")?st.slots.want:null};
    fetch(ENDPOINT,{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({messages:st.messages.slice(-12),slots:slots,site:{profile:"electrician",brand:SITE.brand||"",fulfillment:SITE.fulfillment||"",phone:PHONE,catalog:new URL(S.BASE+"shared/catalog.js",location.href).href}})})
      .then(function(r){return r.json();})
      .then(function(d){
        clearTimeout(slow); if(dots) dots.remove();
        var reply=d.reply||"Sorry, I didn't get that. Can you say it another way?", prods=d.products||[], sugg=d.suggestions||[];
        var ns=d.slots||{}; if(ns.state) st.slots.state=ns.state; if(ns.level) st.slots.level=ns.level; if(ns.want) st.slots.want=ns.want;
        /* if something is still missing and no products were shown, offer the big buttons for it */
        var step=prods.length?(st.slots.state&&st.slots.level?"done":null):(st.slots.state&&st.slots.level?null:needStep(st.slots));
        st.messages.push({role:"assistant",content:reply+(prods.length?" [Shown: "+prods.map(function(p){return p.state?p.state+" "+p.level+" "+p.tierName:p.tierName;}).join("; ")+"]":"")});
        st.view.push({type:"bot",text:reply,products:prods,suggestions:sugg,step:step}); save();
        if(prods.length) track("ai_advisor_recommend",{products:prods.map(function(p){return p.id;}).join(","),mode:"chat"});
        return new Promise(function(r){S.ensureCatalog(r);}).then(function(){ var w=Date.now()-t0; return deliver(reply,prods,sugg,null,w); }).then(function(){ if(step) showPicker(step); });
      })
      .catch(function(){clearTimeout(slow); if(dots) dots.remove(); bubble("bot","Sorry, I couldn't connect just now. You can still tap the buttons"+(PHONE?", or call us at "+PHONE:"")+".",true); var s=needStep(st.slots); if(s!=="done") showPicker(s);})
      .then(function(){setBusy(false);});
  }

  function chatMode(on,prefill){
    panel.hidden=!on; form.hidden=on; res.hidden=on; if(hint) hint.hidden=on;
    box.classList.toggle("ai-on",on);
    if(on){ S.ensureCatalog(function(){ render(!prefill); if(prefill) send(prefill); }); track("ai_advisor_open",{}); }
    else setTimeout(function(){S.q.focus();},20);
  }

  /* typing a state name in the "Type your state" box */
  panel.addEventListener("input",function(e){
    if(!e.target.classList.contains("ai-stin")) return;
    var out=e.target.closest(".ai-states").querySelector(".ai-stmatch");
    var m=S.matchStates?S.matchStates(e.target.value,6):[];
    out.innerHTML=m.map(stateBtn).join("")||(e.target.value.trim().length>1?'<p class="ai-nomatch">Keep typing…</p>':"");
    scroll();
  });
  panel.addEventListener("keydown",function(e){
    if(e.key==="Enter"&&e.target.classList.contains("ai-stin")){ e.preventDefault(); var b=e.target.closest(".ai-states").querySelector(".ai-stmatch .ai-stbtn"); if(b) b.click(); }
  });
  aForm.addEventListener("submit",function(e){e.preventDefault();send(input.value);});
  box.addEventListener("click",function(e){
    var ask=e.target.closest("[data-ai-ask]"); if(ask){e.preventDefault();var t=ask.getAttribute("data-ai-ask");S.q.value="";chatMode(true,t);return;}
    if(e.target.closest("[data-ai-back]")){chatMode(false);return;}
    if(e.target.closest("[data-ai-reset]")){if(greetRun){greetRun.stop=true;greetRun=null;} st=fresh();save();render(true);return;}
    var pick=e.target.closest("[data-pick]"); if(pick){ var kind=pick.closest("[data-kind]").getAttribute("data-kind"); choose(kind,pick.getAttribute("data-pick"),pick.getAttribute("data-label")); return; }
    var chip=e.target.closest(".ai-chip"); if(chip){send(chip.textContent);}
  });
  /* opening search goes straight to Max. "Search instead" switches to the regular instant search. */
  var ov=document.getElementById("search");
  new MutationObserver(function(){ if(!ov.hidden&&panel.hidden&&!ov.dataset.aiSkip) chatMode(true); }).observe(ov,{attributes:true,attributeFilter:["hidden"]});
  if(!ov.hidden) chatMode(true);
  /* a question typed into the search box (several words, or ends with ?) goes to Max on Enter */
  form.addEventListener("submit",function(e){
    var t=S.q.value.trim();
    if(/\?$/.test(t)||t.split(/\s+/).length>=5){e.preventDefault();e.stopImmediatePropagation();S.q.value="";chatMode(true,t);}
  },true);
  if(!S.q.value.trim()) res.innerHTML=window.AI_ROW("");
})();
