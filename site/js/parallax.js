(function(){
  let ticking=false;
  window.addEventListener('scroll',()=>{
    if(!ticking){
      requestAnimationFrame(()=>{
        const scrollY=window.scrollY;
        document.querySelectorAll('[data-parallax]').forEach(el=>{
          const speed=parseFloat(el.getAttribute('data-parallax'));
          el.style.transform=`translateY(${scrollY*speed}px)`;
        });
        ticking=false;
      });
      ticking=true;
    }
  });
})();
