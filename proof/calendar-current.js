(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4917837a82fe7e06.js","sha256":"4917837a82fe7e0668e1ce5f4f8ad4a7e1ccda57f2cb7ef8f34f0819274f20ea","count":2046,"publishedAt":"2026-11-05T23:43:20Z","state":"calendar-state.json","stateSha256":"1b2a0759cdb335389a55c43f9eca93f88e61d2a806a2afb49fd0d7ab7bc0c6bc","sourceState":"calendar-source-state.json","sourceStateSha256":"5e8ff7992ef4a89b752fe440ff856756e7f9ab7760f247a796a99c6e473ca4e1"});
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
