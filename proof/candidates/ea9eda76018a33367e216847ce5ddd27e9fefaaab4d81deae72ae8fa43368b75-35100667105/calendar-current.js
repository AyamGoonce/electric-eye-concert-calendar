(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ea9eda76018a3336.js","sha256":"ea9eda76018a33367e216847ce5ddd27e9fefaaab4d81deae72ae8fa43368b75","count":2500,"publishedAt":"2026-09-16T13:18:56Z","state":"calendar-state.json","stateSha256":"a66f198fc497c940d013373a07bc6988bd99c3c4aba4d0b04a83c1a1d6882ae1"});
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
