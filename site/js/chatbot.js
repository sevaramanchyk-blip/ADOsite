(function(){
  const widget=document.getElementById('chatbot-widget');
  const toggleBtn=document.getElementById('chat-toggle');
  const closeBtn=document.getElementById('chat-close');
  const input=document.getElementById('chat-input');
  const sendBtn=document.getElementById('chat-send');
  const messages=document.getElementById('chat-messages');

  const QA=[
    {q:['ado','who','about','кто','об ado'],a:'Ado (アド) is a Japanese singer born October 24, 2002. One of Japan\'s most popular artists, known for her powerful voice and genre-blending style.'},
    {q:['usseewa','уссева'],a:'"Usseewa" (うっせぇわ) is Ado\'s debut single from 2020, reaching 300M+ views on YouTube. A rebellious anthem that launched her career.'},
    {q:['show','шоу'],a:'"Show" (ショウ) was released in 2022 for One Piece Film Red soundtrack. It became one of Ado\'s biggest hits.'},
    {q:['odo','odo'],a:'"Odo" (踊, meaning "dance") was released in 2021. A high-energy dance track showcasing Ado\'s versatile vocal range.'},
    {q:['readymade'],a:'"Readymade" (リディメイド) is a 2020 track with heavy electronic and rock influences, demonstrating Ado\'s genre-blending approach.'},
    {q:['gira','gira gira'],a:'"Gira Gira" (ギラギラ) from 2021 is a bold, provocative track with powerful vocals and edgy production.'},
    {q:['kyogen','album'],a:'"Kyogen" (狂言) is Ado\'s first studio album released in 2022. It features 12 tracks spanning multiple genres.'},
    {q:['zanmu'],a:'"Zanmu" (残夢) is Ado\'s second original album from 2023, continuing her evolution as an artist with 14 tracks.'},
    {q:['hibana','fire'],a:'"Hibana" (火花, meaning "spark") is Ado\'s 2024 album with 13 tracks, representing her latest musical evolution.'},
    {q:['concert','tour','live','концерт'],a:'Ado has performed at major venues and festivals. She performed the One Piece Film Red soundtrack live. Note: Ado never shows her face during performances.'},
    {q:['one piece','red'],a:'Ado performed 4 songs for One Piece Film Red (2022): "New Genesis", "Freedom", "Shoka", and "I\'m a Contie". The soundtrack was a massive success.'},
    {q:['face','mask','identity'],a:'Ado has never publicly shown her face. She uses voice filters and performs behind silhouettes/screens. This mystery is part of her artistic identity.'},
    {q:['genre','music','style','стиль','жанр'],a:'Ado\'s music spans J-Pop, rock, electronic, punk, and jazz. She\'s known for her incredible vocal range and ability to shift between styles.'},
    {q:['shop','merch','store','магазин'],a:'The official Ado merchandise shop is at ado-shop.com, selling albums (CDs, vinyl), t-shirts, accessories, and other merchandise.'},
    {q:['kura kura'],a:'"Kura Kura" (クラクラ) from 2021 is a psychedelic-influenced track with hypnotic melodies.'},
    {q:['aishite'],a:'"Aishite Aishite Aishite" (愛して愛して愛して, "Love Me Love Me Love Me") is a haunting 2021 track exploring themes of obsession.'},
    {q:['yoru','pierrot'],a:'"Yoru no Pierrot" (夜のピエロ, "Clown of the Night") is a theatrical 2021 track with dramatic vocal delivery.'},
    {q:['rockstar'],a:'"Rockstar" is from Ado\'s 2024 album Hibana. A high-energy rock-influenced track.'},
    {q:['tokyo','cannibal'],a:'"Tokyo Cannibalism" is a 2024 track from Hibana album, showcasing Ado\'s darker, more experimental side.'},
    {q:['hello','hi','привет','hey'],a:'Hey there! Welcome to the ADO fan page. Ask me anything about Ado\'s music, albums, or career!'},
    {q:['born','age','old','родилась'],a:'Ado was born on October 24, 2002, in Japan. She debuted in 2020 at age 17 with "Usseewa".'},
    {q:['help','помощь'],a:'I can tell you about: Ado\'s biography, her songs (Usseewa, Show, Odo, etc.), albums (Kyogen, Zanmu, Hibana), concerts, One Piece Film Red, and the merchandise shop!'}
  ];

  toggleBtn.addEventListener('click',()=>{
    widget.classList.remove('chatbot-closed');
    widget.classList.add('chatbot-open');
    input.focus();
  });

  closeBtn.addEventListener('click',()=>{
    widget.classList.remove('chatbot-open');
    widget.classList.add('chatbot-closed');
  });

  function sendMessage(){
    const text=input.value.trim();
    if(!text)return;

    addMessage(text,'user');
    input.value='';

    showTyping();

    setTimeout(()=>{
      removeTyping();
      const response=findAnswer(text);
      addMessage(response,'bot');
    },800+Math.random()*1200);
  }

  sendBtn.addEventListener('click',sendMessage);
  input.addEventListener('keydown',e=>{
    if(e.key==='Enter')sendMessage();
  });

  function addMessage(text,type){
    const msg=document.createElement('div');
    msg.className='chat-msg '+type;
    msg.innerHTML='<p>'+text+'</p>';
    messages.appendChild(msg);
    messages.scrollTop=messages.scrollHeight;
  }

  function showTyping(){
    const typing=document.createElement('div');
    typing.className='typing-indicator';
    typing.id='typing';
    typing.innerHTML='<span></span><span></span><span></span>';
    messages.appendChild(typing);
    messages.scrollTop=messages.scrollHeight;
  }

  function removeTyping(){
    const t=document.getElementById('typing');
    if(t)t.remove();
  }

  function findAnswer(input){
    const lower=input.toLowerCase();
    for(const item of QA){
      if(item.q.some(kw=>lower.includes(kw))){
        return item.a;
      }
    }
    return "Hmm, I'm not sure about that. Try asking about Ado's songs (Usseewa, Show, Odo), her albums (Kyogen, Zanmu, Hibana), concerts, or the One Piece Film Red soundtrack!";
  }
})();
