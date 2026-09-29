(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f2f98ab3e9fae60d.js","sha256":"f2f98ab3e9fae60dede767cd9425c2481de4d2ce0497e5e4d20163f708f8148c","count":2136,"publishedAt":"2026-09-29T13:48:57Z","state":"calendar-state.json","stateSha256":"4e1dad1b77167670dc066bdf313a1ae0c14aac3a210146555bf4e4cb2ba6c9ee","sourceState":"calendar-source-state.json","sourceStateSha256":"663f6f034c303bd47541b5c9b1edbb4bde373486863ccd74b14581ad9644e949"});
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
