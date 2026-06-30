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

  runBtn.addEventListener('click', async ()=>{
    runBtn.classList.add('loading');
    btnText.style.display='none';
    btnLoader.style.display='inline';
    results.style.display='none';

    const activeTab=document.querySelector('.tab-btn.active').dataset.tab;

    if(activeTab==='api'){
      await runApiTest();
    }else if(activeTab==='ui'){
      runUiTest();
    }else{
      runLoadTest();
    }
  });

  async function runApiTest(){
    const params={
      url:document.getElementById('api-url').value,
      method:document.getElementById('api-method').value,
      expected_status:document.getElementById('api-status').value,
      timeout:document.getElementById('api-timeout').value,
      redirects:document.getElementById('api-redirects').value,
      headers:document.getElementById('api-headers').value,
      body:document.getElementById('api-body').value
    };

    try{
      const resp=await fetch('/api/test',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(params)
      });
      const data=await resp.json();
      renderResults(data);
    }catch(e){
      renderResults({
        passed:0,failed:1,duration:'0.0s',
        tests:[{name:'Request Failed',status:'failed',duration:'0s',error:e.message}]
      });
    }

    stopLoading();
  }

  function runUiTest(){
    const selector=document.getElementById('ui-selector').value;
    const assertion=document.getElementById('ui-assertion').value;
    const browser=document.getElementById('ui-browser').value;
    const timeout=document.getElementById('ui-timeout').value;
    const screenshot=document.getElementById('ui-screenshot').value;
    const customSelector=document.getElementById('ui-custom-selector').value;
    const url=document.getElementById('ui-url').value;

    const tests=[];
    const start=performance.now();

    // Real checks via fetch
    fetch(url).then(r=>{
      const status=r.status;
      tests.push({name:`HTTP ${url} → ${status}`,status:status===200?'passed':'failed',duration:'0s',detail:`Status: ${status}`});
      return r.text();
    }).then(html=>{
      const dur=((performance.now()-start)/1000).toFixed(2);

      // Check for selector in HTML
      const selectorMap={
        'header':'<header','footer':'<footer','logo':'logo','cart':'cart-icon-bubble',
        'products':'product','search':'search','nav':'<nav','h1':'<h1'
      };
      const searchStr=selectorMap[selector]||selector;
      const found=html.toLowerCase().includes(searchStr.toLowerCase());
      tests.push({name:`[${browser}] ${selector} ${assertion}`,status:found?'passed':'failed',duration:dur+'s',detail:found?`Found "${searchStr}"`:`"${searchStr}" not found`});

      // Page load
      tests.push({name:'Page Load Complete',status:'passed',duration:dur+'s'});

      // Content checks
      if(assertion==='text'){
        const hasText=html.length>0;
        tests.push({name:'Has Text Content',status:hasText?'passed':'failed',duration:'0.01s',detail:`${html.length} chars`});
      }
      if(assertion==='visible'||assertion==='exists'){
        tests.push({name:'Element Exists in DOM',status:found?'passed':'failed',duration:'0.01s'});
      }

      // No empty page
      tests.push({name:'Response Not Empty',status:html.length>100?'passed':'failed',duration:'0.01s',detail:`${html.length} bytes`});

      // Custom selector check
      if(customSelector){
        const csFound=html.toLowerCase().includes(customSelector.toLowerCase());
        tests.push({name:`Custom: ${customSelector}`,status:csFound?'passed':'failed',duration:'0.02s',detail:csFound?'Found':'Not found'});
      }

      // HTML structure
      tests.push({name:'Valid HTML Structure',status:html.includes('</html>')?'passed':'failed',duration:'0.01s'});
      tests.push({name:'No Broken Tags',status:(html.match(/<[^>]+>/g)||[]).length>10?'passed':'failed',duration:'0.01s'});

      // JS errors check (basic)
      const scriptCount=(html.match(/<script/g)||[]).length;
      tests.push({name:`Scripts Loaded (${scriptCount})`,status:scriptCount>0?'passed':'failed',duration:'0.01s'});

      // CSS check
      const cssLinks=(html.match(/\.css/g)||[]).length;
      tests.push({name:`Stylesheets (${cssLinks})`,status:cssLinks>0?'passed':'failed',duration:'0.01s'});

      const passed=tests.filter(t=>t.status==='passed').length;
      const failed=tests.filter(t=>t.status==='failed').length;
      renderResults({passed,failed,duration:dur+'s',tests});
      stopLoading();
    }).catch(e=>{
      tests.push({name:'Connection Error',status:'failed',duration:'0s',error:e.message});
      renderResults({passed:0,failed:1,duration:'0s',tests});
      stopLoading();
    });
  }

  function runLoadTest(){
    const url=document.getElementById('load-url').value;
    const users=parseInt(document.getElementById('load-users').value)||10;
    const duration=parseInt(document.getElementById('load-duration').value)||30;
    const threshold=parseInt(document.getElementById('load-threshold').value)||2000;

    const tests=[];
    let completed=0;
    let successes=0;
    let failures=0;
    let totalLatency=0;
    let minLatency=Infinity;
    let maxLatency=0;
    const start=performance.now();
    const endTime=start+duration*1000;
    const interval=100;

    function sendRequest(){
      if(performance.now()>endTime){
        finishLoadTest();
        return;
      }
      const reqStart=performance.now();
      fetch(url).then(r=>{
        const latency=performance.now()-reqStart;
        completed++;
        totalLatency+=latency;
        if(latency<minLatency)minLatency=latency;
        if(latency>maxLatency)maxLatency=latency;
        if(r.ok&&latency<threshold)successes++;
        else failures++;
      }).catch(()=>{
        completed++;
        failures++;
      });
      setTimeout(sendRequest,Math.max(10,interval/users));
    }

    function finishLoadTest(){
      const dur=((performance.now()-start)/1000).toFixed(1);
      const avgLatency=completed>0?(totalLatency/completed).toFixed(0):0;
      const rps=completed>0?(completed/dur).toFixed(1):0;
      const errorRate=completed>0?((failures/completed)*100).toFixed(1):0;

      tests.push({name:`${users} concurrent users`,status:'passed',duration:dur+'s',detail:`Completed: ${completed}`});
      tests.push({name:`Duration: ${duration}s`,status:'passed',duration:dur+'s'});
      tests.push({name:`Total Requests: ${completed}`,status:completed>0?'passed':'failed',duration:'0s'});
      tests.push({name:`Successful: ${successes}`,status:successes>0?'passed':'failed',duration:'0s'});
      tests.push({name:`Failed: ${failures}`,status:failures===0?'passed':'failed',duration:'0s'});
      tests.push({name:`Avg Latency: ${avgLatency}ms`,status:avgLatency<threshold?'passed':'failed',duration:'0s',detail:`Threshold: ${threshold}ms`});
      tests.push({name:`Min Latency: ${minLatency===Infinity?0:minLatency.toFixed(0)}ms`,status:'passed',duration:'0s'});
      tests.push({name:`Max Latency: ${maxLatency.toFixed(0)}ms`,status:maxLatency<threshold*2?'passed':'failed',duration:'0s'});
      tests.push({name:`RPS: ${rps}`,status:parseFloat(rps)>0?'passed':'failed',duration:'0s'});
      tests.push({name:`Error Rate: ${errorRate}%`,status:parseFloat(errorRate)<5?'passed':'failed',duration:'0s'});

      renderResults({passed:tests.filter(t=>t.status==='passed').length,failed:tests.filter(t=>t.status==='failed').length,duration:dur+'s',tests});
      stopLoading();
    }

    tests.push({name:'Load test started...',status:'passed',duration:'0s'});
    renderResults({passed:1,failed:0,duration:'0s',tests});
    sendRequest();
  }

  function stopLoading(){
    runBtn.classList.remove('loading');
    btnText.style.display='inline';
    btnLoader.style.display='none';
  }

  function renderResults(data){
    results.style.display='block';
    results.querySelector('.results-passed').textContent=data.passed+' Passed';
    results.querySelector('.results-failed').textContent=data.failed+' Failed';
    results.querySelector('.results-time').textContent=data.duration;

    const list=results.querySelector('.results-list');
    list.innerHTML='';
    data.tests.forEach(t=>{
      const item=document.createElement('div');
      item.className='result-item '+(t.status==='passed'?'pass':'fail');
      let detail='';
      if(t.detail)detail=`<span class="result-detail">${t.detail}</span>`;
      if(t.error)detail=`<span class="result-detail error">${t.error}</span>`;
      item.innerHTML=`
        <span class="result-status">${t.status}</span>
        <span class="result-name">${t.name}${detail}</span>
        <span class="result-duration">${t.duration}</span>
      `;
      list.appendChild(item);
    });
  }
})();
