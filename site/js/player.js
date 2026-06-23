(function(){
  const items=document.querySelectorAll('.song-item');
  const player=document.getElementById('yt-player');
  const visualizer=document.querySelector('.visualizer');
  const bars=visualizer.querySelectorAll('.bar');

  let isPlaying=true;

  items.forEach(item=>{
    item.addEventListener('click',()=>{
      items.forEach(i=>i.classList.remove('active'));
      item.classList.add('active');
      const embedId=item.getAttribute('data-embed');
      player.src=`https://www.youtube.com/embed/${embedId}?rel=0&autoplay=1`;
      startVisualizer();
    });
  });

  function startVisualizer(){
    visualizer.classList.add('playing');
    bars.forEach(bar=>{
      const h=5+Math.random()*35;
      bar.style.setProperty('--h',h+'px');
    });
  }

  function randomizeBars(){
    if(visualizer.classList.contains('playing')){
      bars.forEach(bar=>{
        const h=5+Math.random()*35;
        bar.style.setProperty('--h',h+'px');
        bar.style.animationDuration=(.2+Math.random()*.5)+'s';
      });
    }
    setTimeout(randomizeBars,500);
  }
  randomizeBars();
})();
