
// implement the endpoints from client.py here
// ex: signup, direct convos, group convos
// event listener: html has things w event listening, like a button --> it listens, so when clicked it does an action
// ex: click signup button --> response

// app.js has signup and login only!
// 3 variable keywords: declare with var (not used much, used to indicate change in the variable),
// let (similar to var), const (constant, unchanged) 
// convention: name html and js files same

const ADDRESS = "127.0.0.1"
const PORT = 8000

// api requests, we want base to rep url
const BASEAPI = `http://${ADDRESS}:${PORT}`

// string templating (way how java can insert vars into string)
let hello = `${BASEAPI}` // use for addresses



// overview of js file:
// two main utility functions (login and signup) --> implement
// get access to dom elements from html file (with buttons, inputs, etc) 
//          -->(to get their values and check for event listeners)
// debug log function (can eitehr be put here or the built in one --> cmd option i)
// send function (POST method)--> takes url (path) and the body (JSON) 
            //--> returns result of whats sent (ex: status 200)
// function: save session (stays logged in when reloaded) --> for now save in local storage (not good practice)
//           better to use token auth (send ur creds to server and server validates it and creates token
//              cryptograpphic string thats tied to ur account/session, it sends token back to u, future requests
//              sent on that token, server gets that token and dehashes and verifies it w server)
//          common token: jwt, tokenauth, o auth (has cookies, ex: login cookie, which is verified)
// function: gets us to chat page, click on a button called chat --> takes us to chat page
// signup/logic button --> can be done from local storage
// 

// skeleton of html, try some of the js (just try, cuz its similar )

// name very short on purpose
// ----------------------------------------------------------------------------
// get elem by id (most direct way to get elem)
// ----------------------------------------------------------------------------
function ge(id){
    // common funct, 
    // DOM: doc object model (way to access the html page) --> look up!!
    // could also do get elem by class name, and others
    return document.getElementById(id)
}

// ----------------------------------------------------------------------------
// VERIFICATION: check inputs are not empty
// ----------------------------------------------------------------------------
function authentication(email, pword) {
    console.log("verifying inputs:", email, pword) // confirms  can access values
    if (!email || !pword) {
        ge("auth-error").textContent = "Please enter both email and password."
        return false
    }
    ge("auth-error").textContent = ""
    return true
}

// ----------------------------------------------------------------------------
// send funct: can be reused
// ----------------------------------------------------------------------------
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


// -----------------------------------------------------------------------------
// login
// -----------------------------------------------------------------------------
// async keyword: dont wait for this funct to finish, blocking and nonblocking execution, with async u can call funct and doenst wait for the result, u can do wtv u want, and get the value/result later
async function login(){
    const LOGIN_URL = `${BASEAPI}/login` // use tics not apostrophe
    let email = ge("auth-email").value
    let pword = ge("auth-password").value

    if (!authentication(email, pword)) return
    const data = await send("/login", { email: email, password: pword })

    if (data.message === "Logged in successfully") {
        ge("auth-screen").classList.add("hidden")
        ge("app-screen").classList.remove("hidden")
        // classList is the list of CSS classes on an element.
        //.add("hidden") hides the login page. 
        //.remove("hidden") reveals the app page.
    } else {
        ge("auth-error").textContent = "Invalid email or password."
    }
    // .value: html is hierarchial, mainelement.property/.method, dot syntax used a lot
    
    // base login func: two parts:
    //  email and pword, gte html elements (refer to them by id --> check index.html page 1)
    // doc get elem by id OR 
    // create a funct that takes in an id and calls doc.get on that id and returns that elem
    // self? not used here. not an object. no class
    // tie this funct to the button click, when buttons clicked this funct runs
}

// -----------------------------------------------------------------------------
// signup
// -----------------------------------------------------------------------------
async function signup() {
    let email = ge("auth-email").value
    let pword = ge("auth-password").value

    if (!authentication(email, pword)) return

    const data = await send("/signup", { email: email, password: pword })

    if (data.message === "Data stored successfully") {
        ge("auth-screen").classList.add("hidden")
        ge("app-screen").classList.remove("hidden")
    } else {
        ge("auth-error").textContent = "Signup failed. Email may already be taken."
    }
}

// EVENT LISTENERS 
ge("auth-login-btn").addEventListener("click", login)
ge("auth-signup-btn").addEventListener("click", signup)