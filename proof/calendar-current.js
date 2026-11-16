(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3a851bc56cb5db43.js","sha256":"3a851bc56cb5db430b9dc9b7f5118efcd7475c5eaf1add87d1a007c3f657a3e6","count":2113,"publishedAt":"2026-11-16T16:24:42Z","state":"calendar-state.json","stateSha256":"a67c741884b9c0ec0335135fd13d310603c7c17fff8aa3c785941d1503efe534","sourceState":"calendar-source-state.json","sourceStateSha256":"1c84bb4a5495e0c58792c9ec0968441c2f39603ab46283d7c782e4f243d0c386"});
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
