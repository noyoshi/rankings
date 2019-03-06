function updateRankingList(data) {
  // Update everything in the recieved data
  var ids = [];
  data.forEach(function(item) {
    var rank = document.getElementById(item.rank.toString() + "-rank");
    var elo = document.getElementById(item.rank.toString() + "-elo");
    var name = document.getElementById(item.rank.toString() + "-name");

    rank.innerHTML = item.output;
    elo.innerHTML = item.elo;
    name.innerHTML = item.name;
  });
}

function submitBeerPongResult() {
  var things = ["p01", "p11", "p00", "p10", "s0", "s1"];
  var results = {};
  things.forEach(function(t) {
    var docThing = document.getElementById(t);
    results[t] = docThing.value;
  });
  var promise = $.ajax({
    type: "POST",
    url: "/beerUpdate",
    data: results,
    dataType: "json"
  });
  promise.then(function(data) {
    updateRankingList(data);
  });
}

function submitAndUpdate() {
  var things = ["p0", "p1", "s0", "s1"];
  var results = {};
  things.forEach(function(t) {
    var docThing = document.getElementById(t);
    results[t] = docThing.value;
  });
  var promise = $.ajax({
    type: "POST",
    url: "/update",
    data: results,
    dataType: "json"
  });
  promise.then(function(data) {
    updateRankingList(data);
  });
}

// particlesJS.load("particles-js", "assets/particles.json", function() {
//   console.log("callback - particles.js config loaded");
// });
