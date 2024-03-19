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
    return mousePos;
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
    const currentTime = Date.now();
    const timeSpent = currentTime - pageVisits[0].startTime; // Time spent in milliseconds
    pageVisits[0].endTime = currentTime;
    pageVisits[0].msElapsed = timeSpent;
    //console.log('Logged visit', pageVisits[0].path, timeSpent)
  }

  //
  // Record a new page session
  //
  const currentTime = Date.now();
  newPageSession = {
    path: pagePath,
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
}

///
///
/// SEND DATA TO BACKEND
///
///

