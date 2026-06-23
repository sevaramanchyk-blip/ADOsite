(function(){
  const nav=document.getElementById('main-nav');
  let lastScroll=0;

  window.addEventListener('scroll',()=>{
    const scrollY=window.scrollY;
    if(scrollY>100){
      nav.classList.add('scrolled');
    }else{
      nav.classList.remove('scrolled');
    }
    lastScroll=scrollY;
  });

  document.querySelectorAll('.song-item').forEach(el=>{
    el.addEventListener('mouseenter',()=>{
      document.body.classList.add('cursor-hover');
    });
    el.addEventListener('mouseleave',()=>{
      document.body.classList.remove('cursor-hover');
    });
  });
})();
