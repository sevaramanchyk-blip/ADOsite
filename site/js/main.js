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
})();
