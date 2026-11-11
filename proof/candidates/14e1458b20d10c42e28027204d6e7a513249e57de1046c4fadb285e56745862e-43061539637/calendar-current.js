(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.14e1458b20d10c42.js","sha256":"14e1458b20d10c42e28027204d6e7a513249e57de1046c4fadb285e56745862e","count":2175,"publishedAt":"2026-11-11T16:46:44Z","state":"calendar-state.json","stateSha256":"7755faa251ea2fd1b3d0fa9c7cb6c4da93fac82f62b2af09d8dcbb9928ec27fa","sourceState":"calendar-source-state.json","sourceStateSha256":"ee555025634066d7b5202f5958279a798a9dc6fcc0a9667285bda07a57042528"});
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
