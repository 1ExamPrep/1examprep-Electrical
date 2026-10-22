/* AI exam advisor inside the site search.
   Loaded by search.js only when "aiFinderUrl" is set in site-config.json.
   The chat runs on the Cloudflare Worker from the ai-product-finder kit; products are always real ones from
   this site's own catalog.js, and Buy now goes to the same checkout links as the rest of the site. */
(function(){
  "use strict";
  var S=window.SRCH, SITE=window.SITE||{}; if(!S||!SITE.aiFinder) return;
  var ENDPOINT=SITE.aiFinder.replace(/\/+$/,"")+(/\/chat$/.test(SITE.aiFinder)?"":"/chat");
  var STORE=SITE.storeUrl||"https://1examprep.com", KEY="ai_advisor_v1";
  var GREETING="Hi! Tell me which state you're testing in and whether it's the journeyman or master exam, and I'll point you to the right prep.";
  var STARTERS=["Texas master electrician","Cheapest way to study","I want practice tests","Code book with tabs"];

  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function money(v){return "$"+Number(v).toFixed(2);}
  function cartUrl(id){return STORE+"/cart/"+id+":1"+(SITE.cartTag||"");}
  function load(){try{return JSON.parse(sessionStorage.getItem(KEY));}catch(e){return null;}}
  function save(){try{sessionStorage.setItem(KEY,JSON.stringify(st));}catch(e){}}
  var st=load()||{messages:[],slots:{},view:[]}, busy=false;

  var box=document.querySelector("#search .srch-box"), form=box.querySelector(".srch-form"), res=box.querySelector(".srch-res"), hint=box.querySelector(".srch-hint");
  var ICON='<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 2l1.8 5.2L19 9l-5.2 1.8L12 16l-1.8-5.2L5 9l5.2-1.8L12 2zm7 12l.9 2.1L22 17l-2.1.9L19 20l-.9-2.1L16 17l2.1-.9L19 14zM5 15l.7 1.6L7.3 17l-1.6.7L5 19.3l-.7-1.6L2.7 17l1.6-.4L5 15z"/></svg>';

  /* entry point: a row at the top of the normal search results */
  window.AI_ROW=function(text){
    var t=(text||"").trim();
    return '<button type="button" class="srch-row ai-ask" data-ai-ask="'+esc(t)+'"><span class="ai-ico">'+ICON+'</span><span class="srch-t"><b>'+(t?'Ask the exam advisor: “'+esc(t.length>48?t.slice(0,48)+"…":t)+'”':"Not sure what to get? Ask the exam advisor")+'</b><small>Answers in plain English and picks the right package for you</small></span><span class="ai-go">Ask</span></button>';
  };

  var panel=document.createElement("div"); panel.className="ai"; panel.hidden=true;
  panel.innerHTML='<div class="ai-head"><span class="ai-ico">'+ICON+'</span><b>Exam advisor</b><span class="ai-sp"></span><button type="button" class="ai-link" data-ai-reset>Start over</button><button type="button" class="ai-link" data-ai-back>Back to search</button><button type="button" class="srch-x" data-sclose aria-label="Close">×</button></div>'+
    '<div class="ai-log" aria-live="polite"></div><div class="ai-chips"></div>'+
    '<form class="ai-form" autocomplete="off"><input class="ai-in" type="text" maxlength="400" placeholder="e.g. Florida journeyman, under $200" aria-label="Your message"><button class="ai-send" type="submit" aria-label="Send"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M3 11.5 21 3l-8.5 18-2.2-7.3L3 11.5Z" fill="currentColor"/></svg></button></form>'+
    '<p class="ai-foot">Recommendations come from our real catalog. Orders are fulfilled by '+esc(SITE.fulfillment||"1 Exam Prep")+'.</p>';
  box.appendChild(panel);
  var log=panel.querySelector(".ai-log"), chips=panel.querySelector(".ai-chips"), aForm=panel.querySelector(".ai-form"), input=panel.querySelector(".ai-in"), sendBtn=panel.querySelector(".ai-send");

  function bubble(role,text){var d=document.createElement("div");d.className="ai-msg "+role;d.textContent=text;log.appendChild(d);log.scrollTop=log.scrollHeight;return d;}
  function cards(products){
    if(!products||!products.length) return;
    var C=window.CATALOG||[], byId={}; C.forEach(function(p){byId[String(p.id)]=p;});
    var html=products.map(function(x,i){
      var p=byId[String(x.id)]; if(!p) return "";
      var v=(p.variants||[]).filter(function(v){return v.available!==false;})[0]||(p.variants||[])[0];
      return '<article class="ai-card'+(i===0?" top":"")+'" data-id="'+esc(p.id)+'"><img src="'+esc(p.image)+'" alt="'+esc(p.tierName)+'" loading="lazy" width="72" height="72">'+
        '<div>'+(i===0?'<span class="ai-badge">Best match</span>':"")+'<h3>'+esc(p.tierName)+'</h3><small>'+esc((p.state||"Any state")+" · "+p.level+" · "+p.year)+'</small>'+
        (x.why?'<p class="ai-why">'+esc(x.why)+'</p>':"")+
        '<div class="ai-row"><span class="ai-price">'+money(p.price)+'</span>'+(v?'<a class="btn btn-buy ai-btn" href="'+esc(cartUrl(v.id))+'" rel="noopener">Buy now</a>':"")+'<a class="ai-more" href="'+esc(S.pathFor(p))+'">What’s inside</a></div></div></article>';
    }).join("");
    if(!html) return;
    var w=document.createElement("div"); w.className="ai-cards"; w.innerHTML=html; log.appendChild(w); log.scrollTop=log.scrollHeight;
  }
  function render(){
    log.innerHTML=""; bubble("bot",GREETING);
    st.view.forEach(function(v){ if(v.type==="user") bubble("user",v.text); else { bubble("bot",v.text); cards(v.products); } });
    chips.innerHTML=st.messages.length?"":STARTERS.map(function(s){return '<button type="button" class="ai-chip">'+esc(s)+'</button>';}).join("");
  }
  function typing(){var d=bubble("bot","");d.innerHTML='<span class="ai-dots"><i></i><i></i><i></i></span>';return d;}
  function setBusy(b){busy=b;sendBtn.disabled=b;input.disabled=b;}
  function track(name,params){try{if(window.dash&&dash.track)dash.track(name,params||{});}catch(e){} try{if(window.gtag)gtag("event",name,params||{});}catch(e){}}

  function send(text){
    text=(text||"").trim(); if(!text||busy) return;
    chips.innerHTML="";
    st.messages.push({role:"user",content:text}); st.view.push({type:"user",text:text}); bubble("user",text);
    input.value=""; setBusy(true); var dots=typing();
    track("ai_advisor_message",{search_term:text.slice(0,100)});
    fetch(ENDPOINT,{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({messages:st.messages.slice(-10),slots:st.slots,site:{profile:"electrician",brand:SITE.brand||"",catalog:new URL(S.BASE+"shared/catalog.js",location.href).href}})})
      .then(function(r){return r.json();})
      .then(function(d){
        dots.remove();
        var reply=d.reply||"Sorry, something went wrong. Try again?", prods=d.products||[];
        st.slots=d.slots||st.slots;
        st.messages.push({role:"assistant",content:reply+(prods.length?" [Shown: "+prods.map(function(p){return p.state?p.state+" "+p.level+" "+p.tierName:p.tierName;}).join("; ")+"]":"")});
        st.view.push({type:"bot",text:reply,products:prods}); save();
        S.ensureCatalog(function(){ bubble("bot",reply); cards(prods); });
        if(prods.length) track("ai_advisor_recommend",{products:prods.map(function(p){return p.id;}).join(",")});
      })
      .catch(function(){dots.remove();bubble("bot","I couldn't connect just now. Try again, or use the regular search.");})
      .then(function(){setBusy(false);input.focus();});
  }

  function chatMode(on,prefill){
    panel.hidden=!on; form.hidden=on; res.hidden=on; if(hint) hint.hidden=on;
    box.classList.toggle("ai-on",on);
    if(on){ S.ensureCatalog(render); if(prefill) send(prefill); else setTimeout(function(){input.focus();},20); track("ai_advisor_open",{}); }
    else setTimeout(function(){S.q.focus();},20);
  }

  aForm.addEventListener("submit",function(e){e.preventDefault();send(input.value);});
  box.addEventListener("click",function(e){
    var ask=e.target.closest("[data-ai-ask]"); if(ask){e.preventDefault();var t=ask.getAttribute("data-ai-ask");S.q.value="";chatMode(true,t);return;}
    if(e.target.closest("[data-ai-back]")){chatMode(false);return;}
    if(e.target.closest("[data-ai-reset]")){st={messages:[],slots:{},view:[]};save();render();input.focus();return;}
    var chip=e.target.closest(".ai-chip"); if(chip){send(chip.textContent);}
  });
  /* each time the search opens it starts on normal search, with the advisor row on top */
  document.addEventListener("click",function(e){ if(e.target.closest("[data-sopen]")) chatMode(false); },true);
  /* a question typed into the search box (several words, or ends with ?) goes to the advisor on Enter */
  form.addEventListener("submit",function(e){
    var t=S.q.value.trim();
    if(/\?$/.test(t)||t.split(/\s+/).length>=5){e.preventDefault();e.stopImmediatePropagation();S.q.value="";chatMode(true,t);}
  },true);
  if(!S.q.value.trim()) res.innerHTML=window.AI_ROW("");
})();
