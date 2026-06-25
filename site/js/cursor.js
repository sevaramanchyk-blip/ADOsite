(function(){
  const outer=document.getElementById('cursor-outer');
  const inner=document.getElementById('cursor-inner');
  const canvas=document.getElementById('cursor-trail');
  const ctx=canvas.getContext('2d');
  let mx=0,my=0,ox=0,oy=0;
  const trail=[];
  const particles=[];
  const TRAIL_LEN=15;

  function resize(){canvas.width=window.innerWidth;canvas.height=window.innerHeight}
  window.addEventListener('resize',resize);
  resize();

  document.addEventListener('mousemove',e=>{
    mx=e.clientX;my=e.clientY;
    trail.push({x:mx,y:my});
    if(trail.length>TRAIL_LEN)trail.shift();
  });

  document.addEventListener('mousedown',e=>{
    spawnParticles(e.clientX,e.clientY,25);
  });

  document.querySelectorAll('a,button,.interactive,.song-item,.album-card,.tab-btn,.run-btn,.select-option,.select-selected').forEach(el=>{
    el.addEventListener('mouseenter',()=>document.body.classList.add('cursor-hover'));
    el.addEventListener('mouseleave',()=>document.body.classList.remove('cursor-hover'));
  });

  function spawnParticles(x,y,count){
    for(let i=0;i<count;i++){
      particles.push({
        x,y,
        vx:(Math.random()-.5)*10,
        vy:(Math.random()-.5)*10,
        life:1,
        color:['#2255ff','#00ccff','#ffffff','#4488ff','#6644cc'][Math.floor(Math.random()*5)],
        size:Math.random()*4+1
      });
    }
  }

  function animate(){
    ox+=(mx-ox)*.15;
    oy+=(my-oy)*.15;
    outer.style.left=ox+'px';
    outer.style.top=oy+'px';
    inner.style.left=mx+'px';
    inner.style.top=my+'px';

    ctx.clearRect(0,0,canvas.width,canvas.height);

    for(let i=0;i<trail.length;i++){
      const t=trail[i];
      const alpha=(i+1)/trail.length*.5;
      const size=(i+1)/trail.length*4;
      ctx.beginPath();
      ctx.arc(t.x,t.y,size,0,Math.PI*2);
      ctx.fillStyle=`rgba(34,85,255,${alpha})`;
      ctx.fill();
    }

    for(let i=particles.length-1;i>=0;i--){
      const p=particles[i];
      p.x+=p.vx;
      p.y+=p.vy;
      p.vy+=.15;
      p.vx*=.99;
      p.life-=.02;
      if(p.life<=0){particles.splice(i,1);continue}
      ctx.beginPath();
      ctx.arc(p.x,p.y,p.size*p.life,0,Math.PI*2);
      ctx.globalAlpha=p.life;
      ctx.fillStyle=p.color;
      ctx.fill();
    }
    ctx.globalAlpha=1;

    requestAnimationFrame(animate);
  }
  animate();
})();
