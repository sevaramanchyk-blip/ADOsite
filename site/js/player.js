(function(){
  document.querySelectorAll('.song-card').forEach(card=>{
    card.addEventListener('mouseenter',()=>document.body.classList.add('cursor-hover'));
    card.addEventListener('mouseleave',()=>document.body.classList.remove('cursor-hover'));
  });
})();
