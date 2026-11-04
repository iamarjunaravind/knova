function openRegister() {
  const modal = document.getElementById("modal");
  if (modal) modal.style.display = "flex";
}

function closeRegister() {
  const modal = document.getElementById("modal");
  if (modal) modal.style.display = "none";
}

// Delegated to Mr.K Engine if available
if (typeof window.toggleChat !== 'function') {
  window.toggleChat = function(e) {
    if (e && e.preventDefault) e.preventDefault();
    const chatWindow = document.getElementById("chatWindow");
    const chatBadge = document.getElementById("chatBadge");
    if (chatWindow) {
      if (chatWindow.style.display === "none" || chatWindow.style.display === "") {
        chatWindow.style.display = "flex";
        if(chatBadge) chatBadge.style.display = "none";
      } else {
        chatWindow.style.display = "none";
      }
    }
  };
}

if (typeof window.sendMsg !== 'function') {
  window.sendMsg = function(question, answer) {
    const history = document.getElementById("chatHistory");
    if (!history) return;
    const userMsg = document.createElement("div");
    userMsg.style.cssText = "background:#1768ff; color:#fff; padding:10px 15px; border-radius:12px; align-self:flex-end; max-width:80%; font-size:14px; margin-top:10px;";
    userMsg.innerHTML = question;
    history.appendChild(userMsg);
    history.scrollTop = history.scrollHeight;
    setTimeout(() => {
      const botMsg = document.createElement("div");
      botMsg.style.cssText = "background:#fff; padding:10px 15px; border-radius:12px; border:1px solid #e2e8f0; align-self:flex-start; max-width:80%; font-size:14px; margin-top:10px;";
      botMsg.innerHTML = answer;
      history.appendChild(botMsg);
      history.scrollTop = history.scrollHeight;
    }, 600);
  };
}

if (typeof window.submitChatLead !== 'function') {
  window.submitChatLead = function() {
    const name = document.getElementById('chatName').value;
    const email = document.getElementById('chatEmail').value;
    
    if (!name || !email) {
      alert("Please enter both Name and Email.");
      return;
    }
    
    fetch('/chat/lead/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: name, email: email })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        document.getElementById('chatLeadForm').style.display = 'none';
        document.getElementById('chatInterface').style.display = 'flex';
      } else {
        alert("Error capturing details.");
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert("Error capturing details.");
    });
  };
}

document.addEventListener('DOMContentLoaded', () => {
    // Countdown Timer (10 days from now)
    const countdownDate = new Date().getTime() + (10 * 24 * 60 * 60 * 1000);
    
    function updateCountdown() {
        const now = new Date().getTime();
        const distance = countdownDate - now;

        if (distance < 0) {
            const countdownEl = document.getElementById("countdown");
            const countdownMobileEl = document.getElementById("countdown-mobile");
            if(countdownEl) countdownEl.style.display = "none";
            if(countdownMobileEl) countdownMobileEl.style.display = "none";
            return false;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        const elDays = document.querySelectorAll(".cd-days");
        const elHours = document.querySelectorAll(".cd-hours");
        const elMins = document.querySelectorAll(".cd-mins");
        const elSecs = document.querySelectorAll(".cd-secs");

        if(elDays.length) elDays.forEach(el => el.innerText = days.toString().padStart(2, '0'));
        if(elHours.length) elHours.forEach(el => el.innerText = hours.toString().padStart(2, '0'));
        if(elMins.length) elMins.forEach(el => el.innerText = minutes.toString().padStart(2, '0'));
        if(elSecs.length) elSecs.forEach(el => el.innerText = seconds.toString().padStart(2, '0'));
        
        return true;
    }

    if (updateCountdown()) {
        const countdownInterval = setInterval(function() {
            if (!updateCountdown()) {
                clearInterval(countdownInterval);
            }
        }, 1000);
    }

    // Reveal animations
    const io = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (e.isIntersecting) e.target.classList.add("show");
        }),
      { threshold: 0.12 },
    );
    document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(a=>{
      a.addEventListener('click',e=>{
        const id=a.getAttribute('href');
        if(id && id!=='#'){
          const el=document.querySelector(id);
          if(el){e.preventDefault();el.scrollIntoView({behavior:'smooth',block:'start'});}
        }
      });
    });

    // Registration and Newsletter forms now use Django's built-in form handling
    // or need to be wired to new Django endpoints.
});
