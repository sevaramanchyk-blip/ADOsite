(function(){
  let audioCtx,analyser,dataArray,timeData,source,micStream,systemStream;
  let active=false;
  let mode='mic';
  let sensitivity=1.5;
  let demoNodes=[];

  const root=document.documentElement;

  window.audioReactive={
    get bass(){return parseFloat(root.style.getPropertyValue('--audio-bass'))||0},
    get mid(){return parseFloat(root.style.getPropertyValue('--audio-mid'))||0},
    get high(){return parseFloat(root.style.getPropertyValue('--audio-high'))||0},
    get volume(){return parseFloat(root.style.getPropertyValue('--audio-volume'))||0},
    get active(){return active}
  };

  function init(){
    audioCtx=new(window.AudioContext||window.webkitAudioContext)();
    analyser=audioCtx.createAnalyser();
    analyser.fftSize=2048;
    analyser.smoothingTimeConstant=0.4;
    analyser.minDecibels=-90;
    analyser.maxDecibels=-10;
    dataArray=new Uint8Array(analyser.frequencyBinCount);
    timeData=new Uint8Array(analyser.frequencyBinCount);
  }

  function reinit(){
    if(audioCtx){
      audioCtx.close().catch(()=>{});
    }
    init();
  }

  async function startMic(){
    reinit();
    if(audioCtx.state==='suspended')await audioCtx.resume();
    micStream=await navigator.mediaDevices.getUserMedia({audio:true});
    source=audioCtx.createMediaStreamSource(micStream);
    source.connect(analyser);
    active=true;
    update();
  }

  async function startSystem(){
    reinit();
    if(audioCtx.state==='suspended')await audioCtx.resume();
    systemStream=await navigator.mediaDevices.getDisplayMedia({video:true,audio:{suppressLocalAudioPlayback:false}});
    if(!systemStream.getAudioTracks().length)throw new Error('No audio track — enable "Share audio" in dialog');
    systemStream.getAudioTracks().forEach(t=>{
      t.onended=()=>{if(active){stop();btn.textContent='Sound Off';btn.classList.remove('active');}};
    });
    source=audioCtx.createMediaStreamSource(systemStream);
    source.connect(analyser);
    active=true;
    update();
  }

  async function startDemo(){
    reinit();
    if(audioCtx.state==='suspended')await audioCtx.resume();

    demoNodes=[];
    const masterGain=audioCtx.createGain();
    masterGain.gain.value=0.5;
    masterGain.connect(analyser);
    analyser.connect(audioCtx.destination);

    const notes=[55,73.42,82.41,110,146.83,164.81,220,293.66,329.63,440];
    const oscs=[];
    for(let i=0;i<4;i++){
      const osc=audioCtx.createOscillator();
      const g=audioCtx.createGain();
      osc.type=['sine','triangle','sawtooth','square'][i];
      g.gain.value=0;
      osc.connect(g);
      g.connect(masterGain);
      osc.start();
      oscs.push({osc,gain:g});
      demoNodes.push(osc,g);
    }
    demoNodes.push(masterGain);

    let beatIdx=0;
    const bpm=128;
    const beatSec=60/bpm;

    function scheduleBeat(){
      if(!active)return;
      const now=audioCtx.currentTime;

      oscs.forEach((o,i)=>{
        const note=notes[(beatIdx+i*3)%notes.length];
        const oct=i<2?1:2;
        o.osc.frequency.setValueAtTime(note*oct,now);
        o.gain.gain.cancelScheduledValues(now);
        o.gain.gain.setValueAtTime(0,now);
        o.gain.gain.linearRampToValueAtTime(0.35,now+0.02);
        o.gain.gain.exponentialRampToValueAtTime(0.01,now+beatSec*0.8);
      });

      if(beatIdx%4===0){
        masterGain.gain.cancelScheduledValues(now);
        masterGain.gain.setValueAtTime(0.6,now);
        masterGain.gain.linearRampToValueAtTime(0.4,now+beatSec*2);
      }

      beatIdx++;
      setTimeout(scheduleBeat,beatSec*1000);
    }

    active=true;
    update();
    scheduleBeat();
  }

  function stop(){
    active=false;
    if(source){
      source.disconnect();
      source=null;
    }
    if(micStream){
      micStream.getTracks().forEach(t=>t.stop());
      micStream=null;
    }
    if(systemStream){
      systemStream.getTracks().forEach(t=>t.stop());
      systemStream=null;
    }
    demoNodes.forEach(n=>{
      try{n.stop&&n.stop()}catch(e){}
      try{n.disconnect&&n.disconnect()}catch(e){}
    });
    demoNodes=[];
    root.style.setProperty('--audio-bass','0');
    root.style.setProperty('--audio-mid','0');
    root.style.setProperty('--audio-high','0');
    root.style.setProperty('--audio-volume','0');
    root.style.setProperty('--screen-shake','0px');
    root.style.setProperty('--screen-flash','0');
  }

  function clamp(v){return Math.min(1,Math.max(0,v))}

  function update(){
    if(!active)return;
    analyser.getByteFrequencyData(dataArray);
    analyser.getByteTimeDomainData(timeData);

    const freqBins=dataArray.length;
    const bassEnd=Math.floor(freqBins*.05);
    const midEnd=Math.floor(freqBins*.25);
    const highEnd=Math.floor(freqBins*.6);

    let rms=0;
    for(let i=0;i<timeData.length;i++){
      const v=(timeData[i]-128)/128;
      rms+=v*v;
    }
    rms=Math.sqrt(rms/timeData.length);

    const rawBass=avgRange(dataArray,0,bassEnd)/255;
    const rawMid=avgRange(dataArray,bassEnd,midEnd)/255;
    const rawHigh=avgRange(dataArray,midEnd,highEnd)/255;
    const rawVol=Math.max(rms,avgRange(dataArray,0,highEnd)/255);

    const bass=clamp(rawBass*sensitivity);
    const mid=clamp(rawMid*sensitivity);
    const high=clamp(rawHigh*sensitivity);
    const volume=clamp(rawVol*sensitivity);

    root.style.setProperty('--audio-bass',bass.toFixed(3));
    root.style.setProperty('--audio-mid',mid.toFixed(3));
    root.style.setProperty('--audio-high',high.toFixed(3));
    root.style.setProperty('--audio-volume',volume.toFixed(3));

    if(bass>.7){
      const intensity=(bass-.7)*3.3;
      root.style.setProperty('--screen-shake',(intensity*3).toFixed(1)+'px');
      root.style.setProperty('--screen-flash',(.15*intensity).toFixed(3));
    }else{
      root.style.setProperty('--screen-shake','0px');
      root.style.setProperty('--screen-flash','0');
    }

    const allBarGroups=[];
    document.querySelectorAll('.audio-bars').forEach(g=>allBarGroups.push(g));
    ['hero-visualizer','player-visualizer','discography-visualizer','tests-visualizer'].forEach(cls=>{
      const el=document.querySelector('.'+cls);
      if(el)allBarGroups.push(el);
    });

    allBarGroups.forEach(group=>{
      const bars=group.querySelectorAll('.audio-bar');
      const len=bars.length;
      const isWide=group.classList.contains('audio-bars-left')||group.classList.contains('audio-bars-right');
      bars.forEach((bar,j)=>{
        const binStart=Math.floor((j/len)*dataArray.length*.6);
        const binEnd=Math.floor(((j+1)/len)*dataArray.length*.6);
        let sum=0,cnt=0;
        for(let k=binStart;k<binEnd&&k<dataArray.length;k++){sum+=dataArray[k];cnt++}
        const val=cnt?clamp(sum/cnt/255*sensitivity):0;
        const h=Math.max(3,val*60);
        if(isWide){
          bar.style.width=h.toFixed(0)+'px';
          bar.style.height='4px';
        }else{
          bar.style.height=h.toFixed(0)+'px';
          bar.style.width='';
        }
        bar.style.opacity=(0.3+val*0.7).toFixed(2);
        bar.style.boxShadow=val>.5?`0 0 ${val*12}px rgba(34,85,255,${val*.5})`:'none';
      });
    });

    requestAnimationFrame(update);
  }

  function avgRange(arr,start,end){
    let sum=0;
    for(let i=start;i<end&&i<arr.length;i++)sum+=arr[i];
    return sum/(end-start);
  }

  function showAudioMsg(text,dur){
    let el=document.getElementById('audio-msg');
    if(!el){
      el=document.createElement('div');
      el.id='audio-msg';
      el.style.cssText='position:fixed;top:80px;left:50%;transform:translateX(-50%);background:rgba(10,10,20,.92);color:#00ccff;border:1px solid #2255ff;padding:12px 24px;border-radius:8px;font:14px/1.4 Orbitron,sans-serif;z-index:99999;pointer-events:none;transition:opacity .4s;letter-spacing:1px;text-align:center;max-width:420px';
      document.body.appendChild(el);
    }
    el.textContent=text;
    el.style.opacity='1';
    clearTimeout(el._t);
    el._t=setTimeout(()=>{el.style.opacity='0'},dur||4000);
  }

  const btn=document.getElementById('audio-toggle');
  const slider=document.getElementById('audio-sensitivity');
  const sliderVal=document.getElementById('sensitivity-val');

  if(slider){
    slider.addEventListener('input',()=>{
      sensitivity=parseFloat(slider.value);
      if(sliderVal)sliderVal.textContent=Math.round(sensitivity*100)+'%';
    });
  }

  if(btn){
    btn.addEventListener('click',async()=>{
      if(active){
        stop();
        btn.textContent='Sound Off';
        btn.classList.remove('active');
      }else{
        btn.textContent='Starting...';
        btn.classList.add('active');
        try{
          if(mode==='mic'){
            await startMic();
          }else if(mode==='system'){
            showAudioMsg('In the dialog: check "Share tab audio"!',5000);
            await startSystem();
          }else{
            await startDemo();
          }
          btn.textContent='Sound On';
          if(mode==='system')showAudioMsg('Speaker mode — playing tab audio',3000);
        }catch(e){
          console.log('Audio start failed:',e);
          const msg=e.message.includes('No audio')
            ? 'No audio! Re-open dialog and CHECK "Share audio" checkbox'
            : 'Audio error: '+e.message;
          showAudioMsg(msg,5000);
          btn.textContent='Sound Off';
          btn.classList.remove('active');
        }
      }
    });
    btn.addEventListener('contextmenu',e=>{
      e.preventDefault();
      const modes=['mic','system','demo'];
      const idx=modes.indexOf(mode);
      mode=modes[(idx+1)%modes.length];
      const labels={mic:'🎤 Mic',system:'🔊 Speaker',demo:'🎵 Demo'};
      btn.title=labels[mode]+' | Right-click: cycle';
      showAudioMsg('Mode: '+labels[mode],2000);
      if(active){
        stop();
        if(mode==='mic')startMic();
        else if(mode==='system')startSystem();
        else startDemo();
      }
    });
  }
})();
