
const ADDRESS = "127.0.0.1"
const PORT = 8000
const BASEAPI = `http://${ADDRESS}:${PORT}`
 
function ge(id) {
    return document.getElementById(id)
}
// Every API call in messaging.js:
//      1. make a POST request
//      2. send JSON in the body
//      3. get JSON back
// instead of rewriting fetch block inside every function, 
// you write it once in send() and every function just calls it:
async function send(path, body) {
    const response = await fetch(`${BASEAPI}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    })
    const data = await response.json()
    console.log("response from", path, data)
    return data
}

// ========================================================
// GET SESSION 
// reads email + password from the URL (index.js puts them 
// there when it redirects: messaging.html?email=...&password=)
// ========================================================
function getSession() {
    const email = localStorage.getItem("email")
    const password = localStorage.getItem("password")
    console.log("session:", email)
    return {
        email: email,
        password: password
    }
}
const session = getSession()
ge("current-user-label").textContent = session.email

// ========================================================
// LOAD CONVO
// ========================================================
async function loadConversations(){
    // call POST 
    const data = await send("/conversations", {
        email: session.email,
        password: session.password
    })
    // get the convo list element from the DOM
    const convoList = ge("convo-list")
    convoList.innerHTML = ""  // clear before adding new items (avoids duplicates)
    // loop thru convos in response
    data.conversations.forEach(convo => {
        const li = document.createElement("li")
        li.classList.add("convo-item")
        if (convo.type === "direct") {
            li.textContent = convo.user // if direct, set label to other user's email
        }
        else {
            li.textContent = convo.name // if group, set label to group name
        }
        // store convo id on the element
        li.dataset.convoId = convo.conversation_id
        li.addEventListener("click", () => {
            document.querySelectorAll(".convo-item").forEach(i => i.classList.remove("active"))
            li.classList.add("active")
            openConversation(convo.conversation_id, li.textContent)
        })
        convoList.appendChild(li)
    })
}

// ========================================================
// OPEN CONVO
// ========================================================
async function openConversation(convoId, title){
    // update chat title with person's name/group name
    ge("chat-title").textContent = title
    // after this, hide the empty state ("no convo selected") and show chat view
    ge("no-convo-selected").classList.add("hidden")
    ge("chat-view").classList.remove("hidden")

    const data = await send(`/messages/receive/${convoId}`, {
        email: session.email,
        password: session.password
    })
    // now actually show the messages
    displayMessages(data.messages)
    // store convo id in send button --> sendMessage will know where to send messages
    ge("send-button").dataset.convoId = convoId
}

// ========================================================
// DISPLAY MESSAGES
// ========================================================
function displayMessages(msgs) {
    const feed = ge("messages-feed")
    
    //clear old msgs
    feed.innerHTML = ""

    //loop thru each msg
    msgs.forEach(msg => {
        //create div for each message
        const div = document.createElement("div")
        div.classList.add("message")
        // CSS uses .message.sent and .message.received to make 
        // sent messages go right and received go left
        if(msg.sender == session.email){
            div.classList.add("sent")
        } else {
            div.classList.add("received")
        }
        // text content
        div.textContent = msg.message
        //add to chat feed
        feed.appendChild(div)
    })
    // scroll to the bottom so latest message is visible
    feed.scrollTop = feed.scrollHeight
}

// ========================================================
// SEND MESSAGE
// ========================================================
async function sendMessage() {
    // get what the user typed
    const input = ge("message-input")
    const text = input.value.trim()

    // get the convo id stored on the send button
    const convoId = ge("send-button").dataset.convoId

    // if input is empty, dont send
    if (!text || !convoId) return

    // call POST /messages/send
    await send("/messages/send", {
        sender: session.email,
        password: session.password,
        conversation_id: parseInt(convoId),  // convert string to number
        message: text
    })
    //clear input box after sending msg
    input.value = ""

    //reload so new msg shows
    const title = ge("chat-title").textContent
    openConversation(convoId, title)

}

// ========================================================
// CREATE DIRECT
// ========================================================
async function createDirect() {
    const otherUser = ge("direct-email-input").value.trim()
    if (!otherUser) return

    const data = await send("/conversations/direct", {
        email: session.email,
        password: session.password,
        other_user: otherUser
    })

    console.log("create direct response:", data)

    if (data.conversation_id) {
        ge("direct-chat-input").classList.add("hidden")  // hide input
        ge("direct-email-input").value = ""              // clear input
        loadConversations()                              // refresh sidebar
    }
}

// ========================================================
// CREATE GROUP
// ========================================================
async function createGroup() {
    const name = ge("group-name-input").value.trim()
    const emailsRaw = ge("group-emails-input").value.trim()

    if (!name || !emailsRaw) return

    // split the textarea by new lines into an array
    const participants = emailsRaw.split("\n").map(e => e.trim()).filter(e => e)

    const data = await send("/conversations/group", {
        email: session.email,
        password: session.password,
        name: name,
        participants: participants
    })

    console.log("create group response:", data)

    if (data.conversation_id) {
        ge("group-chat-input").classList.add("hidden")  // hide input
        ge("group-name-input").value = ""               // clear inputs
        ge("group-emails-input").value = ""
        loadConversations()                             // refresh sidebar
    }
}

// ========================================================
// EVENT LISTENERS
// ========================================================
ge("send-button").addEventListener("click", sendMessage)
ge("refresh-button").addEventListener("click", () => {
    const convoId = ge("send-button").dataset.convoId
    const title = ge("chat-title").textContent
    if (convoId) openConversation(convoId, title)
})
// show input when + Direct Chat clicked
ge("new-direct-btn").addEventListener("click", () => {
    ge("direct-chat-input").classList.toggle("hidden")
})
ge("direct-submit-btn").addEventListener("click", createDirect)

ge("new-group-btn").addEventListener("click", () => {
    ge("group-chat-input").classList.toggle("hidden")
})
ge("group-submit-btn").addEventListener("click", createGroup)

ge("logout-btn").addEventListener("click", () => {
    localStorage.clear()
    window.location.href = "index.html"
})
ge("message-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage()
})

// load conversations when page opens
loadConversations()

//functions: funct, what it does, endpoint
//getSession(): reads email + password from URL (none)
//loadConversations(): fills sidebar with convos (POST /conversations)
//openConversation(id): loads messages when convo clicked (POST /messages/receive/{id})
//displayMessages(msgs): renders messages in the feed (none)

//- diff btwn openConvo and displayMsgs is openConversation talks to the server and hands off the data and
//displayMessages talks to the DOM and create a bubble and put it on screen
//- why split?? reusability,  refresh messages every few seconds, you just call openConversation(id) again 
//and displayMessages handles the rendering automatically -> no need rewrite the display logic