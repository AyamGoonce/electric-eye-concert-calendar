(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7039ae29026c0166.js","sha256":"7039ae29026c0166d68b312650411ca86a994dcc99589a319150673639414f4c","count":2155,"publishedAt":"2026-10-12T13:03:52Z","state":"calendar-state.json","stateSha256":"c4e71dd266fbc646f543dbbd089be4480aaf3fb61a672a56168d68ca2591015c","sourceState":"calendar-source-state.json","sourceStateSha256":"1a45e790e13ac76bb9609da9b1ca353e0f199f5ea2ed15ea8013d23e56301277"});
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
