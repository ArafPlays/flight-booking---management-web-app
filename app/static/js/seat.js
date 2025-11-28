// get all buttons except the confirm seat (next) button with id confirmSeat
const allButtons = document.querySelectorAll("button:not(#confirmSeat)")

// Loop through all buttons and add a click listener
for (var i = 0; i < allButtons.length; i++) {
    // Add a click event to each button
    allButtons[i].addEventListener("click", function(event) {

    // Get the text inside the button that was clicked
    buttonText = event.target.innerText;

    // add a url query parameter for flask
    window.location.href = "/seat?chosenSeat="+buttonText;
  })
}