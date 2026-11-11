(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.0e69f0bc1d7f4f84.js","sha256":"0e69f0bc1d7f4f845f8034b9a83a598a853bad53a5beb6984047c5b0604c4ef0","count":2189,"publishedAt":"2026-11-11T09:29:15Z","state":"calendar-state.json","stateSha256":"42d8ffb118685599afd58a36472e61524bcf5d0630fc581c8d7464c27e00d0ac","sourceState":"calendar-source-state.json","sourceStateSha256":"c5c5136b35e0b5e14c860de4848ce7550264838d7aae0d258c42ee5fe697cb21"});
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
