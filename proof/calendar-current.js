(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c65f4d0355f5ce16.js","sha256":"c65f4d0355f5ce16969490ea835ee94b1a46ae7615cc3fe26c8c9bb081c5eae1","count":2037,"publishedAt":"2026-11-03T11:51:44Z","state":"calendar-state.json","stateSha256":"a082e78e524a6bc11762c861dd1b73890bd95e1b09af165be08fa1109261cd84","sourceState":"calendar-source-state.json","sourceStateSha256":"94f977d2cb58f202fa4e6a75405637e7061978c20876f4c51e7cfe12947e325c"});
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
