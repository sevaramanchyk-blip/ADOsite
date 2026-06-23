(function(){
  const sections=document.querySelectorAll('section');
  const observer=new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.style.opacity='1';
        entry.target.style.transform='translateY(0)';
      }
    });
  },{threshold:0.1});

  sections.forEach(s=>{
    s.style.opacity='0';
    s.style.transform='translateY(30px)';
    s.style.transition='opacity .8s ease,transform .8s ease';
    observer.observe(s);
  });

  document.querySelectorAll('.reveal').forEach(el=>{
    const obs=new IntersectionObserver((entries)=>{
      entries.forEach(e=>{
        if(e.isIntersecting)e.target.classList.add('visible');
      });
    },{threshold:0.15});
    obs.observe(el);
  });

  document.querySelectorAll('.nav-links a, .nav-logo').forEach(link=>{
    link.addEventListener('click',e=>{
      e.preventDefault();
      const target=document.querySelector(link.getAttribute('href'));
      if(target){
        document.body.classList.add('glitch-active');
        setTimeout(()=>{
          document.body.classList.remove('glitch-active');
          target.scrollIntoView({behavior:'smooth'});
        },200);
      }
    });
  });
})();
