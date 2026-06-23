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
        expected_status:document.getElementById('api-status').value
      };
    }else if(activeTab==='ui'){
      params={
        url:document.getElementById('ui-url').value,
        selector:document.getElementById('ui-selector').value,
        assertion:document.getElementById('ui-assertion').value
      };
    }else{
      params={
        users:document.getElementById('load-users').value,
        spawn_rate:document.getElementById('load-rate').value,
        duration:document.getElementById('load-duration').value
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
    const tests=generateMockTests(type);
    const dur=(Math.random()*5+1).toFixed(1);
    return{
      passed:tests.filter(t=>t.status==='passed').length,
      failed:tests.filter(t=>t.status==='failed').length,
      duration:dur,
      tests:tests
    };
  }

  function generateMockTests(type){
    const tests=[];
    if(type==='api'){
      tests.push({name:'GET / Status Code 200',status:'passed',duration:'0.23s'});
      tests.push({name:'GET / Response Time < 2s',status:'passed',duration:'0.45s'});
      tests.push({name:'GET / Content Contains Title',status:'passed',duration:'0.12s'});
      tests.push({name:'GET /collections/shinzou Returns 200',status:'passed',duration:'0.31s'});
      tests.push({name:'POST /cart Invalid Method',status:'passed',duration:'0.08s'});
      tests.push({name:'GET /nonexistent 404',status:Math.random()>.7?'failed':'passed',duration:'0.15s'});
      tests.push({name:'GET /products.json Valid JSON',status:'passed',duration:'0.67s'});
      tests.push({name:'GET / Header Security Check',status:'passed',duration:'0.19s'});
    }else if(type==='ui'){
      tests.push({name:'Header Is Visible',status:'passed',duration:'1.2s'});
      tests.push({name:'Logo Image Loaded',status:'passed',duration:'0.8s'});
      tests.push({name:'Footer Contains Copyright',status:'passed',duration:'0.9s'});
      tests.push({name:'Cart Button Clickable',status:'passed',duration:'1.1s'});
      tests.push({name:'Products Grid Displayed',status:'passed',duration:'1.5s'});
      tests.push({name:'Search Modal Opens',status:Math.random()>.8?'failed':'passed',duration:'2.0s'});
    }else{
      for(let i=1;i<=10;i++){
        tests.push({name:`User ${i} Session`,status:'passed',duration:(Math.random()*3+1).toFixed(1)+'s'});
      }
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
