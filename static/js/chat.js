function addMsg(sender, txt) {
    const log = document.getElementById('chatLog');
    log.innerHTML += `<div><b>${sender}:</b> ${txt}</div>`;
    log.scrollTop = log.scrollHeight;
}

async function sendChat() {
    const inp = document.getElementById('chatInput');
    const msg = inp.value.trim();
    if (!msg) return;
    addMsg("You", msg);
    inp.value = "";
    const page = window.location.pathname;
    const resp = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, page })
    });
    const data = await resp.json();
    addMsg("AI", data.reply);
}