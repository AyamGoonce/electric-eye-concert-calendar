(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7b5caebeeeca98f7.js","sha256":"7b5caebeeeca98f76ba44e28449f525d8f81aed78f8452d72cb3d5842db70b9a","count":1824,"publishedAt":"2026-08-28T11:34:26Z","state":"calendar-state.json","stateSha256":"fa2df37d44784f354c882e290109d7d1e977f0b81a4396af8e95bacb62d33cb6"});
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
