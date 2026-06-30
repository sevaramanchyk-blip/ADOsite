(function(){
  const tabs=document.querySelectorAll('.tab-btn');
  const panels=document.querySelectorAll('.tab-panel');
  const runBtn=document.getElementById('run-test');
  const results=document.getElementById('results');
  const btnText=runBtn.querySelector('.btn-text');
  const btnLoader=runBtn.querySelector('.btn-loader');

  tabs.forEach(tab=>{
    tab.addEventListener('click',()=>{
      tabs.forEach(t=>t.classList.remove('active'));
      panels.forEach(p=>p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('panel-'+tab.dataset.tab).classList.add('active');
    });
  });

  document.querySelectorAll('.custom-select').forEach(sel=>{
    const selected=sel.querySelector('.select-selected');
    const options=sel.querySelector('.select-options');
    const hiddenInput=sel.nextElementSibling;

    selected.addEventListener('click',e=>{
      e.stopPropagation();
      document.querySelectorAll('.custom-select.open').forEach(s=>{
        if(s!==sel)s.classList.remove('open');
      });
      sel.classList.toggle('open');
    });

    sel.querySelectorAll('.select-option').forEach(opt=>{
      opt.addEventListener('click',e=>{
        e.stopPropagation();
        selected.textContent=opt.textContent;
        hiddenInput.value=opt.dataset.value;
        sel.dataset.value=opt.dataset.value;
        sel.querySelectorAll('.select-option').forEach(o=>o.classList.remove('selected'));
        opt.classList.add('selected');
        sel.classList.remove('open');
      });
    });
  });

  document.addEventListener('click',()=>{
    document.querySelectorAll('.custom-select.open').forEach(s=>s.classList.remove('open'));
  });

  runBtn.addEventListener('click',()=>{
    runBtn.classList.add('loading');
    btnText.style.display='none';
    btnLoader.style.display='inline';
    results.style.display='none';

    const activeTab=document.querySelector('.tab-btn.active').dataset.tab;
    let params={};

    if(activeTab==='api'){
      params={
        url:document.getElementById('api-url').value,
        method:document.getElementById('api-method').value,
        expected_status:document.getElementById('api-status').value,
        timeout:document.getElementById('api-timeout').value,
        redirects:document.getElementById('api-redirects').value,
        headers:document.getElementById('api-headers').value,
        body:document.getElementById('api-body').value
      };
    }else if(activeTab==='ui'){
      params={
        url:document.getElementById('ui-url').value,
        selector:document.getElementById('ui-selector').value,
        assertion:document.getElementById('ui-assertion').value,
        timeout:document.getElementById('ui-timeout').value,
        browser:document.getElementById('ui-browser').value,
        screenshot:document.getElementById('ui-screenshot').value,
        custom_selector:document.getElementById('ui-custom-selector').value
      };
    }else{
      params={
        url:document.getElementById('load-url').value,
        users:document.getElementById('load-users').value,
        spawn_rate:document.getElementById('load-rate').value,
        duration:document.getElementById('load-duration').value,
        rampup:document.getElementById('load-rampup').value,
        type:document.getElementById('load-type').value,
        think:document.getElementById('load-think').value,
        threshold:document.getElementById('load-threshold').value
      };
    }

    setTimeout(()=>{
      const data=generateResults(activeTab,params);
      renderResults(data);
      runBtn.classList.remove('loading');
      btnText.style.display='inline';
      btnLoader.style.display='none';
    },1500+Math.random()*2000);
  });

  function generateResults(type,params){
    const tests=generateMockTests(type,params);
    const dur=(Math.random()*5+1).toFixed(1);
    return{
      passed:tests.filter(t=>t.status==='passed').length,
      failed:tests.filter(t=>t.status==='failed').length,
      duration:dur,
      tests:tests
    };
  }

  function generateMockTests(type,params){
    const tests=[];
    if(type==='api'){
      const method=params.method||'GET';
      const url=params.url||'https://ado-shop.com/';
      const status=params.expected_status||'200';
      const timeout=params.timeout||'10';
      tests.push({name:`${method} ${url} → ${status}`,status:'passed',duration:'0.23s'});
      tests.push({name:`Response Time < ${timeout}s`,status:'passed',duration:'0.45s'});
      tests.push({name:'Content-Type is text/html',status:'passed',duration:'0.12s'});
      tests.push({name:'Response Body Not Empty',status:'passed',duration:'0.08s'});
      tests.push({name:'SSL Certificate Valid',status:'passed',duration:'0.31s'});
      tests.push({name:'Server Header Present',status:Math.random()>.7?'failed':'passed',duration:'0.19s'});
      tests.push({name:'CORS Headers Check',status:'passed',duration:'0.15s'});
      tests.push({name:'Cache-Control Present',status:'passed',duration:'0.11s'});
      tests.push({name:'X-Content-Type-Options',status:'passed',duration:'0.09s'});
      if(method==='POST'||method==='PUT'||method==='PATCH'){
        tests.push({name:`${method} Request Body Valid`,status:'passed',duration:'0.14s'});
        tests.push({name:'Content-Type JSON',status:'passed',duration:'0.07s'});
      }
      if(params.redirects==='false'){
        tests.push({name:'No Redirect (3xx)',status:'passed',duration:'0.18s'});
      }
      tests.push({name:'DNS Resolution',status:'passed',duration:'0.32s'});
      tests.push({name:'TCP Connection',status:'passed',duration:'0.05s'});
    }else if(type==='ui'){
      const selector=params.selector||'header';
      const assertion=params.assertion||'visible';
      const browser=params.browser||'chrome';
      const timeout=params.timeout||'10';
      tests.push({name:`[${browser}] ${selector} ${assertion}`,status:'passed',duration:'1.2s'});
      tests.push({name:'Page Load Complete',status:'passed',duration:'0.8s'});
      tests.push({name:'No JS Errors',status:Math.random()>.8?'failed':'passed',duration:'0.9s'});
      tests.push({name:'CSS Animations Loaded',status:'passed',duration:'1.1s'});
      tests.push({name:`Wait ≤ ${timeout}s`,status:'passed',duration:'0.6s'});
      tests.push({name:'Images Loaded',status:'passed',duration:'1.5s'});
      tests.push({name:'No Console Errors',status:'passed',duration:'0.4s'});
      if(params.screenshot==='true'){
        tests.push({name:'Screenshot Captured',status:'passed',duration:'0.3s'});
      }
      if(params.custom_selector){
        tests.push({name:`Custom: ${params.custom_selector}`,status:Math.random()>.6?'failed':'passed',duration:'1.0s'});
      }
      tests.push({name:'Responsive Check',status:'passed',duration:'2.0s'});
      tests.push({name:'Accessibility Basics',status:Math.random()>.5?'failed':'passed',duration:'1.8s'});
    }else{
      const users=parseInt(params.users)||10;
      const duration=params.duration||'30';
      const type_label=params.type||'static';
      const threshold=params.threshold||'2000';
      tests.push({name:`${type_label} endpoint stress`,status:'passed',duration:'0.5s'});
      tests.push({name:`${users} concurrent users`,status:'passed',duration:(Math.random()*3+1).toFixed(1)+'s'});
      tests.push({name:`Duration: ${duration}s`,status:'passed',duration:duration+'s'});
      tests.push({name:`Response < ${threshold}ms`,status:Math.random()>.7?'failed':'passed',duration:'0.3s'});
      tests.push({name:'No Timeouts',status:'passed',duration:'0.2s'});
      tests.push({name:'Error Rate < 1%',status:'passed',duration:'0.4s'});
      tests.push({name:'Throughput RPS',status:'passed',duration:'0.6s'});
      tests.push({name:'P95 Latency',status:'passed',duration:'0.8s'});
      tests.push({name:'P99 Latency',status:'passed',duration:'0.9s'});
      tests.push({name:'CPU Usage OK',status:'passed',duration:'0.1s'});
      tests.push({name:'Memory Usage OK',status:'passed',duration:'0.1s'});
      tests.push({name:'Network I/O',status:'passed',duration:'0.2s'});
    }
    return tests;
  }

  function renderResults(data){
    results.style.display='block';
    results.querySelector('.results-passed').textContent=data.passed+' Passed';
    results.querySelector('.results-failed').textContent=data.failed+' Failed';
    results.querySelector('.results-time').textContent=data.duration+'s';

    const list=results.querySelector('.results-list');
    list.innerHTML='';
    data.tests.forEach(t=>{
      const item=document.createElement('div');
      item.className='result-item '+(t.status==='passed'?'pass':'fail');
      item.innerHTML=`
        <span class="result-status">${t.status}</span>
        <span class="result-name">${t.name}</span>
        <span class="result-duration">${t.duration}</span>
      `;
      list.appendChild(item);
    });
  }
})();
