(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e095fc93ec904db9.js","sha256":"e095fc93ec904db973091bb3e4c50bba46ec2da9ee110b2b8fdee26fa49b5823","count":2454,"publishedAt":"2026-09-14T13:01:03Z","state":"calendar-state.json","stateSha256":"c0339693461ec35eb68263a0a87fd84b966d0513d19cbafdcd746ad53ab51c8c"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
