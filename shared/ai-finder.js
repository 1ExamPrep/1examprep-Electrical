/* AI exam advisor inside the site search.
   Loaded by search.js only when "aiFinderUrl" is set in site-config.json.
   The chat runs on the Cloudflare Worker from the ai-product-finder kit; products are always real ones from
   this site's own catalog.js, and Buy now goes to the same checkout links as the rest of the site. */
(function(){
  "use strict";
  var S=window.SRCH, SITE=window.SITE||{}; if(!S||!SITE.aiFinder) return;
  var ENDPOINT=SITE.aiFinder.replace(/\/+$/,"")+(/\/chat$/.test(SITE.aiFinder)?"":"/chat");
  var STORE=SITE.storeUrl||"https://1examprep.com", KEY="ai_advisor_v2", NAME="Max";
  var PHONE=SITE.phone||((document.querySelector('a[href^="tel:"]')||{}).textContent||"").trim();
  function hello(){var h=new Date().getHours();return h<5?"Hey there":h<12?"Good morning":h<18?"Good afternoon":"Good evening";}
  function greeting(){return hello()+"! I'm "+NAME+", the exam advisor here.\n\nWhat are you studying for? Tell me the state and whether it's journeyman or master, or just ask me anything about the exam.";}
  var STARTERS=["Texas master electrician","It's a retake","Is the exam open book?","What's the cheapest option?"];

  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function money(v){return "$"+Number(v).toFixed(2);}
  function cartUrl(id){return STORE+"/cart/"+id+":1"+(SITE.cartTag||"");}
  function load(){try{return JSON.parse(sessionStorage.getItem(KEY));}catch(e){return null;}}
  function save(){try{sessionStorage.setItem(KEY,JSON.stringify(st));}catch(e){}}
  function fresh(){return {messages:[],slots:{},view:[],greet:greeting()};}
  var st=load()||fresh(), busy=false;
  var reduceMotion=window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var box=document.querySelector("#search .srch-box"), form=box.querySelector(".srch-form"), res=box.querySelector(".srch-res"), hint=box.querySelector(".srch-hint");
  var ICON='<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 2l1.8 5.2L19 9l-5.2 1.8L12 16l-1.8-5.2L5 9l5.2-1.8L12 2zm7 12l.9 2.1L22 17l-2.1.9L19 20l-.9-2.1L16 17l2.1-.9L19 14zM5 15l.7 1.6L7.3 17l-1.6.7L5 19.3l-.7-1.6L2.7 17l1.6-.4L5 15z"/></svg>';
  var AVATAR='<span class="ai-av" aria-hidden="true">'+NAME.charAt(0)+'</span>';

  /* entry point: a row at the top of the normal search results */
  window.AI_ROW=function(text){
    var t=(text||"").trim();
    return '<button type="button" class="srch-row ai-ask" data-ai-ask="'+esc(t)+'">'+AVATAR+'<span class="srch-t"><b>'+(t?'Ask '+NAME+': “'+esc(t.length>48?t.slice(0,48)+"…":t)+'”':"Not sure what you need? Chat with "+NAME)+'</b><small>Our AI exam advisor. Tell it about your exam and it picks the right prep.</small></span><span class="ai-go">Chat</span></button>';
  };

  var panel=document.createElement("div"); panel.className="ai"; panel.hidden=true;
  panel.innerHTML='<div class="ai-head">'+AVATAR+'<div class="ai-who"><b>'+NAME+'</b><small><i class="ai-on-dot"></i><span class="ai-status">AI exam advisor · online</span></small></div><span class="ai-sp"></span><button type="button" class="ai-link" data-ai-reset>Start over</button><button type="button" class="ai-link" data-ai-back>Search products instead</button><button type="button" class="srch-x" data-sclose aria-label="Close">×</button></div>'+
    '<div class="ai-log" aria-live="polite"></div><div class="ai-chips"></div>'+
    '<form class="ai-form" autocomplete="off"><input class="ai-in" type="text" maxlength="400" placeholder="Message '+NAME+'…" aria-label="Your message"><button class="ai-send" type="submit" aria-label="Send"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M3 11.5 21 3l-8.5 18-2.2-7.3L3 11.5Z" fill="currentColor"/></svg></button></form>'+
    '<p class="ai-foot">'+NAME+' is an AI and only recommends products we actually sell.'+(PHONE?' Rather talk to a person? Call <a href="tel:'+esc(PHONE.replace(/[^0-9+]/g,""))+'">'+esc(PHONE)+'</a>.':'')+'</p>';
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
    /* only the last bot bubble in a run keeps its avatar, like a messaging app */
    var prev=r.previousElementSibling; if(role==="bot"&&prev&&prev.classList.contains("bot")) prev.classList.add("cont");
    scroll(); return d;
  }
  function cards(products){
    if(!products||!products.length) return;
    var C=window.CATALOG||[], byId={}; C.forEach(function(p){byId[String(p.id)]=p;});
    var html=products.map(function(x,i){
      var p=byId[String(x.id)]; if(!p) return "";
      var v=(p.variants||[]).filter(function(v){return v.available!==false;})[0]||(p.variants||[])[0];
      return '<article class="ai-card'+(i===0?" top":"")+'" data-id="'+esc(p.id)+'"><img src="'+esc(p.image)+'" alt="'+esc(p.tierName)+'" loading="lazy" width="72" height="72">'+
        '<div>'+(i===0?'<span class="ai-badge">'+NAME+'’s pick</span>':"")+'<h3>'+esc(p.tierName)+'</h3><small>'+esc((p.state||"Any state")+" · "+p.level+" · "+p.year)+'</small>'+
        (x.why?'<p class="ai-why">'+esc(x.why)+'</p>':"")+
        '<div class="ai-row"><span class="ai-price">'+money(p.price)+'</span>'+(v?'<a class="btn btn-buy ai-btn" href="'+esc(cartUrl(v.id))+'" rel="noopener">Buy now</a>':"")+'<a class="ai-more" href="'+esc(S.pathFor(p))+'">What’s inside</a></div></div></article>';
    }).join("");
    if(!html) return;
    var w=document.createElement("div"); w.className="ai-cards"+(reduceMotion?"":" pop"); w.innerHTML=html; log.appendChild(w); scroll();
  }
  function setChips(list){
    chips.innerHTML=(list||[]).map(function(s){return '<button type="button" class="ai-chip">'+esc(s)+'</button>';}).join("");
  }
  function render(animate){
    log.innerHTML="";
    if(animate&&!st.messages.length){ setChips([]); var g=greetRun={stop:false}; deliver(st.greet||greeting(),[],STARTERS,g).then(function(){if(greetRun===g)greetRun=null;}); return; }
    parts(st.greet||greeting()).forEach(function(t){bubble("bot",t);});
    st.view.forEach(function(v){ if(v.type==="user") bubble("user",v.text); else { parts(v.text).forEach(function(t){bubble("bot",t);}); cards(v.products); } });
    var last=st.view[st.view.length-1];
    setChips(!st.messages.length?STARTERS:(last&&last.type==="bot"?last.suggestions:[]));
  }
  function typing(){
    var r=row("bot"); r.classList.add("typing");
    var d=document.createElement("div"); d.className="ai-msg bot"; d.innerHTML='<span class="ai-dots"><i></i><i></i><i></i></span>'; r.appendChild(d);
    var prev=r.previousElementSibling; if(prev&&prev.classList.contains("bot")) prev.classList.add("cont");
    status.textContent=NAME+" is typing…"; scroll();
    return {remove:function(){ r.remove(); var p=log.lastElementChild; if(p&&p.classList.contains("bot")) p.classList.remove("cont"); status.textContent="AI exam advisor · online"; }};
  }
  function wait(ms){return new Promise(function(r){setTimeout(r,reduceMotion?0:ms);});}
  /* a short "typing" pause sized to the message, so replies arrive like a person sending them one by one */
  function pause(text){return Math.min(1700,450+String(text).length*16);}
  function setBusy(b){busy=b;sendBtn.disabled=b;input.disabled=b;}
  function track(name,params){try{if(window.dash&&dash.track)dash.track(name,params||{});}catch(e){} try{if(window.gtag)gtag("event",name,params||{});}catch(e){}}

  var greetRun=null;
  function deliver(reply,prods,sugg,ctl){
    var list=parts(reply), i=0, t=null;
    function next(){
      if(ctl&&ctl.stop){ if(t) t.remove(); return Promise.resolve(); }
      if(i>=list.length){ if(t) t.remove(); cards(prods); setChips(sugg); return Promise.resolve(); }
      var text=list[i++];
      if(!t) t=typing();
      return wait(i===1?Math.max(250,pause(text)-500):pause(text)).then(function(){ if(ctl&&ctl.stop){ if(t) t.remove(); return; } t.remove(); t=null; bubble("bot",text,true); if(i<list.length) t=typing(); return next(); });
    }
    return next();
  }

  function send(text){
    text=(text||"").trim(); if(!text||busy) return;
    if(greetRun){ greetRun.stop=true; greetRun=null; render(false); }   /* they started typing before the greeting finished */
    setChips([]);
    st.messages.push({role:"user",content:text}); st.view.push({type:"user",text:text}); bubble("user",text,true);
    input.value=""; setBusy(true);
    var dots=null, slow=setTimeout(function(){dots=typing();},350);
    track("ai_advisor_message",{search_term:text.slice(0,100)});
    fetch(ENDPOINT,{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({messages:st.messages.slice(-12),slots:st.slots,site:{profile:"electrician",brand:SITE.brand||"",fulfillment:SITE.fulfillment||"",phone:PHONE,catalog:new URL(S.BASE+"shared/catalog.js",location.href).href}})})
      .then(function(r){return r.json();})
      .then(function(d){
        clearTimeout(slow); if(dots) dots.remove();
        var reply=d.reply||"Sorry, I lost my train of thought there. Could you say that again?", prods=d.products||[], sugg=d.suggestions||[];
        st.slots=d.slots||st.slots;
        st.messages.push({role:"assistant",content:reply+(prods.length?" [Shown: "+prods.map(function(p){return p.state?p.state+" "+p.level+" "+p.tierName:p.tierName;}).join("; ")+"]":"")});
        st.view.push({type:"bot",text:reply,products:prods,suggestions:sugg}); save();
        if(prods.length) track("ai_advisor_recommend",{products:prods.map(function(p){return p.id;}).join(",")});
        return new Promise(function(r){S.ensureCatalog(r);}).then(function(){return deliver(reply,prods,sugg);});
      })
      .catch(function(){clearTimeout(slow); if(dots) dots.remove(); bubble("bot","Sorry, I couldn't connect just now. Try again in a moment"+(PHONE?", or give us a call at "+PHONE:"")+".",true);})
      .then(function(){setBusy(false);input.focus();});
  }

  function chatMode(on,prefill){
    panel.hidden=!on; form.hidden=on; res.hidden=on; if(hint) hint.hidden=on;
    box.classList.toggle("ai-on",on);
    if(on){ S.ensureCatalog(function(){render(!prefill);}); if(prefill) send(prefill); else setTimeout(function(){input.focus();},20); track("ai_advisor_open",{}); }
    else setTimeout(function(){S.q.focus();},20);
  }

  aForm.addEventListener("submit",function(e){e.preventDefault();send(input.value);});
  box.addEventListener("click",function(e){
    var ask=e.target.closest("[data-ai-ask]"); if(ask){e.preventDefault();var t=ask.getAttribute("data-ai-ask");S.q.value="";chatMode(true,t);return;}
    if(e.target.closest("[data-ai-back]")){chatMode(false);return;}
    if(e.target.closest("[data-ai-reset]")){st=fresh();save();render(true);input.focus();return;}
    var chip=e.target.closest(".ai-chip"); if(chip){send(chip.textContent);}
  });
  /* opening search (the icon, the "/" key or a link) goes straight into the chat with Max.
     "Back to search" switches to the regular instant search. */
  var ov=document.getElementById("search");
  new MutationObserver(function(){ if(!ov.hidden&&panel.hidden&&!ov.dataset.aiSkip) chatMode(true); }).observe(ov,{attributes:true,attributeFilter:["hidden"]});
  if(!ov.hidden) chatMode(true);
  /* a question typed into the search box (several words, or ends with ?) goes to the advisor on Enter */
  form.addEventListener("submit",function(e){
    var t=S.q.value.trim();
    if(/\?$/.test(t)||t.split(/\s+/).length>=5){e.preventDefault();e.stopImmediatePropagation();S.q.value="";chatMode(true,t);}
  },true);
  if(!S.q.value.trim()) res.innerHTML=window.AI_ROW("");
})();
