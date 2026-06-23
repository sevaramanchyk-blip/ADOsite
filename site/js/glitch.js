(function(){
  function triggerGlitch(){
    document.body.classList.add('glitch-active');
    setTimeout(()=>document.body.classList.remove('glitch-active'),200+Math.random()*300);
  }

  function scheduleGlitch(){
    const delay=3000+Math.random()*7000;
    setTimeout(()=>{
      triggerGlitch();
      scheduleGlitch();
    },delay);
  }

  scheduleGlitch();
})();
