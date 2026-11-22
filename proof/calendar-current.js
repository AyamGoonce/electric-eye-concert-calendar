(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8900f8536ccfdbd7.js","sha256":"8900f8536ccfdbd7b9967adb8f2006cdd878bb53df60a8dbbae356b5d668f2f1","count":2103,"publishedAt":"2026-11-22T11:35:50Z","state":"calendar-state.json","stateSha256":"db7b954ad00867d292a2383a99d4e8bc459472aa42d79137a3ad1849ce7db10d","sourceState":"calendar-source-state.json","sourceStateSha256":"3eb297bac83e1ff97e2edc7219ea15d9e7beecb1ac3468e9953212528d049aad"});
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
