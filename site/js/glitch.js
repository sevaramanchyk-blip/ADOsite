(function(){
  function triggerGlitch(){
    document.body.classList.add('glitch-active');
    setTimeout(()=>document.body.classList.remove('glitch-active'),200+Math.random()*300);
  }

  let lastGlitchTime=0;
  const GLITCH_COOLDOWN=400;

  function scheduleGlitch(){
    const delay=3000+Math.random()*7000;
    setTimeout(()=>{
      triggerGlitch();
      scheduleGlitch();
    },delay);
  }

  function audioGlitch(){
    if(!window.audioReactive||!window.audioReactive.active){
      requestAnimationFrame(audioGlitch);
      return;
    }

    const now=Date.now();
    const vol=window.audioReactive.volume;
    const bass=window.audioReactive.bass;

    if(bass>.65&&vol>.4&&now-lastGlitchTime>GLITCH_COOLDOWN){
      triggerGlitch();
      lastGlitchTime=now;
    }

    if(bass>.85&&now-lastGlitchTime>GLITCH_COOLDOWN/2){
      triggerGlitch();
      lastGlitchTime=now;
    }

    requestAnimationFrame(audioGlitch);
  }

  scheduleGlitch();
  requestAnimationFrame(audioGlitch);
})();
