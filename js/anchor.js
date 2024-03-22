///
///
/// SESSION MANAGEMENT
///
///

let sessionUUID = sessionStorage.getItem('sessionai_sessionUUID');
if (!sessionUUID) {
  sessionUUID = crypto.randomUUID();
  sessionStorage.setItem('sessionai_sessionUUID', sessionUUID);
}

const currentTime = Date.now()
const pageVisitToken = `${sessionUUID}-${currentTime}`;

///
///
/// SOCKETIO CLIENT
///
///

var socketioScript = document.createElement('script');
socketioScript.src = 'https://cdn.socket.io/4.7.5/socket.io.min.js';
socketioScript.crossOrigin = 'anonymous'
document.head.appendChild(socketioScript);

var socket;
socketioScript.onload = function() {
  socket = io('http://127.0.0.1:5000');
  //console.log('socket.io connected');
  socket.on('llmResponse', (data) => {
    displayAlert(data);
  });
}

function displayAlert(data) {
  alert(data);
}

///
///
/// MOUSE POSITION
///
///

var mousePos;

document.onmousemove = handleMouseMove;
setInterval(getMousePosition, 1000);

function handleMouseMove(event) {
    mousePos = {
        x: event.pageX,
        y: event.pageY
    };
}
  
function getMousePosition() {
    //console.log(mousePos);
    let ts = Date.now()
    
    var elementMouseIsOver = document.elementFromPoint(mousePos['x'], mousePos['y']);
    let textOrTagHovered;
    if (elementMouseIsOver.tagName.toLowerCase() === 'body' || elementMouseIsOver.innerText === "") {
        textOrTagHovered = `<${elementMouseIsOver.tagName.toLowerCase()}>`
    } else {
        textOrTagHovered = elementMouseIsOver.innerText
    }

    socket.emit('mouseUpdate', {
      session_id: sessionUUID, 
      pageVisitToken: pageVisitToken,
      mousePos: mousePos,
      recordedAt: ts, 
      hovered: textOrTagHovered,
    });
}

///
///
/// SESSION TRACKER
///
///

// Retrieve the page visit data from sessionStorage on page load
window.addEventListener('load', function() {
    const storedVisits = sessionStorage.getItem('sessionai_pageVisits');
    //console.log("sessionStorage visit log:", storedVisits)
    if (storedVisits) {
      pageVisits = JSON.parse(storedVisits);
    } else {
        pageVisits = [];
    }

    // Log the current page visit
    logPageVisit(window.location.pathname);
});

// Function to log the page visit
function logPageVisit(pagePath) {
  // 
  // Record the end of the previous page session if necessary
  //
  if (pageVisits[0] && pageVisits[0].endTime === null) {
    const timeSpent = currentTime - pageVisits[0].startTime; // Time spent in milliseconds
    pageVisits[0].endTime = currentTime;
    pageVisits[0].msElapsed = timeSpent;

    socket.emit('pageVisitEnd', {
      pageVisitToken: pageVisits[0].pageVisitToken,
      endTime: currentTime,
    })
    //console.log('Logged visit', pageVisits[0].path, timeSpent)
  }

  //
  // Record a new page session
  //
  newPageSession = {
    path: pagePath,
    pageVisitToken: pageVisitToken,
    startTime: currentTime,
    endTime: null,
    msElapsed: null,
  }
  pageVisits.unshift(newPageSession);
  //console.log('New pageview at', pagePath, currentTime)

  //
  // Store the page visit data in sessionStorage
  //
  sessionStorage.setItem('sessionai_pageVisits', JSON.stringify(pageVisits));

  //
  // Emit the page visit data to the backend
  //
  socket.emit('pageVisit', {
    session_id: sessionUUID,
    startTime: currentTime, 
    pageVisitToken: pageVisitToken,
    pagePath: pagePath
  });
}

///
///
/// SEND DATA TO BACKEND
///
///

