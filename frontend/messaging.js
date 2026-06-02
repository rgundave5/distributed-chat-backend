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
    const token = localStorage.getItem("token")
    return { email, password, token }
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
    longPoll(convoId, lastId) 
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

// POLLING (5/22)
// we only hv one convo open at a time, polling for all or just one that's open? do polling for just convo open --> could do notifications later

let pollInterval = null;

function startPolling(convoId) {
    stopPolling(); // avoid stacked intervals
    // we need to know which convo is open, so pass convoId (modify openConvo later)

    // function setInterval(handler: TimerHandler, timeout?: number, ...arguments: any[]): number
    // aysnc arrow function: create anonymous functs and pass it in somewhere, it will be called when it needs to be
    // "single use" function (won't be used elsewhere) --> cleaner code
    pollInterval = setInterval(async () => {
        try {
            const lastId = conversationState[convoId].lastMessageId // we should update that once we get messages froms erver 5/27

            const data = await send(`/messages/receive/${convoId}`, {
                after_id: lastId  // only fetch messages after what we already have
            })

            if (data.messages.length > 0) {
                appendMessages(convoId, data.messages)
            }
        } catch (error) {
            // if send message messes up (invalid convo id for ex), if we dont handle error it could crash
            // prints error and error itself
            console.error("Polling error", error)
        }
        
    }, 1000) // 1 second timeout (in ms)
}

function stopPolling() {
    // !== is a strict equal, ex: strict equal of "5" === 5 --> false
    if (pollInterval !== null) {
        clearInterval(pollInterval); 
        pollInterval = null;
    } 
}
// if we logoit, pollinterval will get wiped, so we need to save it to be able to stopPolling

async function longPoll(convoId, lastId) {
    if (ge("send-button").dataset.convoId != convoId) return // stop if user switched convos!!!
    // 5/27, 
    lastId = conversationState[convoId].lastMessageId // lastid = local copy not real thing
    try {
        const response = await fetch(`${BASEAPI}/poll/${convoId}?last_id=${lastId}`, {
            method: "GET",
            headers: {"Authorization": `Bearer ${session.token}`}
        })
        const data = await response.json()
        if (data.messages && data.messages.length > 0) {
            displayMessages(data.messages)
            conversationState[convoId].lastMessageId = data.messages[data.messages.length - 1].id // udpates now
        } 
    } catch (e) {
        console.log("poll error:", e)
    }
    // immediately poll again
    longPoll(convoId, lastId)
    // update here too when we get data from server 5/27
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
    stopPolling() 
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

/* SENDING MESSAGE
user types message and hits send
    → sendMessage() runs
    → checks text and convoId exist
    → calls send("/messages/send", { conversation_id, message })
        → send() grabs token from localStorage
        → attaches it to Authorization header
        → POST request goes to server
            → server extracts token from header
            → verify_token() checks signature + expiry
            → extracts email from token (this is the sender)
            → save_message(convo_id, email, message_text) saves to DB
            → returns { message_id }
    → back in sendMessage(), input box is cleared
    → appendMessages() called with the new message
        → pushed to conversationState[convoId].messages
        → new div created and added to feed
        → lastMessageId updated
        → feed scrolls to bottom

RECEIVING MESSAGE
setInterval fires every 1 second
    → calls send("/messages/receive/{convoId}", { after_id: lastMessageId })
        → send() attaches token to header
        → POST request goes to server
            → server verifies token
            → calls get_message_by_convo_id(convoId, after_id)
                → queries DB for messages WHERE id > after_id
                → returns only new messages
    → back in polling loop:
        → if data.messages.length > 0:
            → appendMessages() adds them to screen
            → lastMessageId updates to newest message id
        → if empty: nothing happens, wait for next tick */


/* 5/22 homework
- fix time stamps (timezone could be different)
- look into web sockets (for now use long polling) - natural next step (complex)
- next session: proper error handling and UI changes
- short polling real world ex: job scheduler (Check data in near real time but no need for it toe openm for long)
- long polling ex: ebay live auction
- HW: proper error handling and UI changes (Start), make a list of the changes u wanna make in UI, look into long polling (python allows for this - fastAPI, js doesnt) --> where u stored HTTP endpoints (Client.py)
- find errors: clear db and try using it normally, stop server, restart it (for timestamp issue),play around
*/

/* 5/27
- make an actual alert pop up when an error happens
- could make chat more interactive, disable send button when loading convos (for ex)
- give upper bound for how long it polls like ten seconds in longpoll()
- we do long polling for 30 sec of convo id 1, its on server, sevrer is waiting for 30 sec, what of
user switches to convo id 2, (think ab this) --> client should save the data but dont display unless 
the user clicks the convo again
    do simialr check: if (ge("send-button").dataset.convoId != convoId) return // stop if user switched convos!!!
    store the last convo id in the state of the convo, and save the messages returned too --> work w appendMessages()
    using this code: newMessages.forEach(msg => {
        conversationState[convoId].messages.push(msg) // add each new msg from the newMessages array to the convo state's messages array
    })
    - get last msg id, store the 
    - try long polling for two convos at same time (do testing) - check if fastapi can handle it
- we gotta make sure we can check for the awaits

- add standardized error responses from server (refer to wiki page), specific message for client, but vague if server breaks
- right now, we just return 200 error + an error message (default smt went wrong) --> we need HTTP exception
- fastAPI has HTTP error module, returns specific error code + json body (Wtv u want - specific app error code + error msg)
- we assume the request body is corect info but what if its wrong --> we nee dto do validation (adding checks, empty msg? missing convo id? duplocate users? for ex)
- do validation for every endpoint 

- we need to amke sure client can HANDLE the errors (Ex: if convo id doesnt exist, then delete the convo) 
- pply to ogin, send/delete/receeve messages (handle the response)

- db stuff is wrapped in try catch --> have better messages of what went wrong
- create different function in messaging.js thats a certified error handler, pop up box of error message and goes away after 3 sec
timeout, if theres a new error messsage, it resets the 3 sec timer
*/