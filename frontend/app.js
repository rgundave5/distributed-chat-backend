
// implement the endpoints from client.py here
// ex: signup, direct convos, group convos
// event listener: html has things w event listening, like a button --> it listens, so when clicked it does an action
// ex: click signup button --> response

// app.js has signup and login only!
// 3 variable keywords: declare with var (not used much, used to indicate change in the variable),
// let (similar to var), const (constant, unchanged) 

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