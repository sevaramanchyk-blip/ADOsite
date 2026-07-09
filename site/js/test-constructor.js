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
      await runUiTest();
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

    let data;
    try{
      const resp=await fetch('/api/test',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(params)
      });
      data=await resp.json();
    }catch(e){
      data={
        passed:0,failed:1,duration:'0s',
        tests:[{name:'Request Failed',status:'failed',duration:'0s',error:e.message}]
      };
    }

    if(!data)data={passed:0,failed:0,duration:'0s',tests:[]};
    if(!data.tests)data.tests=[];

    renderResults(data);
    stopLoading();
  }

  async function runUiTest(){
    const selector=document.getElementById('ui-selector').value;
    const assertion=document.getElementById('ui-assertion').value;
    const browser=document.getElementById('ui-browser').value;
    const timeout=document.getElementById('ui-timeout').value;
    const screenshot=document.getElementById('ui-screenshot').value;
    const customSelector=document.getElementById('ui-custom-selector').value;
    const url=document.getElementById('ui-url').value;

    const selectorTestMap={
      'header':'elements',
      'footer':'elements',
      'logo':'elements',
      'cart':'business',
      'products':'adoshop',
      'search':'elements',
      'nav':'elements',
      'h1':'spell',
    };

    const testType=selectorTestMap[selector]||'ui';

    let data;
    try{
      const resp=await fetch('/api/run-tests',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          type:testType,
          selector:selector,
          assertion:assertion,
          url:url
        })
      });
      data=await resp.json();
    }catch(e){
      data={
        passed:0,failed:1,duration:'0s',
        tests:[{name:'Connection Error',status:'failed',duration:'0s',error:e.message}],
        raw_output:''
      };
    }

    if(!data)data={passed:0,failed:0,duration:'0s',tests:[],raw_output:''};
    if(!data.tests)data.tests=[];
    if(typeof data.passed!=='number')data.passed=0;
    if(typeof data.failed!=='number')data.failed=0;

    if(data.tests.length===0&&data.raw_output){
      const lines=data.raw_output.split('\n');
      const pytestTests=[];
      let p=0,f=0;

      lines.forEach(line=>{
        const trimmed=line.trim();
        // Формат 2: "FAILED tests/file.py::test_name" на отдельной строке
        if(trimmed.startsWith('FAILED')&&trimmed.includes('::')){
          const m=trimmed.match(/FAILED\s+(\S+::\S+)/);
          if(m){
            let name=m[1].split('::').pop();
            pytestTests.push({name:name,status:'failed',duration:'0s',error:trimmed.substring(0,120)});
            f++;
          }
        // Формат 1: "tests/file.py::test_name PASSED [10%]"
        }else if(trimmed.includes('PASSED')&&trimmed.includes('::')){
          const m=trimmed.match(/(\S+::\S+)\s+PASSED/);
          if(m){
            let name=m[1].split('::').pop();
            pytestTests.push({name:name,status:'passed',duration:'0s'});
            p++;
          }
        }else if(trimmed.includes('FAILED')&&trimmed.includes('::')){
          const m=trimmed.match(/(\S+::\S+)\s+FAILED/);
          if(m){
            let name=m[1].split('::').pop();
            pytestTests.push({name:name,status:'failed',duration:'0s',error:trimmed.substring(0,120)});
            f++;
          }
        }
      });

      if(pytestTests.length>0){
        data.tests=pytestTests;
        data.passed=p;
        data.failed=f;
      }else{
        const lastLines=lines.slice(-5).join(' | ');
        data.tests=[{name:'Test output',status:data.failed>0?'failed':'passed',duration:data.duration||'0s',error:lastLines}];
      }
    }

    if(data.tests.length===0){
      data.tests=[{name:'No results from server',status:'failed',duration:'0s',error:'Empty response from pytest'}];
    }

    data.tests.forEach(t=>{
      if(!t.detail)t.detail=browser+' | '+assertion;
    });

    renderResults(data);
    stopLoading();
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
    if(!data){
      data={passed:0,failed:1,duration:'0s',tests:[{name:'No response from server',status:'failed',duration:'0s',error:'Empty response'}]};
    }
    results.style.display='block';
    results.querySelector('.results-passed').textContent=(data.passed||0)+' Passed';
    results.querySelector('.results-failed').textContent=(data.failed||0)+' Failed';
    results.querySelector('.results-time').textContent=data.duration||'0s';

    const list=results.querySelector('.results-list');
    list.innerHTML='';
    const tests=data.tests||[];
    tests.forEach(t=>{
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

    if(tests.length===0){
      list.innerHTML='<div class="result-item fail"><span class="result-status">failed</span><span class="result-name">No test results returned</span><span class="result-duration">0s</span></div>';
    }
  }
})();
