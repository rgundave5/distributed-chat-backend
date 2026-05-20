// state manager
const conversationState = {}

const ADDRESS = "127.0.0.1"
const PORT = 8000
const BASEAPI = `http://${ADDRESS}:${PORT}`
 
function ge(id) {
    return document.getElementById(id)
}

// ========================================================
// SEND
// ========================================================
async function send(path, body) {
    const token = localStorage.getItem("token")
    const headers = { "Content-Type": "application/json" }
    if (token) {
        headers["Authorization"] = `Bearer ${token}`
    }
    const response = await fetch(`${BASEAPI}${path}`, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(body)
    })
    const data = await response.json()
    return data
}

// ========================================================
// INIT CONVO STATE
// ========================================================
function initConvoState(convoId) {
    // check if convo state already exists before creating one (avoid wiping existing data)
    if(!(convoId in conversationState)){
        conversationState[convoId] = {
            messages: [],
            lastMessageId: 0, // 0 because nothing is loaded yet
        }
    }
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
    const data = await send("/conversations", {})
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

// redundant! no need reloading ALL messages every time, fteching ALL messages when chat is long is hard
// and impractical
// 4/22: (do this) fix this, incremental fetching, track last message id that was sent there 
// every time new message added, check after a certain to only return the "new" messages, not the whole convo
// - real time updates, no need to refrech just automatically reloads messages
// - (do this) polling (async event, runs funct every sec): sends a query, code is repeatedly checking for new data, 
//       will poll when a chat is open, every new message is added to local list, pull every 1 second  
//          for new messages after a certain message id  (to know which emssages are already pulled, bc we only 
//          need the messages AFTER that)
//      ex: ordered pizza, call restaurant asking if pizza is ready (same concept)
// (not needed but for the future, good fix to make --> server tells u new message)
// pollling for all? web sockets, 
// (do this) add time stamps to each message
// (do this) more message data for groupchats, who sent it and when
// typing indicators??? makes more sense with web sockets 
// (do this) proper session handling, js web tokens, password, js web token will be stored, every request sent to server that token is attached and expires after some time, can be stored in request header, avoids leaking credentials
// error handling, alerts/ui feedback for if something goes wrong, change errors so error message is consister (same type of error message and error number for the same error)
// - separate files! in future
// HW: add message metadata to messages (in gc, who sent which message, timestamps), 
// username < message < timestamp
// js syntax (freecodecamp + the assignments given), 
// Learn! --> (for 5-6 more session), session 1: js web tokens (check alex's resources), session 2 & 3: polling
// and openConvo refactoring (intervals, async) (time consuming), session 4: error handling + ui changes,
// session 5: [tbd]
// ========================================================
// OPEN CONVO
// ========================================================
async function openConversation(convoId, title){
    // update chat title with person's name/group name
    ge("chat-title").textContent = title
    ge("no-convo-selected").classList.add("hidden")
    ge("chat-view").classList.remove("hidden")
    ge("send-button").dataset.convoId = convoId
    
    initConvoState(convoId)
    // fetch all messages only if we havent loaded this convo before
    if(conversationState[convoId].messages.length == 0){
        const data = await send(`/messages/receive/${convoId}`, {}) // ask server for all messages in this convo
        conversationState[convoId].messages = data.messages // take msgs the server sent back and store them in local state --> memory
        
        // ensure the code above worked and there actually are messages (avoid crashes)
        if(data.messages.length > 0) {
            conversationState[convoId].lastMessageId = data.messages.at(-1).id // get msg id of last message and store in state
            // to be able to "get msgs after this id"
        }
    }
    // display whats in state
    displayMessages(conversationState[convoId].messages)
}

// ========================================================
// DISPLAY MESSAGES
// ========================================================
function displayMessages(msgs) {
    const feed = ge("messages-feed")
    
    //clear old msgs (wipe the UI -> no nee dto do that)
    // instead, displayMessages will open msgs for first time and store in js dict, call append messages (youll get new msgs)
    feed.innerHTML = ""

    //loop thru each msg
    msgs.forEach(msg => {
        const div = document.createElement("div") // create new element in DOM for each message
        div.classList.add("message")
        if (msg.sender === session.email) {
            div.classList.add("sent")
        } else {
            div.classList.add("received")
        }

        // add sender name
        const sender = document.createElement("div")
        sender.classList.add("message-sender")
        sender.textContent = msg.sender 

        // add message text
        const text = document.createElement("div")
        text.classList.add("message-text")
        text.textContent = msg.message // put the actual message text inside the div

        // add timestamp
        const time = document.createElement("div")
        time.classList.add("message-time")
        time.textContent = new Date(msg.date).toLocaleTimeString()

        // attach the div to the chat feed so it shows on screen
        div.appendChild(sender)
        div.appendChild(text)
        div.appendChild(time)

        feed.appendChild(div)
    })
    // scroll to the bottom so latest message is visible
    feed.scrollTop = feed.scrollHeight
}

// ========================================================
// SEND MESSAGE
// ========================================================
async function sendMessage() {
    const input = ge("message-input")
    const text = input.value.trim()
    const convoId = ge("send-button").dataset.convoId 
    // need convo id, stored in send button using dataset, how to access convo id? 
    // thru the send button (BECAUSE we are using send button dataset to access it!)
    // not good practice tho: maybe convo id is stored in side bar, so when convo is clicked, covo id is stored in local storage

    // if input is empty dont send (check)
    if (!text || !convoId) {
        alert("No text given or conversation not found.")
        return
    }

    const data = await send("/messages/send/", {
        conversation_id: parseInt(convoId),
        message: text
    })

    input.value = ""
    // append the one message that was sent
    appendMessages(convoId, [{
        sender: session.email,
        message: text,
        id: data.message_id,
        date: new Date().toISOString()
    }])
    // no need to reload anymore
}

// ========================================================
// CREATE DIRECT
// ========================================================
async function createDirect() {
    const otherUser = ge("direct-email-input").value.trim()
    if (!otherUser) return

    const data = await send("/conversations/direct", {
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
// APPEND MESSAGES 
// ========================================================
// goal: add new messages (param is an array) to local state and display them without redrawing the whole chat
function appendMessages(convoId, newMessages) {
    newMessages.forEach(msg => {
        conversationState[convoId].messages.push(msg) // add each new msg from the newMessages array to the convo state's messages array
    })
    // add the new messages to the feed
    const feed = ge("messages-feed")
    newMessages.forEach(msg => {
        const div = document.createElement("div") // create new element in DOM for each message
        div.classList.add("message")
        if (msg.sender === session.email) {
            div.classList.add("sent")
        } else {
            div.classList.add("received")
        }

        // add sender name
        const sender = document.createElement("div")
        sender.classList.add("message-sender")
        sender.textContent = msg.sender 

        // add message text
        const text = document.createElement("div")
        text.classList.add("message-text")
        text.textContent = msg.message // put the actual message text inside the div

        // add timestamp
        const time = document.createElement("div")
        time.classList.add("message-time")
        time.textContent = new Date(msg.date).toLocaleTimeString()

        // attach the div to the chat feed so it shows on screen
        div.appendChild(sender)
        div.appendChild(text)
        div.appendChild(time)

        feed.appendChild(div)
    })
    if (newMessages.length > 0) {
        conversationState[convoId].lastMessageId = newMessages.at(-1).id
    }
    // scroll down so last message is visible
    feed.scrollTop = feed.scrollHeight
}  


// ========================================================
// EVENT LISTENERS
// ========================================================
ge("send-button").addEventListener("click", sendMessage)

ge("refresh-button").addEventListener("click", async() => {
    const convoId = ge("send-button").dataset.convoId
    if (!convoId) return

    const lastId = conversationState[convoId].lastMessageId

    const data = await send(`/messages/receive/${convoId}`, {
        after_id: lastId  // only fetch messages after what we already have
    })

    if (data.messages.length > 0) {
        appendMessages(convoId, data.messages)
    }
})

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


// 4/29/26 jwt
// header, payload, secret
// signature needs to be uniqur to the content
// without secret the reuslting signature wil be same for same content --> this is a problem
// if i had a bunch of tokens i could feed in likely haders and potenial payloads and match the hash, ill know what was used to make the signature
// secret salt: introduces randomness so that it cannot be recreated, standard to encrypt and decrypt tokens
// jwt encodes header, payload, signature, 
// signature is how sever can be expected to decrypt it
// in payload: encyprpt pword for ex, signature: how do we tell that this stuff is authentic (not fake payload)
// we encrypt it salt (private key) send it back to cleint
// when client sends it back to us, bc they encrypted it they know how to decrypt it 
// kinda like a pword
// server cretes it w associating info and send it back to client, client sends it back, sever decrypts 
// and uses info to confirm tht the perosn who sent reqauest was validated
// tokens are stateless, we dont hv to store it, or track on sever if its valid or invalid
// ex if someone chages pword u can invalidate token, old token must be invalid after changing pword
// store token in db or cache, see is this token there? then invalidate it 
// u must manually invalidate it, can give it a life span

// 5/19 long polling with setInterval
// 1. variable to track the interval so you can stop it: javascriptlet pollInterval = null
// 2. startPolling() and stopPolling() functions
// Start polling when a conversation is opened, stop when user logs out or switches away
//      in openConversation, at the very end: startPolling(convoId)
//       in logout event listener add stopPolling()
// always clearInterval at the start of startPolling    -> cant have two polls running at the same time
/* user opens convo
→ openConversation loads messages
→ startPolling begins
    → every 1 second: ask server for messages after lastMessageId
    → if new messages exist: appendMessages adds them to screen
    → lastMessageId updates automatically inside appendMessages
user switches convo
→ startPolling called again
→ clearInterval kills the old poll
→ new poll starts for new convo */